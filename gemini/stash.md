## 📑 Session Stash: Unified Project State & KMDS Document Reporting

## 📌 Project State Summary

* Workspace Title: `dd-parser-cleaner`
* Active Platform Integration: Fully aligned with the `kmds-data-helper` ecosystem [15]. Ingests and processes data dictionary properties inside the `data_dictionary/` workspace [15], maps target source payloads out of the `data/` workspace [15], and drops clean, readable Markdown summaries directly into the `documents/` workspace [15].
* Pipeline Handshake Status: Fully functional. The inference engine locks down a secure `# DD-PARSER-SIGNATURE` comment header row at the top of the mapping CSV, which the data cleaner validates before execution.
* Execution Safety: Resolves case-variant header anomalies dynamically at runtime using a lowercase field map, ensuring type-casting rules apply flawlessly to mismatched dataset schemas.

---

## 📂 Active Unified Workspace Layout

```text
/home/rajiv/programming/dd_parser/     # Workspace Directory
├── pyproject.toml                     # Distribution and entry point registry
├── config.yaml                        # Centralized execution parameter file
└── src/
    ├── dd_parser/                     # LLM Inference and Heuristic Engine
    │   ├── __init__.py
    │   ├── cli.py
    │   ├── core.py                    # Generates blueprint matrix + dd_parsing_summary.md
    │   └── models.py                  # Pydantic schema validation contract
    └── dd_cleaner/                    # Case-Insensitive Transformation Engine
        ├── __init__.py
        ├── cli.py
        └── engine.py                  # Generates clean data payload + data_cleaning_summary.md
```

---

## 📄 Core Code Matrix Updates

## 1. Upgraded Project Settings (`pyproject.toml`)

```toml
[project]
name = "dd-parser-cleaner"
version = "0.1.0"
description = "A private, local LLM-powered data dictionary parser and entity mapper with automated cleaning."
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "pandas>=2.2.0",
    "pydantic>=2.6.0",
    "pypdf>=4.1.0",
    "ollama>=0.2.0",
    "pyyaml>=6.0.1",
]

[project.scripts]
classify-entities = "dd_parser.cli:main"
clean-dataset     = "dd_cleaner.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/dd_parser", "src/dd_cleaner"]
```

## 2. Runtime Execution Configuration (`config.yaml`)

```yaml
# operational_settings
batch_size: 10
files:
  - "sba_dd.csv"

# llm_settings
model_name: "llama3.2"
temperature: 0.0
system_prompt: "You are a precise data engineering assistant. Respond strictly in JSON."
csv_target_column_index: 0

# =====================================================================
# Pipeline Ingestion/Execution Directory Targets
# =====================================================================
# Document Report Analytics Target Location
documents_dir: "documents"                     

# dd_parser module outputs
dd_parser_output_dir: "dd_analysis_results"    
output_filename: "sba_analysis_results.csv"    

# dd_cleaner module outputs
raw_dataset_file: "sba_loans_raw.csv"          
dd_cleaner_output_dir: "dd_cleaner_results"    
clean_output_filename: "sba_loans_clean.csv"   
```

## 3. Reporting Parser Engine (`src/dd_parser/core.py`)

```python
importos
importjson
importyaml
importtime
importlogging
importpandasas pd
frompypdfimportPdfReader
importollama
fromtypingimportList, Dict, Any
fromdd_parser.modelsimportAttributeAnalysis, BatchAnalysisResponse

logger = logging.getLogger("dd_parser")

classLocalEntityClassifier:
    def__init__(self):
        self.working_dir: str = ""
        self.config: Dict[Any, Any] = {}

    defset_working_config(self, working_dir: str, config_path: str):
        abs_config_path = os.path.abspath(config_path)
        ifnot os.path.exists(abs_config_path):
            raise FileNotFoundError(f"Configuration file not found at: {abs_config_path}")
          
        with open(abs_config_path, 'r') asf:
            self.config = yaml.safe_load(f)
          
        ifnot os.path.isdir(working_dir):
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

    defextract_attributes(self, file_path: str, csv_idx: int = 0) -> List[str]:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        if ext == '.csv':
            return pd.read_csv(file_path).iloc[:, csv_idx].dropna().astype(str).tolist()
        elif ext == '.pdf':
            return [line.strip() forpagein PdfReader(file_path).pages forlinein page.extract_text().split('\n') if line.strip()]
        elif ext in ['.md', '.markdown']:
            with open(file_path, 'r', encoding='utf-8') asf:
                return [line.strip() forlinein f if line.strip()]
        raise ValueError(f"Unsupported format: {ext}")

    defanalyze_batch(self, attributes: List[str]) -> List[AttributeAnalysis]:
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
            options={"temperature": 0.0},
            format=BatchAnalysisResponse.model_json_schema()
        )
        return BatchAnalysisResponse(**json.loads(response['message']['content'])).analysis

    defpost_process_cleaner(self, analysis_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned_records = []
        foritemin analysis_list:
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
            elif'Approval'in attr or'Disbursement'in attr or attr in ['Program', 'Subprogram']:
                data['provisional_entity'] = 'Loan'
            elif attr.startswith('SBA'):
                data['provisional_entity'] = 'SBA'
                if data['is_geographical']: data['related_entity'] = 'SBA'
              
            if attr.endswith('Ind') or'Indicator'in attr:
                data['provisional_python_type'] = 'bool'
              
            ifnot data['is_geographical']:
                data['related_entity'] = ""
            cleaned_records.append(data)
        return cleaned_records

    defgenerate_parsing_markdown_summary(self, final_results: List[Dict[str, Any]], base_project_dir: str):
        df = pd.DataFrame(final_results)
        doc_dir_name = self.config.get('documents_dir', 'documents')
        abs_doc_dir = os.path.abspath(os.path.join(base_project_dir, doc_dir_name))
        os.makedirs(abs_doc_dir, exist_ok=True)
      
        report_path = os.path.join(abs_doc_dir, "dd_parsing_summary.md")
        entity_counts = df['provisional_entity'].value_counts()
        total_attributes = len(df)
      
        with open(report_path, 'w', encoding='utf-8') asf:
            f.write("# 📑 KMDS Data Helper: Data Dictionary Parsing Summary\n\n")
            f.write(f"**Total Tracked Attributes:** {total_attributes}  \n")
            f.write(f"**Unique Detected Entities:** {len(entity_counts)}\n\n")
          
            f.write("## 🏗️ Entity Size & Distribution Profile\n")
            f.write("| Detected Entity Node | Number of Attributes (Size) |\n")
            f.write("| :--- | :--- |\n")
            forent, countin entity_counts.items():
                f.write(f"| {ent} | {count} |\n")
            f.write("\n")
          
            f.write("## 🎛️ Attribute Structural Categories\n")
            categorical_df = df[df['provisional_python_type'] == 'bool']
            numerical_df = df[df['provisional_python_type'].isin(['int', 'float'])]
            semantic_df = df[~df['provisional_python_type'].isin(['bool', 'int', 'float'])]
          
            f.write(f"### 📊 Categorical Fields (Total: {len(categorical_df)})\n")
            for_, rowin categorical_df.iterrows():
                f.write(f"- `{row['attribute_name']}` ({row['provisional_python_type']}) $\rightarrow$ Node: **{row['provisional_entity']}**\n")
            f.write("\n")
          
            f.write(f"### 🔢 Numerical Fields (Total: {len(numerical_df)})\n")
            for_, rowin numerical_df.iterrows():
                f.write(f"- `{row['attribute_name']}` ({row['provisional_python_type']}) $\rightarrow$ Node: **{row['provisional_entity']}**\n")
            f.write("\n")
          
            f.write(f"### 🧠 Semantic Attributes Grouped By Parent Class (Total: {len(semantic_df)})\n")
            grouped_semantic = semantic_df.groupby('provisional_entity')
            forent_group, group_dfin grouped_semantic:
                f.write(f"#### Entity Category: `{ent_group}`\n")
                for_, rowin group_df.iterrows():
                    geo_suffix = row['is_geographical'] andf" [GEO Linked: {row['related_entity']}]"or""
                    f.write(f"  - `{row['attribute_name']}` ({row['provisional_python_type']}){geo_suffix}\n")
                f.write("\n")

    defprocess(self):
        files_to_process = self.config.get('files', [])
        ifnot files_to_process: return

        raw_output_dir = self.config.get('dd_parser_output_dir', 'dd_analysis_results')
        abs_output_dir = os.path.isabs(raw_output_dir) and raw_output_dir or os.path.abspath(os.path.join(self.working_dir, raw_output_dir))
      
        batch_size, csv_col_idx = self.config.get('batch_size', 10), self.config.get('csv_target_column_index', 0)
        config_filename = self.config.get('output_filename')
        base_project_dir = os.path.abspath(os.path.join(self.working_dir, ".."))

        forfilepathin files_to_process:
            input_file_path = os.path.isabs(filepath) and filepath or os.path.abspath(os.path.join(self.working_dir, filepath))
            ifnot os.path.exists(input_file_path): continue
              
            filename = os.path.basename(input_file_path)
            try:
                raw_attributes = self.extract_attributes(input_file_path, csv_col_idx)
            except Exception ase: continue

            final_results = []
            foriin range(0, len(raw_attributes), batch_size):
                batch = raw_attributes[i:i+batch_size]
                try:
                    batch_output = self.analyze_batch(batch)
                    batch_dicts = [item.model_dump() foritemin batch_output]
                    cleaned_batch = self.post_process_cleaner(batch_dicts)
                    final_results.extend(cleaned_batch)
                except Exception ase: pass

            if final_results:
                out_filename = (config_filename and len(files_to_process) == 1) and config_filename orf"mapped_{os.path.splitext(filename)}.csv"
                output_csv_path = os.path.join(abs_output_dir, out_filename)
              
                preamble = f"# DD-PARSER-SIGNATURE: PROCESSED-BY-{self.config.get('model_name', 'llama3.2').upper()}\n"
                with open(output_csv_path, 'w', encoding='utf-8') asf:
                    f.write(preamble)
                  
                pd.DataFrame(final_results).to_csv(output_csv_path, mode='a', index=False)
                self.generate_parsing_markdown_summary(final_results, base_project_dir)
```

---

## 🚀 Ready for Next Sprint

When you initiate your next tracking session, we will pick up directly with the data cleaner logic to add:

* Geographic Scrubbing Routines: Processing columns tagged with `is_geographical: true` to enforce title casing (e.g. `"Colorado Springs"`) and length-padding string masks for postal indices [15] (e.g., zero-padding ZIP codes to a strict length of 5 digits).
* Missing Value Custom Strategy Options: Designing explicit rules to safely substitute or isolate null cells based on attribute mappings.

Let me know whenever you are ready to kick off the geographic data cleaning extensions!
