"""Local LLM interaction abstraction for domain discovery classification."""

import json
import logging
import httpx
import pandas as pd
from typing import Dict, Any, List


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
            
            profile[str(col).lower()] = {
                "physical_type": str(series.dtype),
                "cardinality": int(series.nunique()),
                "null_ratio": round(float(series.isnull().mean()), 4),
                "samples": samples
            }
        self.logger.info(f"📊 Grounding profile generated for {len(profile)} columns.")
        return profile

    def discover_macro_domain(self, attributes: List[str], descriptions: List[str], explicit_targets: List[str]) -> Dict[str, Any]:
        """🧠 PHASE 1: Scans a sampling of the schema to establish global entity categories dynamically."""
        sample_size = min(15, len(attributes))
        sample_fields = [
            {"attr": str(a), "desc": str(d)} 
            for a, d in zip(attributes[:sample_size], descriptions[:sample_size])
        ]
        
        targets_str = ", ".join(explicit_targets) if explicit_targets else "None"

        macro_prompt = (
            f"You are a master data architect. Scan this snippet of a data dictionary blueprint:\n"
            f"{json.dumps(sample_fields)}\n\n"
            f"Identify the macroscopic business domain (e.g., Banking, Healthcare, Insurance).\n"
            f"Then, generate a list of 4 to 6 coarse-grained logical entity concepts "
            f"suited to house these attributes.\n\n"
            f"CRITICAL RULES:\n"
            f"1. DO NOT lump all attributes into a single catch-all category name.\n"
            f"2. Separate attributes by their intrinsic structural nature (e.g., distinguish between "
            f"Demographics, Risk Profiles, Financial metrics, and Spatial/Temporal metadata).\n"
            f"3. Make sure the entity concepts are granular enough to support target variations.\n"
            f"4. For these specific feature tags: [{targets_str}], identify common keywords or suffixes "
            f"present in the field names that characterize that tag for this specific dataset.\n\n"
            f"Return a strict JSON object with two keys:\n"
            f"- 'logical_entities': a list of strings.\n"
            f"- 'tag_keywords': a dictionary mapping each feature tag to a list of identified keywords.\n\n"
            f"Example:\n"
            f'{{"logical_entities": ["Demographics", "Financials"], "tag_keywords": {{"geographic": ["city", "zip", "state"]}}}}'
        )

        try:
            response = httpx.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": f"{self.system_prompt}\n\n{macro_prompt}",
                    "stream": False,
                    "options": {"temperature": 0.0},
                    "format": "json"
                },
                timeout=15.0
            )
            if response.status_code == 200:
                raw_json = response.json().get("response", "{}")
                data = json.loads(raw_json)
                self.logger.info(f"🎯 Dynamic Domain Discovery Successful!")
                return data
        except Exception as e:
            self.logger.warning(f"⚠️ Macro domain onboarding lookup bypassed: {e}")
            
        return {"logical_entities": ["unassigned"], "tag_keywords": {}}

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

        self.logger.info(f"🧠 Processing {len(attributes)} attributes atomically via Llama 3.2...")

        for attr, desc in zip(attributes, descriptions):
            attr_str = str(attr)
            # Fetch grounding data if available (case-insensitive)
            stats = grounding_profile.get(attr_str.lower(), {})
            stats_str = json.dumps(stats) if stats else "No physical data profile available."
            
            user_prompt = (
                f"Classify this single data schema field:\n"
                f"Field Name: {attr_str}\n"
                f"Description: {str(desc)}\n"
                f"Physical Data Profile (Grounding Context): {stats_str}\n\n"
                f"Instructions:\n"
                f"1. Select the best match for 'entity_assignment' from these discovered choices: [{hints_str}].\n"
                f"2. Evaluate dedicated boolean flags for these explicit semantic targets: {targets_str}.\n\n"
                f"Return a strict flat JSON object exactly like this example:\n"
                f'{{"entity_assignment": "YourChoice", "is_geographic": false}}'
            )

            try:
                response = httpx.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": f"{self.system_prompt}\n\n{user_prompt}",
                        "stream": False,
                        "options": {"temperature": 0.0},
                        "format": "json"
                    },
                    timeout=10.0
                )
                if response.status_code == 200:
                    raw_json = response.json().get("response", "{}")
                    assignments[attr_str] = json.loads(raw_json)
                    continue
            except Exception as e:
                self.logger.error(f"⚠️ Network error or bad payload during atomic parse of '{attr_str}': {e}")

            # 🧠 DOMAIN-AGNOSTIC EMPTY FALLBACK: Zero hardcoded strings or guesswork
            assignments[attr_str] = {"entity_assignment": "unassigned"}
            for target in explicit_targets:
                assignments[attr_str][f"is_{target}"] = False
                
        return assignments
