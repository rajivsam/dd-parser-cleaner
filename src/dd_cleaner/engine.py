import os
import yaml
import logging
import pandas as pd
from typing import Dict, Any, List
from path_coordinator import PlatformPathResolver

logger = logging.getLogger("dd_cleaner")

class DatasetCleaner:
    def __init__(self):
        self.working_dir: str = ""
        self.config: Dict[Any, Any] = {}
        self.geo_metadata: pd.DataFrame = pd.DataFrame()
        self.paths: PlatformPathResolver = None

    def set_working_config(self, working_dir: str, config_path: str):
        abs_config_path = os.path.abspath(config_path)
        if not os.path.exists(abs_config_path):
            raise FileNotFoundError(f"Configuration file not found at: {abs_config_path}")
        
        with open(abs_config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        if not os.path.isdir(working_dir):
            raise FileNotFoundError(f"Target data directory not found: {os.path.abspath(working_dir)}")
        self.working_dir = os.path.abspath(working_dir)
        
        # Instantiate the centralized Platform Abstraction Routing Engine
        self.paths = PlatformPathResolver(working_dir=self.working_dir, config=self.config)
        
        # Initialize output directories via abstraction resolver targets
        abs_out_dir = self.paths.data_cleaner_dir
        
        # Initialize Logger Routing
        log_file_path = os.path.join(abs_out_dir, "cleaner_run.log")
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(file_handler)
        
        logger.info("Cleaner Context initialized successfully with Platform Abstraction.")

    def validate_pipeline_handshake(self) -> str:
        """
        Validates pipeline integrity via the separated sidecar signature tracking file.
        Uses the path coordinator to safely isolate structural checking targets.
        """
        abs_metadata_path = self.paths.data_dictionary_csv_path
        abs_signature_path = f"{abs_metadata_path}.signature"
        
        if not os.path.exists(abs_metadata_path):
            raise FileNotFoundError(f"Pipeline Handshake Failed: Data dictionary metadata not found at {abs_metadata_path}")
        if not os.path.exists(abs_signature_path):
            raise FileNotFoundError(f"Pipeline Handshake Failed: Guard signature file missing at {abs_signature_path}")
            
        with open(abs_signature_path, 'r', encoding='utf-8') as f:
            sig_line = f.readline().strip()
            
        if not sig_line.startswith("# DD-PARSER-SIGNATURE: PROCESSED-BY-"):
            raise ValueError(f"Pipeline Handshake Rejected: Malformed control signature found: '{sig_line}'")
            
        logger.info(f"Pipeline handshake verified via sidecar context: {sig_line}")
        return abs_metadata_path

    def scrub_city_field(self, series: pd.Series) -> pd.Series:
        """Standardizes geographic city names into Title Case layout format safely handling nulls."""
        def clean_city(val: Any) -> Any:
            if pd.isna(val) or str(val).strip().lower() in ['nan', 'none', '']:
                return None
            return str(val).strip().title()
        return series.apply(clean_city)

    def scrub_state_field(self, series: pd.Series) -> pd.Series:
        """Standardizes geographic state abbreviations into uppercase strings safely handling nulls."""
        def clean_state(val: Any) -> Any:
            if pd.isna(val) or str(val).strip().lower() in ['nan', 'none', '']:
                return None
            return str(val).strip().upper()
        return series.apply(clean_state)

    def scrub_zip_field(self, series: pd.Series) -> pd.Series:
        """Enforces a strict 5-digit string constraint by zero-padding short sequences."""
        def pad_zip(val: Any) -> Any:
            if pd.isna(val) or str(val).strip().lower() in ['nan', 'none', '']:
                return None
            
            # Extract string portion before any floating point decimal point safely
            raw_str = str(val).split('.')
            clean_str = raw_str[0].strip()
            
            if not clean_str:
                return None
                
            return clean_str.zfill(5)[:5]
        return series.apply(pad_zip)

    def process_cleaning_pipeline(self):
        logger.info("Data scrubbing pipeline execution sequence engaged.")
        
        # 1. Execute and verify the pipeline handshake
        metadata_csv_path = self.validate_pipeline_handshake()
        self.geo_metadata = pd.read_csv(metadata_csv_path)
        
        # 2. Ingest the case-preserved raw dataset matrix via resolver path
        abs_raw_path = self.paths.raw_data_input_path
        if not os.path.exists(abs_raw_path):
            raise FileNotFoundError(f"Raw file targeted for scrubbing absent at: {abs_raw_path}")
            
        df_data = pd.read_csv(abs_raw_path)
        logger.info(f"Ingested raw dataset containing {len(df_data)} rows and {len(df_data.columns)} columns.")
        
        # 3. Separate geographic fields matching our metadata dictionary rule map
        geo_fields_df = self.geo_metadata[self.geo_metadata['is_geographical'] == True]
        
        # 4. Transform elements based on actual field identity rules
        for _, row in geo_fields_df.iterrows():
            target_col = row['attribute_name']
            
            # Defensive check matching case-preserved naming structures
            if target_col not in df_data.columns:
                logger.warning(f"Configured column target '{target_col}' missing from raw payload headers. Skipping.")
                continue
                
            logger.info(f"Executing geographic scrub routine on attribute column: {target_col}")
            
            target_col_lower = target_col.lower()
            if 'zip' in target_col_lower:
                df_data[target_col] = self.scrub_zip_field(df_data[target_col])
            elif 'city' in target_col_lower:
                df_data[target_col] = self.scrub_city_field(df_data[target_col])
            elif 'state' in target_col_lower:
                df_data[target_col] = self.scrub_state_field(df_data[target_col])
            else:
                df_data[target_col] = df_data[target_col].astype(str).str.strip()

        # 5. Export clean database arrays into resolved cleaner directory
        clean_filename = self.config.get('clean_output_filename', 'sba_loans_clean.csv')
        abs_clean_path = os.path.join(self.paths.data_cleaner_dir, clean_filename)
        
        df_data.to_csv(abs_clean_path, index=False)
        logger.info(f"Cleaned dataset written successfully to workflow path: {abs_clean_path}")
        
        # 6. Generate execution summary metric file reports
        self.generate_cleaning_summary(df_data, geo_fields_df)

    def generate_cleaning_summary(self, df_clean: pd.DataFrame, geo_metadata: pd.DataFrame):
        abs_doc_dir = self.paths.documents_dir
        md_path = os.path.join(abs_doc_dir, "data_cleaning_summary.md")
        
        geo_columns_cleaned = geo_metadata['attribute_name'].tolist()
        columns_block = "\n".join([f"- `{col}`" for col in geo_columns_cleaned])
        
        md_content = f"""# Data Cleaning Transformation Summary

## 📈 Execution Scope Metrics
- **Raw Processing Payload Length**: {len(df_clean)} records
- **Geographic Scrubbing Sweeps Executed**: {len(geo_columns_cleaned)} columns cleaned

## 🛠️ Cleansed Geographic Attribute Inventory
{columns_block}

## 📋 Sample Clean Output View
"""
        # Formats layout to markdown table explicitly using active data targets
        md_content += df_clean[geo_columns_cleaned].head(5).to_markdown(index=False)
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        logger.info(f"Analytics file metadata reporting snapshot dumped into target workspace: {md_path}")
