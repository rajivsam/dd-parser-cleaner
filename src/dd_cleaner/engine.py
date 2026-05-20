import os
import logging
import yaml
import pandas as pd
from typing import Dict, Any

logger = logging.getLogger("dd_cleaner")

class DataCleanerEngine:
    def __init__(self):
        self.working_dir: str = ""
        self.config: Dict[Any, Any] = {}

    def set_working_config(self, working_dir: str, config_path: str):
        """Loads the shared config and binds the root working directory context."""
        abs_config_path = os.path.abspath(config_path)
        if not os.path.exists(abs_config_path):
            raise FileNotFoundError(f"Configuration file not found at: {abs_config_path}")
        with open(abs_config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        if not os.path.isdir(working_dir):
            raise FileNotFoundError(f"Target data directory not found: {os.path.abspath(working_dir)}")
        self.working_dir = os.path.abspath(working_dir)
        logger.info("Cleaner Context Initialized.")

    def verify_and_load_blueprint(self) -> pd.DataFrame:
        """Handshakes with the dd_parser output subdirectory to grab the metadata map."""
        parser_dir = self.config.get('dd_parser_output_dir', 'dd_analysis_results')
        blueprint_name = self.config.get('output_filename', 'sba_analysis_results.csv')
        blueprint_path = os.path.isabs(parser_dir) and os.path.join(parser_dir, blueprint_name) or os.path.abspath(os.path.join(self.working_dir, parser_dir, blueprint_name))
        
        if not os.path.exists(blueprint_path):
            raise FileNotFoundError(f"Missing parsing matrix blueprint file at: {blueprint_path}")
            
        with open(blueprint_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if not first_line.startswith("# DD-PARSER-SIGNATURE"):
                raise ValueError(f"Rejected: File at {blueprint_path} does not originate from dd-parser pipeline!")
                
        return pd.read_csv(blueprint_path, comment='#')

    def generate_cleaning_markdown_summary(self, data_df: pd.DataFrame, base_project_dir: str):
        """Compiles clean data type breakdowns and null metrics to the documents/ workspace."""
        doc_dir_name = self.config.get('documents_dir', 'documents')
        abs_doc_dir = os.path.abspath(os.path.join(base_project_dir, doc_dir_name))
        os.makedirs(abs_doc_dir, exist_ok=True)
        
        report_path = os.path.join(abs_doc_dir, "data_cleaning_summary.md")
        type_summary = data_df.dtypes.value_counts()
        null_counts = data_df.isnull().sum()
        total_rows = len(data_df)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 🧼 KMDS Data Helper: Data Cleaning Summary Report\n\n")
            f.write("## 📊 Converted Data Types Summary\n")
            for dtype_name, count in type_summary.items():
                f.write(f"| {dtype_name} | {count} |\n")
            f.write("\n## 🗃️ Missing Value Counts\n")
            for col in data_df.columns:
                f.write(f"| `{col}` | {null_counts[col]} | {(total_rows - null_counts[col])/total_rows*100:.2f}% |\n")
                
        logger.info(f"Generated clean dataset validation profile saved to: {report_path}")

    def execute_numeric_imputer(self, series: pd.Series) -> pd.Series:
        """
        Isolated strategy vector for missing continuous numerical data items.
        Swap out this inner logic to upgrade from median to kNN/Iterative models later.
        """
        fill_value = series.median()
        return series.fillna(fill_value)

    def execute_poc_feature_prep(self, df: pd.DataFrame, blueprint_df: pd.DataFrame) -> pd.DataFrame:
        """Applies basic missing value strategies and builds address strings for geocoding."""
        prep_df = df.copy()
        raw_cols_lower = {col.lower(): col for col in prep_df.columns}
        
        # 1. Extract and compile Geo attributes on a per-entity basis
        geo_blueprint = blueprint_df[blueprint_df['is_geographical'] == True]
        entity_geo_groups = geo_blueprint.groupby('provisional_entity')
        
        for entity_name, group in entity_geo_groups:
            geo_cols = []
            for _, row in group.iterrows():
                attr_lower = row['attribute_name'].lower()
                if attr_lower in raw_cols_lower:
                    geo_cols.append(raw_cols_lower[attr_lower])
            
            if geo_cols:
                logger.info(f" -> Consolidating geo attributes for entity: '{entity_name}'")
                prep_df[f"{entity_name.lower()}_geo_search_string"] = prep_df[geo_cols].fillna("").astype(str).agg(", ".join, axis=1)
        
        # 2. Variable Strategy Loop driven by Schema Typing definitions
        for _, row in blueprint_df.iterrows():
            attr_lower = row['attribute_name'].lower()
            if attr_lower not in raw_cols_lower:
                continue
            col_name = raw_cols_lower[attr_lower]
            t_type = row['provisional_python_type']
            
            # Numeric Strategy: Route directly through decoupled method
            if t_type in ['int', 'float']:
                if prep_df[col_name].isnull().any():
                    prep_df[col_name] = self.execute_numeric_imputer(prep_df[col_name])
                    
            # Categorical Strategy: Explicitly flag missing indices
            elif t_type == 'str':
                prep_df[col_name] = prep_df[col_name].replace(["nan", "None", ""], None).fillna("MISSING")
                
        return prep_df

    def clean_dataset(self):
        blueprint_df = self.verify_and_load_blueprint()
        raw_file = self.config.get('raw_dataset_file', 'sba_loans_raw.csv')
        base_project_dir = os.path.abspath(os.path.join(self.working_dir, ".."))
        raw_path = os.path.isabs(raw_file) and raw_file or os.path.abspath(os.path.join(base_project_dir, "data", raw_file))
        
        data_df = pd.read_csv(raw_path)
        raw_columns_lower = {col.lower(): col for col in data_df.columns}
        
        # [STAGE 1] Perform baseline type conversions
        for _, row in blueprint_df.iterrows():
            blueprint_attr = row['attribute_name']
            target_type = row['provisional_python_type']
            attr_lower = blueprint_attr.lower()
            if attr_lower not in raw_columns_lower: continue
            col_name = raw_columns_lower[attr_lower]
            
            try:
                if target_type == 'bool':
                    if data_df[col_name].dtype == object:
                        data_df[col_name] = data_df[col_name].astype(str).str.upper().str.strip().isin(['TRUE', '1', 'Y', 'YES', 'T'])
                    else:
                        data_df[col_name] = data_df[col_name].fillna(False).astype(bool)
                elif target_type == 'int':
                    data_df[col_name] = pd.to_numeric(data_df[col_name], errors='coerce')
                elif target_type == 'float':
                    data_df[col_name] = pd.to_numeric(data_df[col_name], errors='coerce')
                elif target_type in ['datetime.date', 'datetime.datetime']:
                    data_df[col_name] = pd.to_datetime(data_df[col_name], errors='coerce')
                else:
                    data_df[col_name] = data_df[col_name].astype(str).str.strip()
            except Exception: pass

        # [STAGE 2] Write standard output and generate report
        cleaner_dir = self.config.get('dd_cleaner_output_dir', 'dd_cleaner_results')
        clean_filename = self.config.get('clean_output_filename', 'sba_loans_clean.csv')
        abs_dest_dir = os.path.isabs(cleaner_dir) and cleaner_dir or os.path.abspath(os.path.join(base_project_dir, "data", cleaner_dir))
        os.makedirs(abs_dest_dir, exist_ok=True)
        
        data_df.to_csv(os.path.join(abs_dest_dir, clean_filename), index=False)
        self.generate_cleaning_markdown_summary(data_df, base_project_dir)
        
        # [STAGE 3] Run PoC feature prep AFTER generating the report
        logger.info("Executing PoC Missing Value Strategies and Geo-string preparation...")
        poc_ready_df = self.execute_poc_feature_prep(data_df, blueprint_df)
        
        # Save the finalized feature-selection dataset
        poc_output_path = os.path.join(abs_dest_dir, "feature_selection_ready.csv")
        poc_ready_df.to_csv(poc_output_path, index=False)
        logger.info(f"🎉 Hand-off Complete! Modeling matrix saved to: {poc_output_path}")
