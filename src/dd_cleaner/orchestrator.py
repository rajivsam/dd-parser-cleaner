"""Coordinates data cleaning lifecycles using Constructor Dependency Injection."""

import json
import pandas as pd
from pathlib import Path
from typing import List
from path_coordinator import PathCoordinator
from .rules import CleaningRulesEngine
from .reporter import CleaningReportManager
# 📊 ALIGNED IMPORT FIX: Point strictly to the new null_profiler module asset
from .null_profiler import DatasetDataProfiler


class CleanerPipelineOrchestrator:
    """Symmetric cleaner pipeline manager mirroring the parser execution layout."""

    def __init__(self, path_coordinator: PathCoordinator) -> None:
        """Injects operational dependencies and isolates configuration boundaries."""
        if path_coordinator is None:
            raise TypeError("CleanerPipelineOrchestrator requires a valid PathCoordinator instance.")
        self.paths = path_coordinator

    def process_cleaning_pipeline(self) -> pd.DataFrame:
        """Executes the data cleaning stage sequentially using decoupled sub-modules."""
        input_path = self.paths.raw_dataset_path
        if not input_path.exists():
            raise FileNotFoundError(f"Raw operational dataset table missing at: {input_path}")
            
        df_raw = pd.read_csv(input_path)
        
        # 🎯 DATA QUALITY PROFILE: Run baseline metrics BEFORE any scrubbing transformations execute
        profiler = DatasetDataProfiler(output_report_path=self.paths.profiling_report_path)
        print(f"📊 Generating raw dataset metrics report at: {self.paths.profiling_report_path}")
        profiler.generate_null_quality_report(df_raw)

        dict_path = Path(self.paths.data_dictionary_csv_path)
        casing_map = {}
        active_prefixes: List[str] = []
        
        if dict_path.exists():
            try:
                df_dict = pd.read_csv(dict_path)
                attr_col_name = self.paths.data_dictionary_attribute_col_name
                
                if attr_col_name in df_dict.columns:
                    casing_map = {str(attr).lower().strip(): str(attr).strip() for attr in df_dict[attr_col_name].dropna()}
                elif "attribute_name" in df_dict.columns:
                    casing_map = {str(attr).lower().strip(): str(attr).strip() for attr in df_dict["attribute_name"].dropna()}
                    
                sig_path = dict_path.with_suffix(".signature")
                if sig_path.exists():
                    with open(sig_path, "r", encoding="utf-8") as sf:
                        meta_payload = json.load(sf)
                        active_prefixes = meta_payload.get("dynamic_prefixes", [])
                        print(f"📡 Cleaner imported dynamic prefix matrix from sidecar: {active_prefixes}")
            except Exception as e:
                print(f"⚠️ Handshake read warning: Falling back to empty state. Detail: {e}")

        # Continue with decoupled cleaner rule passes
        rules_engine = CleaningRulesEngine(active_prefixes=active_prefixes)
        reporter = CleaningReportManager(output_file_path=self.paths.clean_dataset_output_path)

        cleaned_df = rules_engine.execute_transformations(df_raw)
        
        if casing_map:
            cleaned_df.columns = [
                casing_map.get(str(col).lower().strip(), col)
                for col in cleaned_df.columns
            ]
        
        reporter.write_cleaned_dataset(cleaned_df)
        return cleaned_df

    def process_pipeline(self) -> pd.DataFrame:
        """Backward-compatible alias keeping interface symmetric with parser."""
        return self.process_cleaning_pipeline()
