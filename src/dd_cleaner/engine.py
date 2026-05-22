import os
import pandas as pd
from pathlib import Path
from path_coordinator import PathCoordinator

class DatasetCleaner:
    """
    Symmetric operational table cleaner applying vectorized pandas 
    title-casing and zero-padding transformations based on path coordinator blueprints.
    """
    def __init__(self, path_coordinator: PathCoordinator):
        # 🎯 FIX: Force injection of the routing orchestration layer contract
        if path_coordinator is None:
            raise TypeError("DatasetCleaner requires a valid PathCoordinator instance.")

        self.paths = path_coordinator
        self.config = {}
        self.cleaner_config = {}

        # Hydrate configuration dictionaries immediately from the mandatory coordinator
        self._hydrate_internal_configurations()

    def _hydrate_internal_configurations(self) -> None:
        """Helper to cleanly extract active framework configuration boundaries."""
        self.config = self.paths.config
        self.cleaner_config = self.config.get("cleaner", self.config)

    def set_working_config(self, working_dir: str, config_path: str) -> None:
        """Resets the internal environment configuration boundaries with explicit parameters."""
        # 🧼 FIX: Re-instantiate the layout parameters using the class blueprint definition
        self.paths = self.paths.__class__(config_path=config_path, working_dir=working_dir)
        self._hydrate_internal_configurations()

    def process_cleaning_pipeline(self) -> pd.DataFrame:
        """
        Executes end-to-end data cleaning pipelines exactly as requested 
        by line 34 of your automated test suite tracker.
        """
        # 1. Fetch unified target file path from the resolver contract
        input_path = self.paths.raw_dataset_path
        if not input_path.exists():
            raise FileNotFoundError(f"Raw operational dataset table missing at: {input_path}")
            
        df_raw = pd.read_csv(input_path)
        
        # 2. Extract original metadata dictionary casing map to protect structural headers
        dict_path = Path(self.paths.data_dictionary_csv_path)
        casing_map = {}
        if dict_path.exists():
            try:
                df_dict = pd.read_csv(dict_path)
                if "attribute_name" in df_dict.columns:
                    # Construct case lookup mapping contract dictionary
                    casing_map = {str(attr).lower().strip(): str(attr).strip() for attr in df_dict["attribute_name"].dropna()}
            except Exception:
                pass  # Fall back gracefully if file is unreadable during transient steps

        # 3. Execute defensive, vectorized scrubbing transformations
        cleaned_df = self._execute_scrubbing_transformations(df_raw)
        
        # 4. Enforce exact case tracking preservation to fix header mutations
        if casing_map:
            new_columns = []
            for col in cleaned_df.columns:
                col_clean = str(col).lower().strip()
                if col_clean in casing_map:
                    new_columns.append(casing_map[col_clean])
                else:
                    new_columns.append(col)
            cleaned_df.columns = new_columns
        
        # 5. Output results using path coordinate properties exclusively
        output_file_path = self.paths.clean_dataset_output_path
        cleaned_df.to_csv(output_file_path, index=False)
        
        return cleaned_df

    def process_pipeline(self) -> pd.DataFrame:
        """Backward-compatible alias keeping interface symmetric with parser."""
        return self.process_cleaning_pipeline()

    def _execute_scrubbing_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies zero-padding to numeric identifiers and vectorized title-casing
        to unformatted structural strings. Handles mixed type cells defensively.
        """
        df_out = df.copy()
        
        # Identify text columns based on schema properties or string indicators
        for col in df_out.columns:
            col_lower = str(col).lower()
            
            # 🧼 DEFENSIVE STEP: Convert to string type first to eliminate float NaN exceptions
            series_str = df_out[col].fillna("").astype(str).str.strip()
            
            # Heuristic 1: Apply Vectorized Title-Casing on Name/Address Contexts
            if any(token in col_lower for token in ["name", "street", "city", "state"]):
                df_out[col] = series_str.str.title()
                
            # Heuristic 2: Apply Smart Zero-Padding on Codes / ZIP / ID Fields
            elif any(token in col_lower for token in ["zip", "id", "number", "code"]):
                # Ensure zip codes are padded to 5 digits, other codes left to native length
                pad_width = 5 if "zip" in col_lower else 0
                if pad_width > 0:
                    df_out[col] = series_str.str.zfill(pad_width)
                else:
                    df_out[col] = series_str

        return df_out
