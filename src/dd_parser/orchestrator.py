"""Pipeline orchestration engine for the metadata classification framework."""

import pandas as pd
from typing import List
from path_coordinator import PathCoordinator

from .llm_client import LLMEntityClassifier
from .post_processor import MetadataPostProcessor


class PipelineOrchestrator:
    """Entry point architecture that choreographs the domain discovery workflow."""

    def __init__(self, path_coordinator: PathCoordinator) -> None:
        """Injects dependencies and hydrates framework configuration boundaries."""
        if path_coordinator is None:
            raise TypeError("PipelineOrchestrator requires a valid PathCoordinator instance.")
            
        self.paths = path_coordinator
        self.global_config = self.paths.config
        self.parser_config = self.global_config.get("parser", self.global_config)
        
        # Inject modular specialized sub-components safely via relative module references
        self.llm_classifier = LLMEntityClassifier(self.global_config, self.parser_config)
        self.post_processor = MetadataPostProcessor(self.paths, self.parser_config)

        # Insert at the end of PipelineOrchestrator.__init__
        print("\n=== [DIAGNOSTIC] CONFIGURATION TAG EVALUATION ===")
        raw_tags = self.parser_config.get("entity_tagging") or []
        print(f"1. Raw 'entity_tagging' from YAML: {raw_tags} (Type: {type(raw_tags)})")
        explicit_targets = [str(t).strip().lower() for t in raw_tags if t]
        print(f"2. Sanitized target concepts to tag: {explicit_targets}")
        overrides = self.parser_config.get("overrides") or {}
        print(f"3. Active structural overrides found: {list(overrides.keys())}")
        print("=================================================\n")

    def set_working_config(self, working_dir: str, config_path: str) -> None:
        """Resets the internal environment boundaries with runtime parameters."""
        self.paths = self.paths.__class__(config_path=config_path, working_dir=working_dir)
        self.global_config = self.paths.config
        self.parser_config = self.global_config.get("parser", self.global_config)
        
        # Refresh configurations across downstream dependencies
        self.llm_classifier.update_config(self.global_config, self.parser_config)
        self.post_processor.update_config(self.paths, self.parser_config)

    def extract_inventory_attributes(self) -> List[str]:
        """Safely extracts native attribute strings from the configured source."""
        target_path = self.paths.data_dictionary_path
        if not target_path.exists():
            return []
            
        df_dict = pd.read_csv(target_path, sep=None, engine='python', skipinitialspace=True)
        attr_series, _ = self.post_processor.infer_schema_columns(df_dict)
        clean_series = attr_series.dropna().astype(str).str.strip()
        return clean_series[clean_series != ""].tolist()

    def process_pipeline(self) -> pd.DataFrame:
        """Executes LLM domain discovery and passes artifacts to post-processing."""
        target_path = self.paths.data_dictionary_path
        if not target_path.exists():
            raise FileNotFoundError(f"Data Dictionary blueprint missing at: {target_path}")
            
        df_dict = pd.read_csv(target_path, sep=None, engine='python', skipinitialspace=True)

        # Synchronize schema names BEFORE column series extraction
        raw_dataset_path = self.paths.raw_dataset_path
        if raw_dataset_path.exists():
            df_raw_schema = pd.read_csv(raw_dataset_path, sep=None, engine='python', nrows=0)
            raw_headers = list(df_raw_schema.columns)
            
            # Re-index data dictionary instantly so columns reflect raw file lowercase properties
            df_dict = self.post_processor.synchronize_with_raw_headers(df_dict, raw_headers)

        # 🎯 ZERO-HARDCODING FIX: Extract the tag list strictly from your config space with empty list fallback
        raw_tags = self.parser_config.get("entity_tagging") or []
        explicit_targets = [str(t).strip().lower() for t in raw_tags if t]

        # Extract normalized, synchronized attributes and description values
        attr_series, desc_series = self.post_processor.infer_schema_columns(df_dict)
        
        # Component 2: LLM processes the correct raw strings and dynamic target criteria
        llm_assignments = self.llm_classifier.discover_entities(attr_series, desc_series, explicit_targets)
        
        # Component 3: Saves exact layout attributes without subsequent corruption
        parsed_matrix = self.post_processor.execute(df_dict, attr_series, desc_series, llm_assignments)
        return parsed_matrix
