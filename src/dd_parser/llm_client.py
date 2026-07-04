"""Local LLM interaction abstraction for domain discovery classification."""

import json
import logging
import httpx
import re
import pandas as pd
from typing import Dict, Any, List
from .rules import IntegrityEngine


class LLMEntityClassifier:
    """
    Manages Ollama API contexts and matches fallback heuristics semantically.

    Attributes:
        model_name (str): The specific local model to invoke.
        system_prompt (str): Global behavior instructions for the LLM.
        prompts (dict): Collection of dynamic templates from configuration.
    """

    def __init__(self, global_config: Dict[str, Any], parser_config: Dict[str, Any]) -> None:
        """Initializes the client with configuration contexts."""
        self.logger = logging.getLogger(__name__)
        self.update_config(global_config, parser_config)

    def update_config(self, global_config: Dict[str, Any], parser_config: Dict[str, Any]) -> None:
        """
        Dynamically refreshes active structural settings fields.

        Args:
            global_config (dict): Shared project settings.
            parser_config (dict): Parser-specific settings.
        """
        self.global_config = global_config
        self.parser_config = parser_config if parser_config is not None else {}
        self.model_name = self.global_config.get("model_name", "llama3.2")
        self.system_prompt = self.global_config.get("system_prompt", "Respond strictly in JSON.")
        self.prompts = self.parser_config.get("prompts", {}).get("entity_classifier", {})

    def is_ready(self) -> bool:
        """
        Verifies local Ollama server status endpoint synchronously.

        Returns:
            bool: True if the model engine is reachable.
        """
        try:
            response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
            return response.status_code == 200
        except Exception:
            return False

    def generate_grounding_profile(self, df_sample: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Generates a physical metadata profile to ground LLM inference.

        Args:
            df_sample (pd.DataFrame): Representative sample of raw data.

        Returns:
            Dict[str, dict]: Metadata stats (types, cardinality, samples) per column.
        """
        profile = {}
        for col in df_sample.columns:
            series = df_sample[col]
            # Capture top 5 unique non-null values as strings for prompt context
            raw_samples = series.dropna().unique()[:5]
            samples = [str(s) for s in raw_samples]
            
            # Aggressive normalization to ensure keys match the post-processor's lookup map
            profile[IntegrityEngine.normalize(col)] = {
                "physical_type": str(series.dtype),
                "cardinality": int(series.nunique()),
                "null_ratio": round(float(series.isnull().mean()), 4),
                "samples": samples
            }
        self.logger.info(f"📊 Grounding profile generated for {len(profile)} columns.")
        return profile

    def _call_llm(self, prompt: str, timeout: float = 15.0) -> str:
        """Standardized HTTP caller for Ollama."""
        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={
                "model": self.model_name,
                "prompt": f"{self.system_prompt}\n\n{prompt}",
                "stream": False,
                "options": {"temperature": 0.0},
                "format": "json"
            },
            timeout=timeout
        )
        if response.status_code == 200:
            return response.json().get("response", "{}")
        raise RuntimeError(f"Ollama API error: {response.text}")

    def discover_macro_domain(self, attributes: List[str], descriptions: List[str], dataset_type: str = "cross-sectional") -> List[str]:
        """
        Scans the schema to establish global entity categories dynamically.

        Args:
            attributes (List[str]): Field names.
            descriptions (List[str]): Definitions.
            dataset_type (str): Dataset structural type.

        Returns:
            List[str]: Discovered entity concept names.
        """
        sample_size = min(15, len(attributes))
        sample_fields = [
            {"attr": str(a), "desc": str(d)} 
            for a, d in zip(attributes[:sample_size], descriptions[:sample_size])
        ]

        # Assembly Phase
        macro_prompt = self._assemble_macro_prompt(sample_fields, dataset_type)

        # Execution and Processing Phase
        try:
            response = self._call_llm(macro_prompt)
            return self._process_macro_result(response)
        except Exception as e:
            self.logger.warning(f"⚠️ Macro domain onboarding lookup bypassed: {e}")
            
        return ["unassigned"]

    def _assemble_macro_prompt(self, sample_fields: List[Dict[str, str]], dataset_type: str) -> str:
        """
        Constructs the macro domain discovery prompt.

        Args:
            sample_fields (List[dict]): Sample of the schema.
            dataset_type (str): Dataset structural type.

        Returns:
            str: Formatted prompt.
        """
        template = self.prompts.get("macro_domain_template")
        if template:
            return template.format(sample_fields=json.dumps(sample_fields), dataset_type=dataset_type)
        
        return (
            f"You are a master data architect. Scan this snippet of a data dictionary blueprint:\n"
            f"{json.dumps(sample_fields)}\n\n"
            f"This dataset is a '{dataset_type}' dataset.\n"
            f"Identify the macroscopic business domain (e.g., Banking, Healthcare, Insurance).\n"
            f"Then, generate a list of 4 to 6 coarse-grained logical entity concepts.\n"
            f"Return a strict JSON object: {{'logical_entities': ['A', 'B']}}"
        )

    def _process_macro_result(self, raw_json: str) -> List[str]:
        data = json.loads(raw_json)
        discovered = data.get("logical_entities", [])
        if discovered:
            self.logger.info(f"🎯 Dynamic Domain Discovery Successful! Extracted Core Concepts: {discovered}")
            return [str(item) for item in discovered]
        return ["unassigned"]

    def discover_entities(
        self, 
        attributes: pd.Series, 
        descriptions: pd.Series, 
        explicit_targets: List[str], 
        generated_hints: List[str] = None,
        grounding_profile: Dict[str, Any] = None,
        dataset_type: str = "cross-sectional"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Queries local model atomically per attribute to guarantee classification stability.

        Args:
            attributes (pd.Series): Column names.
            descriptions (pd.Series): Definitions.
            explicit_targets (List[str]): Semantic tags to evaluate.
            generated_hints (List[str], optional): Discovery context from Phase 1.
            grounding_profile (dict, optional): Physical data stats.

        Returns:
            Dict[str, Dict[str, Any]]: Mapping of attribute to entity assignment and tags.
        """
        assignments = {}
        active_hints = generated_hints if generated_hints else []
        hints_str = ", ".join(str(h) for h in active_hints) if active_hints else "Logical Categories"
        targets_str = ", ".join([f"'is_{t}' (boolean)" for t in explicit_targets])
        grounding_profile = grounding_profile or {}

        self.logger.info(f"🧠 Processing {len(attributes)} attributes atomically via {self.model_name}...")

        for attr, desc in zip(attributes, descriptions):
            attr_str = str(attr)
            # Aggressive normalization via the shared IntegrityEngine
            attr_norm = IntegrityEngine.normalize(attr_str)
            stats = grounding_profile.get(attr_norm, {})
            stats_str = json.dumps(stats) if stats else "No physical data profile available."
            
            # Assembly Phase
            user_prompt = self._assemble_entity_prompt(attr_str, str(desc), stats_str, hints_str, targets_str, dataset_type)

            # Execution Phase
            try:
                response = self._call_llm(user_prompt, timeout=10.0)
                parsed = json.loads(response)
                assignments[attr_str] = self._normalize_entity_response(parsed, explicit_targets)
                continue
            except Exception as e:
                self.logger.error(f"⚠️ Network error or bad payload during atomic parse of '{attr_str}': {e}")

            # Fallback Phase
            assignments[attr_str] = {"entity_assignment": "unassigned"}
            for target in explicit_targets:
                assignments[attr_str][f"is_{target}"] = False
                
        return assignments

    def _normalize_entity_response(self, parsed: Dict[str, Any], explicit_targets: List[str]) -> Dict[str, Any]:
        """
        Normalize the LLM response into the expected entity assignment contract.

        Args:
            parsed (Dict[str, Any]): Raw parsed JSON from the LLM.
            explicit_targets (List[str]): Semantic flag names.

        Returns:
            Dict[str, Any]: Normalized entity assignment payload.
        """
        normalized = {"entity_assignment": "unassigned"}

        if isinstance(parsed, dict):
            if "entity_assignment" in parsed:
                normalized["entity_assignment"] = parsed["entity_assignment"]
            elif "classification" in parsed:
                normalized["entity_assignment"] = parsed["classification"]
            elif parsed.get("flags") and "entity_assignment" in parsed["flags"]:
                normalized["entity_assignment"] = parsed["flags"]["entity_assignment"]

            if "static_dynamic" in parsed:
                normalized["static_dynamic"] = str(parsed["static_dynamic"]).lower()
            elif parsed.get("flags") and "static_dynamic" in parsed["flags"]:
                normalized["static_dynamic"] = str(parsed["flags"]["static_dynamic"]).lower()

            # Preserve explicit boolean targets if present
            for target in explicit_targets:
                key = f"is_{target}"
                if key in parsed:
                    normalized[key] = bool(parsed[key])
                elif parsed.get("flags") and key in parsed["flags"]:
                    normalized[key] = bool(parsed["flags"][key])
                else:
                    normalized[key] = False

        else:
            for target in explicit_targets:
                normalized[f"is_{target}"] = False

        return normalized

    def _assemble_entity_prompt(self, attr_str, desc_str, stats_str, hints_str, targets_str, dataset_type: str) -> str:
        """
        Constructs the atomic entity classification prompt.

        Args:
            attr_str (str): Field name.
            desc_str (str): Definition.
            stats_str (str): Grounding stats JSON.
            hints_str (str): Available entity choices.
            targets_str (str): Semantic tags requested.

        Returns:
            str: Formatted prompt.
        """
        template = self.prompts.get("entity_discovery_template")
        if template:
            return template.format(
                attr_str=attr_str,
                desc_str=desc_str,
                stats_str=stats_str,
                hints_str=hints_str,
                targets_str=targets_str,
                dataset_type=dataset_type
            )
        
        return (
            f"Classify this single data schema field:\n"
            f"Field Name: {attr_str}\n"
            f"Description: {desc_str}\n"
            f"Physical Data Profile: {stats_str}\n\n"
            f"Instructions:\n"
            f"1. Select 'entity_assignment' from [{hints_str}].\n"
            f"2. Evaluate flags: {targets_str}.\n"
            f"3. The dataset type is {dataset_type}. For panel/longitudinal data, indicate whether this field is 'static' or 'dynamic' based on whether it changes over time for the same subject.\n\n"
            f"Return a strict flat JSON object exactly like this example:\n"
            f"{{\"entity_assignment\": \"YourChoice\", \"static_dynamic\": \"dynamic\", \"is_geographic\": false}}"
        )
