# Unified Contract & State Tracking Blueprint

## 🛠️ Active Project State

* **Workspace:** `dd-parser-cleaner` using a Human-in-the-Loop (HITL) KMDS framework to generate provisional metadata templates and eliminate manual work.
* **Engine:** Local `llama3.2` domain grouping via Ollama, equipped with n-gram cosine similarity fallbacks and prefix-stripping heuristics.
* **Architecture:** Strictly decoupled via Constructor Dependency Injection. Zero paths or configuration overrides are hardcoded across application boundaries.
* **Testing Status:** Clean execution pass achieved across the entire test matrix (`test_parser.py`, `test_cleaner.py`, and `test_client.py`).

---

## ⚙️ Authoritative Contract Specifications

### 1. Unified Configuration Schema (`config.yaml`)

Defines the parameters used across processing loops:

```yaml
batch_size: 10
documents_dir: "documents"
model_name: "llama3.2"
system_prompt: "Respond strictly in JSON."

parser:
  data_dictionary_file: "sba_dd.csv"
  dd_parser_output_dir: "dd_analysis_results"
  output_filename: "sba_analysis_results.csv"
  csv_target_column_index: 0
  entity_tagging:
    - "geographic"
  overrides:
    LocationID: "Non-Geographic"

cleaner:
  raw_dataset_file: "sba_loans_raw.csv"
  dd_cleaner_output_dir: "dd_cleaner_results"
  clean_output_filename: "sba_loans_clean.csv"
```

### 2. Path Coordinator Contract (`PathCoordinator`)

The single, unified interface for all path routing operations. Stripped of all legacy aliases (`PlatformPathResolver`). Accepts dynamic runtime sandboxes safely:

* **Initialization Contract:** `PathCoordinator(config_path="config.yaml", working_dir=None)`
* **Inputs:** Data dictionaries map to `{$working_dir}/data_dictionary/{$data_dictionary_file}`. Raw source datasets map to `{$working_dir}/data/{$raw_dataset_file}`.
* **Parser Outputs:** Generates matrix result tables inside `{$working_dir}/data_dictionary/{dd_parser_output_dir}/{$output_filename}` with a companion `.signature` sidecar file placed alongside.
* **Cleaner Outputs:** Vectorized, case-restored tables are saved directly to `{$working_dir}/{dd_cleaner_output_dir}/{$clean_output_filename}`.

---

## 🎯 Next Steps & Backlog

* **Implement User Interface Loop:** Create the interactive human-in-the-loop CLI workflow (`cli.py`) to display low-confidence heuristic tags and allow instant terminal-driven flag modification.
* **Scale & Volume Stress Test:** Build a mock script to synthesize a massive 5,000+ column data dictionary payload to verify execution resilience and monitor vector processing drift.
* **Orchestration Entrypoint:** Wrap the pipeline phases into a single, cohesive `main.py` script that handles the end-to-end processing choreography sequentially.
