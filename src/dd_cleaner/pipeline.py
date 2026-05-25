"""Idempotent cleaning pipeline runner for structured data transformation."""

import logging
import pandas as pd
from pathlib import Path
from typing import Tuple
from path_coordinator import PathCoordinator
from .null_profiler import DatasetDataProfiler

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

        # 5. Step: Null Profiling (Always performed for visibility)
        self.profiler.generate_null_quality_report(df)

        self.logger.info("🏁 Pipeline core increment (Integrity & Profiling) complete.")
        return df

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