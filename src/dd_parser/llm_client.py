"""Local LLM interaction abstraction for domain discovery classification."""

import json
import logging
import httpx
import re
import pandas as pd
from typing import Dict, Any, List
from .rules import IntegrityEngine


class LLMEntityClassifier:
    """Manages Ollama API contexts and matches fallback heuristics semantically."""

    def __init__(self, global_config: Dict[str, Any], parser_config: Dict[str, Any]) -> None:
        """Hydrates runtime configurations for model routing queries."""
        self.logger = logging.getLogger(__name__)
        self.update_config(global_config, parser_config)

    def update_config(self, global_config: Dict[str, Any], parser_config: Dict[str, Any]) -> None:
        """Dynamically refreshes active structural settings fields."""
        self.global_config = global_config
        self.parser_config = parser_config if parser_config is not None else {}
        self.model_name = self.global_config.get("model_name", "llama3.2")
        self.system_prompt = self.global_config.get("system_prompt", "Respond strictly in JSON.")
        self.prompts = self.parser_config.get("prompts", {}).get("entity_classifier", {})

    def is_ready(self) -> bool:
        """🧠 INFRASTRUCTURE PROBE: Verifies local Ollama server status endpoint synchronously."""
        try:
            response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
            return response.status_code == 200
        except Exception:
            return False

    def generate_grounding_profile(self, df_sample: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Generates a physical metadata profile (cardinality, types, samples) to ground LLM inference."""
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

    def infer_dataset_type(self, attributes: List[str], descriptions: List[str]) -> str:
        """🧠 PHASE 1.5: Infers structural nature (Cross-sectional vs Panel) via temporal cues."""
        sample_size = min(30, len(attributes))
        sample_fields = [
            {"attr": str(a), "desc": str(d)} 
            for a, d in zip(attributes[:sample_size], descriptions[:sample_size])
        ]

        # Assembly Phase
        type_prompt = self._assemble_dataset_type_prompt(sample_fields)

        # Execution and Processing Phase
        try:
            response = self._call_llm(type_prompt)
            return self._process_dataset_type_result(response)
        except Exception as e:
            self.logger.warning(f"⚠️ Dataset type inference failed: {e}")
        
        return "cross-sectional"

    def _assemble_dataset_type_prompt(self, sample_fields: List[Dict[str, str]]) -> str:
        template = self.prompts.get("dataset_type_template")
        if template:
            return template.format(sample_fields=json.dumps(sample_fields))
        
        return (
            "Analyze this data dictionary snippet to determine the dataset's structural type.\n"
            f"Data: {json.dumps(sample_fields)}\n\n"
            "CRITERIA:\n"
            "1. 'panel': Schema contains repeating attribute sets for different time periods in one row.\n"
            "2. 'cross-sectional': Data represents a single snapshot.\n\n"
            "Return a strict JSON object: {'dataset_type': 'cross-sectional' | 'panel'}"
        )

    def _process_dataset_type_result(self, raw_json: str) -> str:
        data = json.loads(raw_json)
        inferred = data.get("dataset_type", "cross-sectional").lower()
        self.logger.info(f"📊 Structural Assessment: Inferred dataset as '{inferred}'")
        return inferred

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

    def discover_macro_domain(self, attributes: List[str], descriptions: List[str]) -> List[str]:
        """🧠 PHASE 1: Scans a sampling of the schema to establish global entity categories dynamically."""
        sample_size = min(15, len(attributes))
        sample_fields = [
            {"attr": str(a), "desc": str(d)} 
            for a, d in zip(attributes[:sample_size], descriptions[:sample_size])
        ]

        # Assembly Phase
        macro_prompt = self._assemble_macro_prompt(sample_fields)

        # Execution and Processing Phase
        try:
            response = self._call_llm(macro_prompt)
            return self._process_macro_result(response)
        except Exception as e:
            self.logger.warning(f"⚠️ Macro domain onboarding lookup bypassed: {e}")
            
        return ["unassigned"]

    def _assemble_macro_prompt(self, sample_fields: List[Dict[str, str]]) -> str:
        template = self.prompts.get("macro_domain_template")
        if template:
            return template.format(sample_fields=json.dumps(sample_fields))
        
        return (
            f"You are a master data architect. Scan this snippet of a data dictionary blueprint:\n"
            f"{json.dumps(sample_fields)}\n\n"
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
        grounding_profile: Dict[str, Any] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Queries local Llama 3.2 model atomically per attribute row to guarantee classification stability."""
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
            user_prompt = self._assemble_entity_prompt(attr_str, str(desc), stats_str, hints_str, targets_str)

            # Execution Phase
            try:
                response = self._call_llm(user_prompt, timeout=10.0)
                assignments[attr_str] = json.loads(response)
                continue
            except Exception as e:
                self.logger.error(f"⚠️ Network error or bad payload during atomic parse of '{attr_str}': {e}")

            # Fallback Phase
            assignments[attr_str] = {"entity_assignment": "unassigned"}
            for target in explicit_targets:
                assignments[attr_str][f"is_{target}"] = False
                
        return assignments

    def _assemble_entity_prompt(self, attr_str, desc_str, stats_str, hints_str, targets_str) -> str:
        template = self.prompts.get("entity_discovery_template")
        if template:
            return template.format(
                attr_str=attr_str,
                desc_str=desc_str,
                stats_str=stats_str,
                hints_str=hints_str,
                targets_str=targets_str
            )
        
        return (
            f"Classify this single data schema field:\n"
            f"Field Name: {attr_str}\n"
            f"Description: {desc_str}\n"
            f"Physical Data Profile: {stats_str}\n\n"
            f"Instructions:\n"
            f"1. Select 'entity_assignment' from [{hints_str}].\n"
            f"2. Evaluate flags: {targets_str}.\n\n"
            f"Return a strict flat JSON object."
        )
