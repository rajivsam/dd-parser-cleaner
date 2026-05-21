import os
import json
import yaml
import time
import logging
import pandas as pd
from pypdf import PdfReader
import ollama
from typing import List, Dict, Any
from dd_parser.models import AttributeAnalysis, BatchAnalysisResponse
from path_coordinator import PlatformPathResolver

logger = logging.getLogger("dd_parser")

class LocalEntityClassifier:
    def __init__(self):
        self.working_dir: str = ""
        self.config: Dict[Any, Any] = {}
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
        
        # Ensure our target destination folders exist prior to creating logs
        abs_output_dir = self.paths.data_dictionary_dir
        
        log_file_path = os.path.join(abs_output_dir, "parser_run.log")
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(file_handler)

        logger.info("Context Initialized with Platform Abstraction Path Routing.")

    def extract_inventory_attributes(self) -> List[str]:
        """
        Extracts 100% of real columns directly from the raw data payload.
        Utilizes the path coordinator to resolve the absolute data directory location.
        """
        abs_raw_path = self.paths.raw_data_input_path
        
        if not os.path.exists(abs_raw_path):
            raise FileNotFoundError(f"Platform Abstraction Gap: Raw dataset file not found at {abs_raw_path}")

        _, ext = os.path.splitext(abs_raw_path)
        ext = ext.lower()
        
        if ext == '.csv':
            df = pd.read_csv(abs_raw_path, nrows=0)
            return [col.strip() for col in df.columns]
        elif ext == '.pdf':
            return [line.strip() for page in PdfReader(abs_raw_path).pages for line in page.extract_text().split('\n') if line.strip()]
        elif ext in ['.md', '.markdown']:
            with open(abs_raw_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        raise ValueError(f"Unsupported format: {ext}")

    def analyze_batch(self, attributes: List[str]) -> List[AttributeAnalysis]:
        """Instructs the LLM to preserve the exact character casing of the input schemas."""
        prompt = f"""
        Analyze the following data dictionary attributes. Maintain the exact character casing of the input names.
    
        ### EXAMPLES OF EXCELLENT PERFORMANCE
        Input: ["BorrCity", "BankStreet", "GrossApproval", "cdc_zip", "ThirdPartyLender_City"]
        Output Schema Map:
        {{
            "analysis": [
                {{"attribute_name": "BorrCity", "provisional_entity": "Borrower", "is_geographical": true, "related_entity": "Borrower", "provisional_python_type": "str"}},
                {{"attribute_name": "BankStreet", "provisional_entity": "Bank", "is_geographical": true, "related_entity": "Bank", "provisional_python_type": "str"}},
                {{"attribute_name": "GrossApproval", "provisional_entity": "Loan", "is_geographical": false, "related_entity": null, "provisional_python_type": "float"}},
                {{"attribute_name": "cdc_zip", "provisional_entity": "cdc", "is_geographical": true, "related_entity": "cdc", "provisional_python_type": "str"}},
                {{"attribute_name": "ThirdPartyLender_City", "provisional_entity": "ThirdPartyLender", "is_geographical": true, "related_entity": "ThirdPartyLender", "provisional_python_type": "str"}}
            ]
        }}

        ### CURRENT EXECUTION BATCH
        Attributes to process: {json.dumps(attributes)}
        """
        response = ollama.chat(
            model=self.config.get('model_name', 'llama3.2'),
            messages=[
                {"role": "system", "content": self.config.get('system_prompt', 'You are a precise data engineering assistant. Respond strictly in JSON.')},
                {"role": "user", "content": prompt}
            ],
            options={"temperature": 0.0},
            format=BatchAnalysisResponse.model_json_schema()
        )
        return BatchAnalysisResponse(**json.loads(response['message']['content'])).analysis

    def post_process_cleaner(self, analysis_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Applies case-insensitive suffix sweeps while keeping original casing intact."""
        cleaned_records = []
        geo_suffixes = ('_street', '_city', '_state', '_zip', '_county', 'street', 'city', 'state', 'zip', 'county')
        
        for item in analysis_list:
            data = item.copy()
            original_attr = data['attribute_name']
            lower_attr = original_attr.lower()
            
            if '_' in lower_attr:
                parts = original_attr.split('_')
                prefix = parts[0] if parts else "unknown"
            elif lower_attr.startswith('borr'):
                prefix = original_attr[:4] if len(original_attr) >= 4 else "Borr"
            elif lower_attr.startswith('bank'):
                prefix = original_attr[:4] if len(original_attr) >= 4 else "Bank"
            elif lower_attr.startswith('project'):
                prefix = original_attr[:7] if len(original_attr) >= 7 else "Project"
            else:
                prefix = data.get('provisional_entity', 'unknown')

            data['provisional_entity'] = prefix

            if lower_attr.endswith(geo_suffixes) or 'district' in lower_attr:
                data['is_geographical'] = True
                data['related_entity'] = prefix
            else:
                data['is_geographical'] = bool(data.get('is_geographical', False))
                if data['is_geographical'] and not data.get('related_entity'):
                    data['related_entity'] = prefix

            cleaned_records.append(data)
        return cleaned_records

    def generate_markdown_summary(self, df: pd.DataFrame, execution_time: float) -> str:
        total_fields = len(df)
        entities = df['provisional_entity'].value_counts().to_dict()
        geo_count = int(df['is_geographical'].sum())
        
        entity_breakdown = "\n".join([f"- **{k}**: {v} fields" for k, v in entities.items()])
        
        md = f"""# Data Dictionary Analysis Summary

## ⏱️ Execution Metrics
- **Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Duration**: {execution_time:.2f} seconds
- **Total Fields Processed**: {total_fields}

## 📊 Entity Distribution Matrix
{entity_breakdown}

## 🌍 Geospatial Insights
- **Geographic Fields Found**: {geo_count}

## 🔍 Detailed Data Mapping Table
"""
        return md + df.to_markdown(index=False)

    def process_pipeline(self):
        start_time = time.time()
        logger.info("Pipeline execution sequence started.")
        
        # Pull inventory via absolute resolved input path variables
        attributes = self.extract_inventory_attributes()
        batch_size = self.config.get('batch_size', 10)
        
        all_analyses: List[AttributeAnalysis] = []
        for i in range(0, len(attributes), batch_size):
            batch = attributes[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1}")
            all_analyses.extend(self.analyze_batch(batch))
            
        dict_records = [model.model_dump() for model in all_analyses]
        final_records = self.post_process_cleaner(dict_records)
        
        df_out = pd.DataFrame(final_records)
        
        # Enforce destination targets out of path resolver properties
        csv_path = self.paths.data_dictionary_csv_path
        df_out.to_csv(csv_path, index=False)
        logger.info(f"Clean uncorrupted CSV data table saved via resolver at: {csv_path}")
        
        # Store verification sidecar control file independently adjacent to metadata table
        signature_path = f"{csv_path}.signature"
        model_tag = self.config.get('model_name', 'llama3.2').upper()
        with open(signature_path, 'w', encoding='utf-8') as f:
            f.write(f"# DD-PARSER-SIGNATURE: PROCESSED-BY-{model_tag}\n")
        logger.info(f"Isolated verification check signature written to sidecar track file: {signature_path}")
        
        duration = time.time() - start_time
        summary_md = self.generate_markdown_summary(df_out, duration)
        
        # Direct markdown text outputs to target documents folder configuration
        abs_doc_dir = self.paths.documents_dir
        md_path = os.path.join(abs_doc_dir, "dd_parsing_summary.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(summary_md)
            
        logger.info(f"Analytics workflow report written safely to documents workspace at: {md_path}")
