"""Pipeline orchestration engine for the metadata classification framework."""

import sys
import logging
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
            
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self.paths = path_coordinator
        self.global_config = self.paths.config
        self.parser_config = self.global_config.get("parser", self.global_config)
        
        # 📊 DIAGNOSTIC: Evaluate configuration state immediately after hydration
        self.logger.info("=== CONFIGURATION TAG EVALUATION ===")
        raw_tags = self.parser_config.get("entity_tagging") or []
        self.logger.info(f"1. Raw 'entity_tagging' from YAML: {raw_tags}")
        explicit_targets = [str(t).strip().lower() for t in raw_tags if t]
        self.logger.info(f"2. Sanitized target concepts to tag: {explicit_targets}")
        overrides = self.parser_config.get("overrides") or {}
        self.logger.info(f"3. Active structural overrides found: {list(overrides.keys())}")
        self.logger.info("=====================================")

        # Inject modular specialized sub-components safely via relative module references
        self.llm_classifier = LLMEntityClassifier(self.global_config, self.parser_config)
        self.post_processor = MetadataPostProcessor(self.paths, self.parser_config)

        # 🧠 DEPENDENCY CHECKPOINT: Validate background processing infrastructure availability
        self._verify_infrastructure_availability()

    def _verify_infrastructure_availability(self) -> None:
        """Verifies that the core inference model client infrastructure is reachable before execution."""
        if not hasattr(self.llm_classifier, "is_ready") or not self.llm_classifier.is_ready():
            self.logger.critical("❌ Background inference model (Ollama) is offline. Please start your local service engine instance and re-run this tool.")
            sys.exit(1)

    def set_working_config(self, working_dir: str, config_path: str) -> None:
        """Resets the internal environment boundaries with runtime parameters."""
        self.paths = self.paths.__class__(config_path=config_path, working_dir=working_dir)
        self.global_config = self.paths.config
        self.parser_config = self.global_config.get("parser", self.global_config)
        
        # Refresh configurations across downstream dependencies
        self.llm_classifier.update_config(self.global_config, self.parser_config)
        self.post_processor.update_config(self.paths, self.parser_config)
        
        # Re-verify infrastructure capabilities following environmental layout adjustments
        self._verify_infrastructure_availability()

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

        # 📊 GROUNDED INFERENCE: Synchronize schema and generate data profile
        grounding_profile = {}
        df_raw_sample = None
        raw_dataset_path = self.paths.raw_dataset_path
        if raw_dataset_path.exists():
            self.logger.info(f"📊 Generating grounding profile from sample of: {raw_dataset_path.name}")
            # Read a 500-row sample to generate cardinality and distribution metrics
            df_raw_sample = pd.read_csv(raw_dataset_path, sep=None, engine='python', nrows=500)
            
            # Task 4.1: Request the LLM client to generate the metadata bundle
            grounding_profile = self.llm_classifier.generate_grounding_profile(df_raw_sample)

            # 📊 HEADER SYNCHRONIZATION: Align dictionary attributes with authoritative raw headers
            df_dict = self.post_processor.synchronize_with_raw_headers(df_dict, df_raw_sample)

        # 🎯 ZERO-HARDCODING FIX: Extract the tag list strictly from your config space with empty list fallback
        raw_tags = self.parser_config.get("entity_tagging") or []
        explicit_targets = [str(t).strip().lower() for t in raw_tags if t]
        
        # Extract normalized, synchronized attributes and description values
        attr_series, desc_series = self.post_processor.infer_schema_columns(df_dict)
        
        # 🧠 PHASE 1 RUNTIME ENGAGEMENT: Bootstrap domain identification directly from data file arrays
        discovered_hints = self.llm_classifier.discover_macro_domain(
            attr_series.tolist(), desc_series.tolist()
        )

        # 🧠 PHASE 2 STREAMING EXECUTION: Pass dynamically extracted definitions down the pipe
        llm_assignments = self.llm_classifier.discover_entities(
            attr_series, desc_series, explicit_targets, 
            generated_hints=discovered_hints, grounding_profile=grounding_profile
        )
        
        # Component 3: Saves exact layout attributes without subsequent corruption
        parsed_matrix = self.post_processor.execute(
            df_dict, attr_series, desc_series, llm_assignments,
            grounding_profile=grounding_profile, df_raw_sample=df_raw_sample
        )
        return parsed_matrix
