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

logger = logging.getLogger("dd_parser")

class LocalEntityClassifier:
    def __init__(self):
        self.working_dir: str = ""
        self.config: Dict[Any, Any] = {}

    def set_working_config(self, working_dir: str, config_path: str):
        abs_config_path = os.path.abspath(config_path)
        if not os.path.exists(abs_config_path):
            raise FileNotFoundError(f"Configuration file not found at: {abs_config_path}")
            
        with open(abs_config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        if not os.path.isdir(working_dir):
            raise FileNotFoundError(f"Target data directory not found: {os.path.abspath(working_dir)}")
        self.working_dir = os.path.abspath(working_dir)
        
        raw_output_dir = self.config.get('dd_parser_output_dir', 'dd_analysis_results')
        abs_output_dir = os.path.isabs(raw_output_dir) and raw_output_dir or os.path.abspath(os.path.join(self.working_dir, raw_output_dir))
        os.makedirs(abs_output_dir, exist_ok=True)
        
        log_file_path = os.path.join(abs_output_dir, "parser_run.log")
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(file_handler)

        logger.info("Context Initialized with Hybrid Processing Configuration.")
        logger.info(f"Loaded Config: {abs_config_path} | Tracking Log: {log_file_path}")

    def extract_attributes(self, file_path: str, csv_idx: int = 0) -> List[str]:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        if ext == '.csv':
            return pd.read_csv(file_path).iloc[:, csv_idx].dropna().astype(str).tolist()
        elif ext == '.pdf':
            return [line.strip() for page in PdfReader(file_path).pages for line in page.extract_text().split('\n') if line.strip()]
        elif ext in ['.md', '.markdown']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        raise ValueError(f"Unsupported format: {ext}")

    def analyze_batch(self, attributes: List[str]) -> List[AttributeAnalysis]:
        prompt = f"""
        Analyze the following data dictionary attributes. 
        
        ### EXAMPLES OF EXCELLENT PERFORMANCE
        Input: ["BorrCity", "BankStreet", "GrossApproval", "SoldSecMrktInd"]
        Output Schema Map:
        {{
            "analysis": [
                {{"attribute_name": "BorrCity", "provisional_entity": "Borrower", "is_geographical": true, "related_entity": "Borrower", "provisional_python_type": "str"}},
                {{"attribute_name": "BankStreet", "provisional_entity": "Bank", "is_geographical": true, "related_entity": "Bank", "provisional_python_type": "str"}},
                {{"attribute_name": "GrossApproval", "provisional_entity": "Loan", "is_geographical": false, "related_entity": null, "provisional_python_type": "float"}},
                {{"attribute_name": "SoldSecMrktInd", "provisional_entity": "Loan", "is_geographical": false, "related_entity": null, "provisional_python_type": "bool"}}
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
            options={"temperature": self.config.get('temperature', 0.0)},
            format=BatchAnalysisResponse.model_json_schema()
        )
        return BatchAnalysisResponse(**json.loads(response['message']['content'])).analysis

    def post_process_cleaner(self, analysis_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned_records = []
        for item in analysis_list:
            data = item.copy()
            attr = data['attribute_name']
        
            if attr.startswith('Borr'):
                data['provisional_entity'] = 'Borrower'
                if data['is_geographical']: data['related_entity'] = 'Borrower'
            elif attr.startswith('Bank'):
                data['provisional_entity'] = 'Bank'
                if attr in ['BankStreet', 'BankCity', 'BankState', 'BankZip']:
                    data['is_geographical'] = True
                    data['related_entity'] = 'Bank'
            elif attr.startswith('Project'):
                data['provisional_entity'] = 'Project'
                if attr in ['ProjectCounty', 'ProjectState']:
                    data['is_geographical'] = True
                    data['related_entity'] = 'Project'
            elif 'Approval' in attr or 'Disbursement' in attr or attr in ['Program', 'Subprogram']:
                data['provisional_entity'] = 'Loan'
            elif attr.startswith('SBA'):
                data['provisional_entity'] = 'SBA'
                if data['is_geographical']: data['related_entity'] = 'SBA'
                
            if attr.endswith('Ind') or 'Indicator' in attr:
                data['provisional_python_type'] = 'bool'
                
            if not data['is_geographical']:
                data['related_entity'] = ""
            
            cleaned_records.append(data)
        return cleaned_records

    def generate_parsing_markdown_summary(self, final_results: List[Dict[str, Any]], base_project_dir: str):
        """Compiles structural data profiles and metadata metrics as a clean Markdown specification file."""
        df = pd.DataFrame(final_results)
        doc_dir_name = self.config.get('documents_dir', 'documents')
        abs_doc_dir = os.path.abspath(os.path.join(base_project_dir, doc_dir_name))
        os.makedirs(abs_doc_dir, exist_ok=True)
        
        report_path = os.path.join(abs_doc_dir, "dd_parsing_summary.md")
        entity_counts = df['provisional_entity'].value_counts()
        total_attributes = len(df)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 📑 KMDS Data Helper: Data Dictionary Parsing Summary\n\n")
            f.write(f"**Total Tracked Attributes:** {total_attributes}  \n")
            f.write(f"**Unique Detected Entities:** {len(entity_counts)}\n\n")
            
            f.write("## 🏗️ Entity Size & Distribution Profile\n")
            f.write("| Detected Entity Node | Number of Attributes (Size) |\n")
            f.write("| :--- | :--- |\n")
            for ent, count in entity_counts.items():
                f.write(f"| {ent} | {count} |\n")
            f.write("\n")
            
            f.write("## 🎛️ Attribute Structural Categories\n")
            categorical_df = df[df['provisional_python_type'] == 'bool']
            numerical_df = df[df['provisional_python_type'].isin(['int', 'float'])]
            semantic_df = df[~df['provisional_python_type'].isin(['bool', 'int', 'float'])]
            
            f.write(f"### 📊 Categorical Fields (Total: {len(categorical_df)})\n")
            for _, row in categorical_df.iterrows():
                f.write(f"- `{row['attribute_name']}` ({row['provisional_python_type']}) $\rightarrow$ Node: **{row['provisional_entity']}**\n")
            f.write("\n")
            
            f.write(f"### 🔢 Numerical Fields (Total: {len(numerical_df)})\n")
            for _, row in numerical_df.iterrows():
                f.write(f"- `{row['attribute_name']}` ({row['provisional_python_type']}) $\rightarrow$ Node: **{row['provisional_entity']}**\n")
            f.write("\n")
            
            f.write(f"### 🧠 Semantic Attributes Grouped By Parent Class (Total: {len(semantic_df)})\n")
            grouped_semantic = semantic_df.groupby('provisional_entity')
            for ent_group, group_df in grouped_semantic:
                f.write(f"#### Entity Category: `{ent_group}`\n")
                for _, row in group_df.iterrows():
                    geo_suffix = row['is_geographical'] and f" [GEO Linked: {row['related_entity']}]" or ""
                    f.write(f"  - `{row['attribute_name']}` ({row['provisional_python_type']}){geo_suffix}\n")
                f.write("\n")
                
        logger.info(f"Generated parser metadata documentation report saved to: {report_path}")

    def process(self):
        files_to_process = self.config.get('files', [])
        if not files_to_process: return

        raw_output_dir = self.config.get('dd_parser_output_dir', 'dd_analysis_results')
        abs_output_dir = os.path.isabs(raw_output_dir) and raw_output_dir or os.path.abspath(os.path.join(self.working_dir, raw_output_dir))
        
        batch_size, csv_col_idx = self.config.get('batch_size', 10), self.config.get('csv_target_column_index', 0)
        config_filename = self.config.get('output_filename')

        # Extract base project root for kmds-data-helper structure alignment
        base_project_dir = os.path.abspath(os.path.join(self.working_dir, ".."))

        for filepath in files_to_process:
            input_file_path = os.path.isabs(filepath) and filepath or os.path.abspath(os.path.join(self.working_dir, filepath))
            if not os.path.exists(input_file_path): continue
                
            filename = os.path.basename(input_file_path)
            try:
                raw_attributes = self.extract_attributes(input_file_path, csv_col_idx)
                logger.info(f"Extracted {len(raw_attributes)} attributes from {filename}")
            except Exception as e:
                logger.exception(f"Read failure on {filename}: {e}")
                continue

            final_results = []
            for i in range(0, len(raw_attributes), batch_size):
                batch = raw_attributes[i:i+batch_size]
                start_time = time.perf_counter()
                try:
                    batch_output = self.analyze_batch(batch)
                    batch_dicts = [item.model_dump() for item in batch_output]
                    cleaned_batch = self.post_process_cleaner(batch_dicts)
                    final_results.extend(cleaned_batch)
                    logger.info(f" Batch run {i} verified in {time.perf_counter() - start_time:.2f}s")
                except Exception as e:
                    logger.error(f" Batch crash at element index {i}: {e}")

            if final_results:
                if config_filename and len(files_to_process) == 1:
                    out_filename = config_filename
                else:
                    base_name, _ = os.path.splitext(filename)
                    out_filename = f"mapped_{base_name}.csv"
                
                output_csv_path = os.path.join(abs_output_dir, out_filename)
                
                preamble = f"# DD-PARSER-SIGNATURE: PROCESSED-BY-{self.config.get('model_name', 'llama3.2').upper()}\n"
                with open(output_csv_path, 'w', encoding='utf-8') as f:
                    f.write(preamble)
                    
                pd.DataFrame(final_results).to_csv(output_csv_path, mode='a', index=False)
                logger.info(f"Finished tracking {filename}. Saved verified matrix map to: {output_csv_path}")
                
                # Dynamic Markdown Generation Task Trigger
                self.generate_parsing_markdown_summary(final_results, base_project_dir)
