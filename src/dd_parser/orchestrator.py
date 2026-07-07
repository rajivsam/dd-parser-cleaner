"""Pipeline orchestration engine for the metadata classification framework."""

import sys
import json
import logging
import pandas as pd
from importlib.resources import files as resource_files
from pathlib import Path
from typing import List
from rich.console import Console
from rich.prompt import Confirm
from dd_common.path_coordinator import PathCoordinator

from .llm_client import LLMEntityClassifier
from .post_processor import MetadataPostProcessor
from .rules import IntegrityEngine


class PipelineOrchestrator:
    """
    Entry point architecture that choreographs the domain discovery workflow.

    Attributes:
        paths (PathCoordinator): Authorized routing contract for project resources.
        global_config (dict): Root configuration settings.
        parser_config (dict): Isolated parser-specific settings.
        llm_classifier (LLMEntityClassifier): Client for semantic categorization.
        post_processor (MetadataPostProcessor): Logic for matrix assembly and export.
        console (Console): Rich terminal interface for user feedback.
    """

    def __init__(self, path_coordinator: PathCoordinator) -> None:
        """
        Injects dependencies and hydrates framework configuration boundaries.

        Args:
            path_coordinator (PathCoordinator): Initialized resource manager.
        """
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
        self.console = Console()

        # 🧠 DEPENDENCY CHECKPOINT: Validate background processing infrastructure availability
        self._verify_infrastructure_availability()

    def _verify_infrastructure_availability(self) -> None:
        """
        Verifies that the core inference model client infrastructure is reachable.
        
        Checks the connectivity to the local Ollama instance. If unreachable, 
        terminates execution to prevent pipeline failure.
        """
        if not hasattr(self.llm_classifier, "is_ready") or not self.llm_classifier.is_ready():
            self.logger.critical("❌ Background inference model (Ollama) is offline. Please start your local service engine instance and re-run this tool.")
            sys.exit(1)

    def _load_questionnaire_schema(self) -> dict:
        schema_path = self.global_config.get("questionnaire_schema_path")
        if not schema_path:
            return {}

        candidates = []
        schema_file = Path(schema_path)
        if schema_file.is_absolute():
            candidates.append(schema_file)
        else:
            candidates.append(self.paths.working_dir / schema_path)
            config_path = Path(self.paths._config_name)
            if not config_path.is_absolute():
                config_path = (self.paths.working_dir / self.paths._config_name).resolve()
            candidates.append(config_path.parent / schema_path)

        for candidate in candidates:
            if candidate.exists():
                with open(candidate, "r", encoding="utf-8") as f:
                    return json.load(f)

        # Fallback to a packaged questionnaire schema shipped with the installed distribution.
        try:
            package_schema = resource_files("dd_common").joinpath("schemas").joinpath(Path(schema_path).name)
            if package_schema.is_file():
                with package_schema.open("r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass

        raise FileNotFoundError(f"Questionnaire schema not found at any of: {candidates}")

    def _collect_questionnaire_answers(self) -> dict:
        if not self.global_config.get("enable_dataset_questionnaire"):
            return {}
        if not self.global_config.get("interactive_mode"):
            return {}
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            self.logger.warning("⚠️ Non-interactive environment detected; skipping questionnaire collection.")
            return {}

        schema = self._load_questionnaire_schema()
        questions = schema.get("questions") or []
        if not questions:
            self.logger.warning("⚠️ Questionnaire schema contains no questions; skipping questionnaire collection.")
            return {}

        answers = {}
        for question in questions:
            qid = question.get("id")
            prompt = question.get("prompt")
            if not qid or not prompt:
                raise ValueError("Questionnaire schema entries must include both 'id' and 'prompt'.")
            answer = self.console.input(f"{prompt} ").strip()
            answers[qid] = answer

        if self.global_config.get("handshake_require_questions") and any(not v for v in answers.values()):
            raise ValueError("Questionnaire requires answers for all configured questions.")

        return answers

    def process_pipeline(self) -> pd.DataFrame:
        """
        Executes LLM domain discovery and passes artifacts to post-processing.

        Returns:
            pd.DataFrame: The final synchronized metadata matrix.

        Raises:
            FileNotFoundError: If the Data Dictionary source file is missing.
        """
        target_path = Path(self.paths.data_dictionary_path)
        if not target_path.exists():
            raise FileNotFoundError(f"Data Dictionary blueprint missing at: {target_path}")
            
        try:
            df_dict = pd.read_csv(target_path, engine='c', low_memory=False)
        except Exception:
            df_dict = pd.read_csv(target_path, sep=None, engine='python', skipinitialspace=True)


        # 📊 GROUNDED INFERENCE: Synchronize schema and generate data profile
        grounding_profile = {}
        df_raw_sample = None
        bridge = None
        raw_dataset_path = Path(self.paths.raw_dataset_path)
        if raw_dataset_path.exists():
            cleaner_cfg = self.global_config.get("cleaner", {})
            filters = cleaner_cfg.get("column_filters", {})
            manual_drops = filters.get("drop_attributes", [])
            ignored = filters.get("ignore_recommendations", [])
            all_exclusions = list(set(manual_drops) | set(ignored))

            self.logger.info(f"📊 Generating grounding profile from sample of: {raw_dataset_path.name}")
            # Read a 500-row sample and immediately filter out manual drops
            try:
                df_raw_sample = pd.read_csv(raw_dataset_path, engine='c', nrows=500)
                self.logger.info(f"Loaded sample from {raw_dataset_path.name} using C engine.")
            except Exception:
                self.logger.warning("C engine failed for sample. Falling back to Python engine for sniffing...")
                df_raw_sample = pd.read_csv(raw_dataset_path, sep=None, engine='python', nrows=500)

            df_raw_sample = self._execute_filtering(df_raw_sample, manual_drops)
            
            # Task 4.1: Request the LLM client to generate the metadata bundle
            grounding_profile = self.llm_classifier.generate_grounding_profile(df_raw_sample)

            # 🛡️ INTEGRITY EVALUATION: Reconcile Dictionary vs Raw BEFORE synchronization
            # This ensures that 'Orphans' are captured before they are filtered out of the operational pool.
            attr_series, _ = self.post_processor.infer_schema_columns(df_dict)
            bridge = IntegrityEngine.evaluate_bridge(attr_series.tolist(), list(df_raw_sample.columns))
            self.logger.info(f"🌉 Bridge Evaluation: {len(bridge['operational'])} Operational, {len(bridge['orphans'])} Orphans, {len(bridge['ghosts'])} Ghosts")
            
            if bridge['orphans']:
                self.logger.warning(f"⚠️  Orphans Detected (Dictionary entries with no data match): {bridge['orphans'][:5]}...")
            if bridge['ghosts']:
                self.logger.info(f"👻 Ghosts Detected (Raw headers without dictionary entry): {bridge['ghosts'][:5]}...")

            # 📊 HEADER SYNCHRONIZATION: Align dictionary attributes with authoritative raw headers
            df_dict = self.post_processor.synchronize_with_raw_headers(df_dict, df_raw_sample)
            
            # Synchronize the dictionary to exclude manual drops before LLM classification
            if manual_drops:
                attr_series, _ = self.post_processor.infer_schema_columns(df_dict)
                attr_col_name = attr_series.name if attr_series.name in df_dict.columns else df_dict.columns[0]
                df_dict = df_dict[~df_dict[attr_col_name].isin(manual_drops)].reset_index(drop=True)

        # 🧠 PHASE 1.5: Dataset Type Selection (explicitly configured in config.yaml)
        dataset_type = self.global_config.get("dataset_type")
        if not isinstance(dataset_type, str):
            dataset_type = self.global_config.get("cleaner", {}).get("structural_assessment", {}).get("dataset_type")

        if not isinstance(dataset_type, str):
            self.logger.warning(
                "⚠️ Missing dataset_type in config.yaml. Defaulting to 'cross-sectional'."
            )
            dataset_type = "cross-sectional"
        else:
            dataset_type_lower = dataset_type.strip().lower()
            if "panel" in dataset_type_lower:
                dataset_type = "panel"
            elif "event_log" in dataset_type_lower or "event log" in dataset_type_lower:
                dataset_type = "event_log"
            elif "longitudinal" in dataset_type_lower:
                dataset_type = "longitudinal"
            else:
                dataset_type = "cross-sectional"

        if dataset_type in {"panel", "longitudinal"}:
            self.logger.info(
                "🧠 Dataset type indicates longitudinal/panel data. "
                "Cleaning actions should be handled by the featurization pipeline, "
                "continuing with metadata and dictionary processing."
            )

        # 🎯 ZERO-HARDCODING FIX: Extract the tag list strictly from your config space with empty list fallback
        raw_tags = self.parser_config.get("entity_tagging") or []
        explicit_targets = [str(t).strip().lower() for t in raw_tags if t]
        
        # Extract normalized, synchronized attributes and description values
        attr_series, desc_series = self.post_processor.infer_schema_columns(df_dict)

        seed_attr_series, seed_desc_series = self._select_wide_short_seed_attributes(attr_series, desc_series)
        
        # 🧠 PHASE 1 RUNTIME ENGAGEMENT: Bootstrap domain identification directly from the seed schema fields
        discovered_hints = self.llm_classifier.discover_macro_domain(
            seed_attr_series.tolist(), seed_desc_series.tolist(), dataset_type=dataset_type
        )

        # 🧠 PHASE 2 STREAMING EXECUTION: Pass dynamically extracted definitions down the pipe
        llm_assignments = self.llm_classifier.discover_entities(
            seed_attr_series, seed_desc_series, explicit_targets, 
            generated_hints=discovered_hints, grounding_profile=grounding_profile,
            dataset_type=dataset_type
        )

        # Component 3: Saves exact layout attributes without subsequent corruption
        questionnaire_answers = self._collect_questionnaire_answers()
        parsed_matrix = self.post_processor.execute(
            df_dict, attr_series, desc_series, llm_assignments,
            grounding_profile=grounding_profile, df_raw_sample=df_raw_sample,
            dataset_type=dataset_type,
            bridge_report=bridge,
            use_case_answers=questionnaire_answers
        )
        return parsed_matrix

    def _select_wide_short_seed_attributes(self, attr_series: pd.Series, desc_series: pd.Series) -> tuple[ pd.Series, pd.Series ]:
        """
        Selects a minimal seed set of schema fields for wide-short homogeneous datasets.

        The seed set contains the first schema field and the configured wide-short
        representative column. This avoids querying every repeated attribute.
        """
        if not self.parser_config.get("wide_short_homogeneous"):
            return attr_series, desc_series

        rep_column = self.parser_config.get("wide_short_representative_column")
        if not rep_column or rep_column not in attr_series.tolist():
            return attr_series, desc_series

        seed_attrs = [attr_series.iloc[0]]
        seed_descs = [desc_series.iloc[0]]

        if rep_column != seed_attrs[0]:
            rep_index = attr_series[attr_series == rep_column].index
            if len(rep_index) > 0:
                idx = rep_index[0]
                seed_attrs.append(attr_series.iloc[idx])
                seed_descs.append(desc_series.iloc[idx])
            else:
                return attr_series, desc_series

        return pd.Series(seed_attrs, dtype=attr_series.dtype), pd.Series(seed_descs, dtype=desc_series.dtype)

    def _execute_filtering(self, df: pd.DataFrame, drop_cols: List[str]) -> pd.DataFrame:
        """
        Physically removes attributes specified in the configuration.

        Args:
            df (pd.DataFrame): Data sample to filter.
            drop_cols (List[str]): Column names to exclude.

        Returns:
            pd.DataFrame: Filtered sample.
        """
        if not drop_cols:
            return df
        existing_drops = [c for c in drop_cols if c in df.columns]
        if existing_drops:
            df = df.drop(columns=existing_drops)
        return df
