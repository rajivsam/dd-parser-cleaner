"""Idempotent cleaning pipeline runner for structured data transformation."""

import importlib.util
import logging
import pandas as pd
from pathlib import Path
from typing import Tuple, Any
from path_coordinator import PathCoordinator
from .null_profiler import DatasetDataProfiler
from .reporter import CleaningReportManager

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
        output_dir = self.paths.cleaner_output_directory
        filename = self.cleaner_config.get("clean_output_filename", "cleaned_data.csv")
        self.reporter = CleaningReportManager(output_dir / filename)

    def run(self) -> pd.DataFrame:
        """Executes the sequence of cleaning steps defined in the authoritative config."""
        self.logger.info("🚀 Initializing Cleaner Pipeline Runner...")

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

        # 4. Step: Type Casting (Alignment with Parser Metadata)
        df = self._apply_type_casting(df, dict_df)

        # 5. Step: Row Filtering (Custom Logic Bridge)
        df = self._execute_row_filtering(df)

        # 6. Step: Null Profiling (Always performed for visibility)
        self.profiler.generate_null_quality_report(df)

        # 7. Step: Save Results
        self.reporter.write_cleaned_dataset(df)

        self.logger.info("🏁 Pipeline core increment (Integrity & Profiling) complete.")
        return df

    def _execute_row_filtering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies row exclusion logic based on config overrides."""
        filters = self.cleaner_config.get("row_filters", {}).get("attribute_overrides", {})
        if not filters:
            return df
            
        custom_module = self._load_custom_logic()
        if not custom_module:
            return df
            
        initial_count = len(df)
        for rule_name, action in filters.items():
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

    def _load_custom_logic(self) -> Any:
        """Dynamically loads the python module containing domain-specific logic."""
        logic_path_str = self.cleaner_config.get("missing_values", {}).get("custom_logic_path")
        if not logic_path_str:
            return None
            
        # PathCoordinator handles working_dir (e.g., tests/)
        logic_path = self.paths.raw_dataset_path.parent.parent / logic_path_str
        
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
        """Casts DataFrame columns to their intended physical types based on the dictionary."""
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
        Reconciles the Data Dictionary against physical file headers.
        
        Bucket A (Operational): Common to both.
        Bucket B (Orphans): In Dictionary but missing from Data (Stripped).
        Bucket C (Ghosts): In Data but missing from Dictionary (Logged).
        """
        self.logger.info("⚖️ Executing Integrity Sync (Bucket Strategy)...")
        
        # We assume 'attribute_name' is the key column in the parser's output CSV
        attr_col = "attribute_name"
        if attr_col not in dict_df.columns:
            self.logger.warning(f"Column '{attr_col}' not found in dictionary. Attempting index 0.")
            attr_col = dict_df.columns[0]

        data_cols = set(df.columns)
        dict_cols = set(dict_df[attr_col].astype(str))

        bucket_a = data_cols & dict_cols
        bucket_b = dict_cols - data_cols
        bucket_c = data_cols - dict_cols

        self.logger.info(f"  - Bucket A (Matches): {len(bucket_a)}")
        
        if bucket_b:
            self.logger.warning(f"  - Bucket B (Orphans detected): {len(bucket_b)} attributes in dictionary are missing from raw data.")
            for orphan in sorted(list(bucket_b)):
                self.logger.debug(f"    [ORPHAN]: {orphan}")
            # Strip orphans from the dictionary to prevent processing errors
            dict_df = dict_df[dict_df[attr_col].isin(bucket_a)].reset_index(drop=True)

        if bucket_c:
            self.logger.warning(f"  - Bucket C (Ghosts detected): {len(bucket_c)} columns in data have no dictionary entry.")
            for ghost in sorted(list(bucket_c)):
                self.logger.debug(f"    [GHOST]: {ghost}")

        # Optional: Save the synchronized 'Bucket A' dictionary for downstream pipeline traceability
        sync_path = self.paths.cleaner_output_directory / "synchronized_dictionary.csv"
        dict_df.to_csv(sync_path, index=False)
        self.logger.info(f"✅ Synchronized operational matrix saved to: {sync_path.name}")

        return df, dict_df