"""Idempotent cleaning pipeline runner for structured data transformation."""

import importlib.util
import logging
import json
import pandas as pd
from pathlib import Path
from typing import Tuple, Any, Dict, List
from dd_common.path_coordinator import PathCoordinator
from .null_profiler import DatasetDataProfiler
from .reporter import CleaningReportManager
from .imputation_engine import MissingValueHandler
from .rules import CleaningRulesEngine
from .validator import UniversalValidator

class PipelineRunner:
    """
    Orchestrates the multi-stage cleaning process.
    Enforces the 'Bucket Strategy' for dictionary/data synchronization.
    """

    def __init__(self, coordinator: PathCoordinator) -> None:
        self.paths = coordinator
        self.logger = logging.getLogger(__name__)
        self.cleaner_config = self.paths.config.get("cleaner", {})
        
        # Initialize sub-components
        self.profiler = DatasetDataProfiler(self.paths.profiling_report_path)
        
        # 🎯 DYNAMIC RESOLUTION: Bind the reporter to the output target defined in config
        self.reporter = CleaningReportManager(Path(self.paths.clean_dataset_output_path))

        # 📜 Load the Domain Policy Manifest (Phase 0 Discovery Artifact)
        self.manifest = self._load_policy_manifest()
        self.validator = UniversalValidator(self.manifest)

    def run(self, action: str = "full") -> pd.DataFrame:
        """
        Executes the sequence of cleaning steps defined in the authoritative config.

        Args:
            action (str): The specific pipeline stage to execute or 'full' for the entire sequence.

        Returns:
            pd.DataFrame: The transformed (cleaned) dataset.

        Raises:
            FileNotFoundError: If the raw dataset or data dictionary is missing from the resolved paths.
        """
        self.logger.info("🚀 Initializing Cleaner Pipeline Runner...")

        # 📊 STRUCTURAL ASSESSMENT: Output the inferred or confirmed dataset type
        sa_cfg = self.cleaner_config.get("structural_assessment", {})
        ds_type = sa_cfg.get("dataset_type", "unknown")
        self.logger.info(f"📊 Structural Context: [Dataset Type: {ds_type}]")

        # 1. Load Data
        raw_path = self.paths.raw_dataset_path
        if not raw_path.exists():
            raise FileNotFoundError(f"Raw dataset missing at: {raw_path}")
        df = pd.read_csv(raw_path, sep=None, engine='python')

        # 2. Load Parsed Dictionary (Output from Parser)
        dict_path = Path(self.paths.data_dictionary_csv_path)
        if not dict_path.exists():
            raise FileNotFoundError(f"Parsed Data Dictionary not found at: {dict_path}")
        dict_df = pd.read_csv(dict_path)

        # 3. Step: Integrity Sync (Bucket Strategy)
        # We synchronize the dictionary to the data to ensure we only process columns that exist.
        df, dict_df = self._integrity_sync(df, dict_df)

        # 4. Step: Vectorized Cleaning (Manifest-driven formatting)
        # HEURISTIC: Formatting happens while data is in string/object state.
        df = self._execute_vectorized_cleaning(df, dict_df)

        # 4.5 Step: Type Casting (Alignment with Parser Metadata)
        df = self._apply_type_casting(df, dict_df)

        # 5. Step: Row Filtering (Custom Logic Bridge)
        df = self._execute_row_filtering(df)

        if action == "row_filter": return df

        # 6. Step: Imputation (Missing Value Handler - Task 5.3)
        df = self._execute_imputation(df, dict_df)

        if action == "impute": return df

        # 7. Step: Derivation (Custom Feature Engineering - Task 5.4)
        df = self._execute_derivation(df)

        # 7.5 Step: Policy Validation (Universal Validator - Task 6.3)
        df = self._execute_policy_validation(df)

        if action == "derive": return df

        # 8. Step: Column Filtering (Terminal Transformation)
        # HEURISTIC: This is the final transformation step. It is executed last to ensure 
        # that all preceding steps (imputation, derivation, policy audit) have access 
        # to all available attributes before they are physically purged.
        df = self._execute_column_filtering(df)

        if action == "column_filter": return df

        # 9. Step: Null Profiling (Always performed for visibility)
        attr_col = "attribute_name" if "attribute_name" in dict_df.columns else dict_df.columns[0]
        metadata_lookup = dict_df.set_index(attr_col)["logical_type"].to_dict()
        self.profiler.generate_null_quality_report(df, metadata_lookup=metadata_lookup)

        # 10. Step: Save Results
        self.reporter.write_cleaned_dataset(df)

        self.logger.info("🏁 Pipeline core increment (Integrity & Profiling) complete.")
        return df

    def _load_policy_manifest(self) -> Dict[str, Any]:
        """Loads the domain manifest from the documents directory."""
        manifest_file = self.cleaner_config.get("policy_manifest_file", "policy_manifest.json")
        
        # Resolving via PathCoordinator authoritative routing
        manifest_path = self.paths.cleaner_narrative_directory / manifest_file

        if manifest_path.exists():
            try:
                with open(manifest_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"❌ Failed to load policy manifest: {e}")
        
        self.logger.warning("⚠️ No Policy Manifest found. Proceeding with default heuristics.")
        return {}

    def _execute_vectorized_cleaning(self, df: pd.DataFrame, dict_df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies formatting rules (padding, casing) driven by the policy manifest.

        Args:
            df (pd.DataFrame): The operational dataset.
            dict_df (pd.DataFrame): The synchronized operational dictionary.

        Returns:
            pd.DataFrame: Data with manifest-driven string formatting applied.
        """
        # Derive active prefixes from the dictionary entity assignments
        prefixes = []
        if "provisional_entity_assignment" in dict_df.columns:
            prefixes = dict_df["provisional_entity_assignment"].unique().tolist()
        
        engine = CleaningRulesEngine(active_prefixes=prefixes, policy_manifest=self.manifest)
        
        self.logger.info("🧹 Applying manifest-driven vectorized transformations...")
        return engine.execute_transformations(df)

    def _execute_policy_validation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes regulatory audit rules and isolates violations based on the Policy Manifest.

        Args:
            df (pd.DataFrame): The dataset to validate.

        Returns:
            pd.DataFrame: The dataset stripped of quarantined records, containing validation flags.
        """
        df_out, quarantine_indices = self.validator.execute_validation(df)
        
        if quarantine_indices:
            self.logger.warning(f"🛡️ Policy Validation: Isolating {len(quarantine_indices)} records to quarantine.")
            
            # Isolate records for the quarantine file
            quarantine_df = df_out.loc[quarantine_indices]
            self._write_quarantine_records(quarantine_df)
            
            # Remove from active pipeline
            df_out = df_out.drop(index=quarantine_indices)
            
        return df_out

    def _write_quarantine_records(self, df: pd.DataFrame) -> None:
        """Persists isolated records to the configured quarantine directory."""
        q_path = self.paths.quarantine_path
        q_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(q_path, index=False)
        self.logger.info(f"📁 Isolated records saved to: {q_path}")

    def _execute_column_filtering(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Physically removes attributes specified in the configuration as a terminal step.

        Args:
            df (pd.DataFrame): The dataset being cleaned.

        Returns:
            pd.DataFrame: Dataset with dropped columns removed.
        """
        drop_cols = self.cleaner_config.get("column_filters", {}).get("drop_attributes", [])
        if not drop_cols:
            return df
            
        # Capture count for visual confirmation as requested
        target_drops = [c for c in drop_cols if c in df.columns]
        self.logger.info(f"✂️  Column Filter: Removing {len(target_drops)} attributes from the dataset.")

        if target_drops:
            df = df.drop(columns=target_drops)
        return df

    def _execute_row_filtering(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies row exclusion logic based on config overrides and custom logic hooks.

        Args:
            df (pd.DataFrame): The dataset being cleaned.

        Returns:
            pd.DataFrame: Dataset with excluded rows removed.
        """
        filters = self.cleaner_config.get("row_filters", {}).get("attribute_overrides", {})
        if not filters:
            return df
            
        custom_module = self._load_custom_logic()
        if not custom_module:
            return df
            
        initial_count = len(df)
        for rule_name, action_data in filters.items():
            # Normalize to list to support single strings or multiple components
            actions = [action_data] if isinstance(action_data, str) else action_data
            
            for action in actions:
                if action.startswith("custom:"):
                    func_name = action.split(":")[1]
                    if hasattr(custom_module, func_name):
                        self.logger.info(f"🛡️ Applying custom row filter: {rule_name} ({func_name})")
                        func = getattr(custom_module, func_name)
                        # Filter Contract: func(df) -> pd.Index (indices to KEEP)
                        keep_index = func(df)
                        df = df.loc[keep_index]
                    else:
                        self.logger.error(f"❌ Custom filter function '{func_name}' not found in domain logic.")
        
        dropped = initial_count - len(df)
        if dropped > 0:
            self.logger.info(f"✂️ Row Filtering complete: {dropped} rows excluded ({len(df)} remaining).")
            
        return df

    def _execute_imputation(self, df: pd.DataFrame, dict_df: pd.DataFrame) -> pd.DataFrame:
        """
        Implements the Resolution Hierarchy for missing values across the operational pool.

        Args:
            df (pd.DataFrame): The dataset containing missing values.
            dict_df (pd.DataFrame): Operational dictionary containing logical types for strategy resolution.

        Returns:
            pd.DataFrame: Dataset with missing values resolved.
        """
        # Identify columns with nulls
        null_cols = df.columns[df.isna().any()].tolist()
        if not null_cols:
            return df
            
        self.logger.info(f"🩹 Imputation: Inspecting {len(null_cols)} columns with missing data for strategies...")
        # Use authoritative base_dir from coordinator
        handler = MissingValueHandler(self.paths.config, self.paths.base_dir)

        attr_col = "attribute_name" if "attribute_name" in dict_df.columns else dict_df.columns[0]

        for col in null_cols:
            l_type = "unknown"
            if col in dict_df[attr_col].values:
                l_type = str(dict_df.loc[dict_df[attr_col] == col, 'logical_type'].iloc[0]).lower()
            
            df[col] = handler.resolve(df, col, l_type)

        return df

    def _execute_derivation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes custom feature derivations defined in the Custom Code Bridge.

        Args:
            df (pd.DataFrame): The dataset being cleaned.

        Returns:
            pd.DataFrame: Dataset with new derived attributes appended.
        """
        derivations = self.cleaner_config.get("derivation", {}).get("attribute_overrides", {})
        if not derivations:
            return df
            
        custom_module = self._load_custom_logic()
        if not custom_module:
            return df

        for attr, strategy in derivations.items():
            if strategy.startswith("custom:"):
                func_name = strategy.split(":")[1]
                if hasattr(custom_module, func_name):
                    self.logger.info(f"✨ Executing derivation: {attr} ({func_name})")
                    func = getattr(custom_module, func_name)
                    # Derivation Contract: func(df) -> pd.DataFrame
                    df = func(df)
        return df

    def _load_custom_logic(self) -> Any:
        """
        Dynamically loads the python module containing domain-specific logic from scripts/.

        Returns:
            Optional[Module]: The loaded python module or None if not defined/found.
        """
        logic_path_str = self.cleaner_config.get("custom_logic_path")
        if not logic_path_str:
            return None
            
        # Use authoritative base_dir from coordinator
        logic_path = self.paths.base_dir / logic_path_str
        
        if not logic_path.exists():
            self.logger.warning(f"⚠️ Custom logic script not found at {logic_path}")
            return None
            
        try:
            spec = importlib.util.spec_from_file_location("domain_logic", logic_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            self.logger.error(f"❌ Failed to load custom logic module: {e}")
            return None

    def _apply_type_casting(self, df: pd.DataFrame, dict_df: pd.DataFrame) -> pd.DataFrame:
        """
        Casts DataFrame columns to their intended physical types based on Parser metadata.

        Args:
            df (pd.DataFrame): The raw dataset.
            dict_df (pd.DataFrame): The operational dictionary containing type mappings.

        Returns:
            pd.DataFrame: Dataset with standardized physical types.
        """
        self.logger.info("🎭 Applying physical type casting based on dictionary metadata...")
        
        # Resolve the attribute name column in the dictionary
        attr_col = "attribute_name"
        if attr_col not in dict_df.columns:
            attr_col = dict_df.columns[0]
            
        for _, row in dict_df.iterrows():
            col = str(row[attr_col])
            p_type = str(row.get("physical_type", "unknown")).lower()
            
            if col not in df.columns or p_type == "unknown":
                continue
                
            try:
                if p_type == "datetime":
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                elif p_type == "int":
                    # Use Int64 (nullable integer) to prevent float conversion of NaN
                    df[col] = pd.to_numeric(df[col], errors='coerce').round().astype('Int64')
                elif p_type == "float":
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                elif p_type == "bool":
                    df[col] = df[col].map({'True': True, 'False': False, '1': True, '0': False, 1: True, 0: False}, na_action='ignore')
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to cast column '{col}' to {p_type}: {e}")
                
        return df

    def _integrity_sync(self, df: pd.DataFrame, dict_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Synchronizes the raw dataset headers with the Parser's Operational Matrix.

        Args:
            df (pd.DataFrame): The raw dataset headers.
            dict_df (pd.DataFrame): The provisional dictionary produced by the parser.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: A subsetted DataFrame containing only 'Clean Bucket' 
                                              columns and its corresponding dictionary mapping.

        SELECTION LOGIC (Clean Bucket Filtering):
        The cleaner treats the loaded dictionary as an authoritative filter mask.
        1. Only attributes present in the 'Clean Bucket' (Parser Output) are permitted.
        2. 'Ghost' columns (Data columns with no dictionary entry) are physically purged.
        3. 'Orphans' are stripped to ensure metadata-data alignment for the current file.
        """
        self.logger.info("⚖️ Executing Integrity Sync (Operational Bucket Subsetting)...")
        
        attr_col = "attribute_name"
        if attr_col not in dict_df.columns:
            attr_col = dict_df.columns[0]

        # 🎯 INTERSECTION ENFORCEMENT: Pick up only the 'Clean Bucket'
        operational_attributes = set(dict_df[attr_col].astype(str))
        physical_headers = set(df.columns)
        clean_bucket = sorted(list(physical_headers & operational_attributes))

        # 🛡️ GHOST REMOVAL: Drop any physical column that wasn't semantically qualified by the parser
        ghosts = physical_headers - operational_attributes
        if ghosts:
            self.logger.warning(f"👻 Ghost Removal: Purging {len(ghosts)} unmapped columns from raw data.")
            for ghost in sorted(list(ghosts)):
                self.logger.debug(f"    [GHOST]: {ghost}")

        # Apply the filter to both Data and Dictionary
        df = df[clean_bucket].copy()
        dict_df = dict_df[dict_df[attr_col].isin(clean_bucket)].reset_index(drop=True)

        # 🛡️ DEDUPLICATION: Ensure the dictionary has unique attribute mappings to prevent index collisions
        if not dict_df[attr_col].is_unique:
            self.logger.warning("⚠️ Non-unique attributes found in Data Dictionary. Deduplicating operational matrix.")
            dict_df = dict_df.drop_duplicates(subset=[attr_col]).reset_index(drop=True)

        # Optional: Save the synchronized 'Bucket A' dictionary to narrative directory for traceability
        sync_path = self.paths.cleaner_narrative_directory / "synchronized_dictionary.csv"
        dict_df.to_csv(sync_path, index=False)
        self.logger.info(f"✅ Synchronized operational matrix saved to: {sync_path.name}")

        return df, dict_df