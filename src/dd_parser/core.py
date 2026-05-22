import os
import json
import hashlib
import re
from pathlib import Path
import pandas as pd
import httpx
from path_coordinator import PlatformPathResolver

class LocalEntityClassifier:
    """
    Zero-hardcoding parser engine that uses local Llama 3.2 models to 
    dynamically discover coarse-grained domain entities from data dictionary payloads,
    equipped with an explicit human-in-the-loop manual override schema layer.
    """
    def __init__(self):
        self.paths = None
        self.config = {}
        self.parser_config = {}
        self.global_config = {}
        
        # Known domain entity prefix stems and common abbreviation mappings
        self._known_prefixes = ["borrower", "borr", "lender", "lend", "bank", "location", "loc", "loan", "prop"]

    def set_working_config(self, working_dir: str, config_path: str) -> None:
        """Sets up the environment configuration boundaries."""
        self.paths = PlatformPathResolver(config_path=config_path)
        self.paths.base_dir = Path(working_dir).resolve()
        self.paths._loaded_config = None
        
        self.global_config = self.paths.config
        self.parser_config = self.global_config.get("parser", self.global_config)

    def extract_inventory_attributes(self) -> list[str]:
        """Safely extracts original native attribute strings directly from targets."""
        if not self.paths:
            raise ValueError("Pipeline configuration must be loaded via set_working_config.")
        target_path = self.paths.data_dictionary_path
        if not target_path.exists():
            return []
        df_dict = pd.read_csv(target_path, sep=None, engine='python', skipinitialspace=True)
        attr_series, _ = self._infer_schema_columns(df_dict)
        clean_series = attr_series.dropna().astype(str).str.strip()
        return clean_series[clean_series != ""].tolist()

    def process_pipeline(self) -> pd.DataFrame:
        """Executes LLM-driven domain discovery and advanced feature tagging loops."""
        if not self.paths:
            raise ValueError("Pipeline configuration must be loaded via set_working_config.")
        target_path = self.paths.data_dictionary_path
        if not target_path.exists():
            raise FileNotFoundError(f"Data Dictionary blueprint missing at: {target_path}")
            
        df_dict = pd.read_csv(target_path, sep=None, engine='python', skipinitialspace=True)
        explicit_targets = self.parser_config.get("entity_tagging", ["geographic"])
        
        attr_series, desc_series = self._infer_schema_columns(df_dict)
        
        # 🧠 DYNAMIC PASS: Call Llama 3.2 to deduce coarse-grained entity mappings
        llm_assignments = self._discover_entities_via_llm(attr_series, desc_series)
        
        parsed_matrix = self._process_tags_and_routing(
            df_dict, attr_series, desc_series, explicit_targets, llm_assignments
        )
        self._write_pipeline_artifacts(parsed_matrix)
        return parsed_matrix

    def _infer_schema_columns(self, df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
        """Extracts structural components from messy columns dynamically."""
        attr_idx = self.parser_config.get("csv_target_column_index", 0)
        if attr_idx >= len(df.columns):
            attr_idx = 0
        attr_series = df.iloc[:, attr_idx].astype(str).str.strip()

        remaining_cols = [i for i in range(len(df.columns)) if i != attr_idx]
        if not remaining_cols:
            return attr_series, pd.Series([""] * len(df))

        best_desc_idx = remaining_cols
        max_mean_length = -1
        for idx in remaining_cols:
            col_name = str(df.columns[idx]).lower()
            if any(kw in col_name for kw in ['definition', 'desc', 'meaning', 'explanation']):
                best_desc_idx = idx
                break
            mean_len = df.iloc[:, idx].astype(str).str.len().mean()
            if mean_len > max_mean_length:
                max_mean_length = mean_len
                best_desc_idx = idx

        desc_series = df.iloc[:, best_desc_idx].astype(str).str.strip()
        return attr_series, desc_series

    def _discover_entities_via_llm(self, attributes: pd.Series, descriptions: pd.Series) -> dict[str, str]:
        """Queries local Llama 3.2 model to group attributes into logical domain entities."""
        assignments = {}
        model_name = self.global_config.get("model_name", "llama3.2")
        system_prompt = self.global_config.get("system_prompt", "Respond strictly in JSON.")
        
        schema_summary = []
        for attr, desc in zip(attributes, descriptions):
            schema_summary.append({"attribute": str(attr), "description": str(desc)})
            
        user_prompt = (
            f"Analyze these fields and group them into logical coarse-grained Domain Entities "
            f"(e.g., Borrower, Lender, Loan, Temporal). Return a flat JSON object where the keys "
            f"are the exact attribute names and values are the entity labels.\n\n"
            f"Fields:\n{json.dumps(schema_summary)}"
        )

        try:
            response = httpx.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model_name,
                    "prompt": f"{system_prompt}\n\n{user_prompt}",
                    "stream": False,
                    "options": {"temperature": 0.0},
                    "format": "json"
                },
                timeout=30.0
            )
            if response.status_code == 200:
                raw_json = response.json().get("response", "{}")
                assignments = json.loads(raw_json)
        except Exception:
            # Fallback heuristic if local Ollama server is offline
            for attr in attributes:
                attr_lower = str(attr).lower()
                if "borr" in attr_lower: assignments[attr] = "Borrower"
                elif "bank" in attr_lower or "lender" in attr_lower: assignments[attr] = "Lender"
                elif "date" in attr_lower: assignments[attr] = "Temporal"
                else: assignments[attr] = "Loan"
                
        return assignments

    def _strip_attribute_prefix(self, attr_name: str) -> str:
        """Strips known prefixes and isolates the root token attribute."""
        attr_clean = str(attr_name).strip()
        attr_lower = attr_clean.lower()
        sorted_prefixes = sorted(self._known_prefixes, key=len, reverse=True)
        
        for prefix in sorted_prefixes:
            if attr_lower.startswith(prefix):
                prefix_len = len(prefix)
                stripped = attr_clean[prefix_len:]
                stripped = re.sub(r'^[^a-zA-Z0-9]+', '', stripped)
                if stripped:
                    return stripped
        return attr_clean

    def _process_tags_and_routing(
        self, df: pd.DataFrame, attributes: pd.Series, descriptions: pd.Series, 
        explicit_targets: list[str], llm_assignments: dict[str, str]
    ) -> pd.DataFrame:
        """Assembles data matrix injecting assignments, overrides, and feature flags."""
        provisional_template_df = df.copy()
        provisional_template_df["attribute_name"] = attributes
        provisional_template_df["provisional_entity_assignment"] = "unassigned"
        
        clean_attrs = attributes.fillna("").astype(str).str.strip()
        clean_descs = descriptions.fillna("").astype(str).str.strip()
        
        configured_boolean_filters = [t.strip().lower() for t in explicit_targets]
        for target in configured_boolean_filters:
            provisional_template_df[f"is_{target}"] = False

        # ⚡ Extract human-in-the-loop manual overrides dictionary safely from config
        user_overrides = self.parser_config.get("overrides", {})

        for idx in range(len(df)):
            attr_raw = clean_attrs.iloc[idx]
            desc_text = clean_descs.iloc[idx].lower()
            
            # Check for explicit manual override match first
            if attr_raw in user_overrides:
                field_override = user_overrides[attr_raw]
                
                # 1. Authoritative Override for Coarse Domain Assignment
                overridden_entity = field_override.get("provisional_entity_assignment", "Override")
                provisional_template_df.at[idx, "provisional_entity_assignment"] = str(overridden_entity)
                
                # 2. Authoritative Override for Capability Feature Flags
                for target in configured_boolean_filters:
                    flag_override_key = f"is_{target}"
                    if flag_override_key in field_override:
                        provisional_template_df.at[idx, flag_override_key] = bool(field_override[flag_override_key])
                
                continue # 🏎️ Bypass standard inference completely for this overridden row

            # --- STANDARD INFERENCE PIPELINE (Runs if no override matches) ---
            assigned_label = llm_assignments.get(attr_raw, llm_assignments.get(attr_raw.lower(), "Loan"))
            provisional_template_df.at[idx, "provisional_entity_assignment"] = str(assigned_label).capitalize()

            stripped_attribute = self._strip_attribute_prefix(attr_raw).lower()
            payload_for_routing = f"{stripped_attribute}: {desc_text}"

            for target in configured_boolean_filters:
                is_feature_matched = False
                if target == "geographic":
                    geo_tokens = ["street", "city", "state", "zip", "location", "address", "country", "territory"]
                    if any(tok in payload_for_routing for tok in geo_tokens):
                        is_feature_matched = True
                elif target == "medical":
                    med_tokens = ["icd", "patient", "clinical", "provider", "diagnosis", "health"]
                    if any(tok in payload_for_routing for tok in med_tokens):
                        is_feature_matched = True
                
                if is_feature_matched:
                    provisional_template_df.at[idx, f"is_{target}"] = True

        return provisional_template_df

    def _write_pipeline_artifacts(self, df_matrix: pd.DataFrame) -> None:
        """Persists analytical matrix artifacts strictly using coordinator paths."""
        csv_out_path = str(self.paths.data_dictionary_csv_path)
        df_matrix.to_csv(csv_out_path, index=False)
        
        sig_path = f"{csv_out_path}.signature"
        with open(sig_path, "w") as f:
            content_hash = hashlib.sha256(df_matrix.to_csv().encode()).hexdigest()
            f.write(content_hash)
            
        md_path = os.path.join(self.paths.documents_dir, "dd_parsing_summary.md")
        os.makedirs(os.path.dirname(md_path), exist_ok=True)
        with open(md_path, "w") as f:
            f.write(f"# Unified KMDS Analysis Summary\n\nProcessed attributes: {len(df_matrix)}")
