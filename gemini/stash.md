## 📌 Unified Contract & State Tracking Blueprint (Stash)

## 🛠️ Active Project State

* Workspace: `dd-parser-cleaner`
* Architecture: Fully modularized and decoupled.

  * `dd_parser` split into orchestrator, llm_client, and post_processor.
  * `dd_cleaner` decoupled into `orchestrator.py` (Pipeline Manager), `rules.py` (Vectorized Transformations Engine), `null_profiler.py` (Data Profiler), and `reporter.py` (Audit Log Manager).
* State Checkpoint: N-gram domain stems are now dynamically derived at runtime by the parser, serialized into a sidecar `.signature` control matrix, and harvested by the downstream cleaner using an integrated metadata handshake. Successfully validated that the cleaner pipeline updates all target files on physical disk with today's live execution timestamps.

---

## ⚙️ Authoritative Contract Specifications

## 1. Unified Configuration Schema (`config.yaml`)

```yaml
batch_size: 10
documents_dir: documents
model_name: llama3.2
system_prompt: You are a precise data engineering assistant. Respond strictly in JSON.
temperature: 0.0

parser:
  csv_target_column_index: 0
  data_dictionary_attribute_col_name: "Field Name"
  data_dictionary_file: sba_dd.csv
  dd_parser_output_dir: dd_analysis_results
  output_filename: sba_analysis_results.csv
  entity_tagging:
    - geographic
  overrides:
    LocationID:
      is_geographic: false
      provisional_entity_assignment: Lender

cleaner:
  raw_dataset_file: sba_loans_raw.csv
  dd_cleaner_output_dir: dd_cleaner_results
  clean_output_filename: sba_loans_clean.csv
  profiling_output_dir: dd_cleaner_results
  profiling_report_filename: sba_data_profile.md
```

## 2. Verified Path Coordinator Endpoints (`path_coordinator.py`)

```python
    @property
    def cleaner_output_directory(self) -> Path:
        """OUTPUT DIR: Target directory location for clean table metrics."""
        out_dir_name = self._cleaner_config.get("dd_cleaner_output_dir", "dd_cleaner_results")
        out_dir = self.base_dir / "data" / out_dir_name
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    @property
    def clean_dataset_output_path(self) -> str:
        """OUTPUT FILE: Endpoint contract where cleaned table datasets are stored."""
        filename = self._cleaner_config.get("clean_output_filename", "sba_loans_clean.csv")
        return str(self.cleaner_output_directory / filename)
  
    @property
    def profiling_report_path(self) -> Path:
        """
        Authoritative routing endpoint for the markdown data quality profiling report.
        Maps dynamically to: {$working_dir}/documents/{$profiling_output_dir}/{$profiling_report_filename}
        """
        cleaner_cfg = self.config.get("cleaner", {})
        output_dir = cleaner_cfg.get("profiling_output_dir", "dd_cleaner_results")
        filename = cleaner_cfg.get("profiling_report_filename", "sba_data_profile.md")
      
        target_dir = Path(self.base_dir) / "documents" / output_dir
        return target_dir / filename
```

---

## 🧩 Modular System Snapshots (Decoupled Cleaner)

## 🧬 Data Quality Profiler (`src/dd_cleaner/null_profiler.py`)

Generates a pre-scrub baseline assessment matrix as a markdown file, capturing null counts and percentage distributions per column field.

## 🧼 Vectorized Rules Engine (`src/dd_cleaner/rules.py`)

Applies zero-padding to tracking codes and localized title-casing on text elements matching the dynamically harvested prefix stems (`active_prefixes`).

## 🛡️ Cleaner Orchestrator (`src/dd_cleaner/orchestrator.py`)

Coordinates reading raw tables, running the pre-scrub profile, executing rule matrices, reconciling case-sensitive headers from the dictionary output, and saving artifacts via constructor dependency injection.

## 💻 Unified Entry Points (`cli.py`)

Both modules now export unified argument parsers (`--workspace`, `--config`) reading fresh from the physical file layout paths on disk.

---

## 🎯 Resumption Backlog (Next Steps)

1. Verify Sandbox Test Harness Sync: Update assertions inside `tests/test_cleaner.py` to match the updated `PathCoordinator` destinations so that the automated suite passes cleanly.
2. Interactive Human-In-The-Loop Hook: Begin coding the interactive `cli.py` workflow allowing a user to inspect low-confidence domain classifications and dynamically write changes directly into the `parser.overrides` namespace block.

---

## 📜 Clear Acknowledgement of the Golden Rule

Understood and logged. The Golden Rule is locked in as a strict, non-negotiable operational boundary.

* Going forward, every code update will strictly follow incremental or decremental changes directly on your existing baseline classes.
* If a new feature or transformation modifies an architectural component and the exact target baseline code is not currently active in the chat history context, I will directly ask you to supply that exact file baseline before writing any modifications.

When you return for the next session, let me know if you would like to begin by synchronising the `test_cleaner.py` file to your new directory paths, or if we should commence the interactive HITL review feature!
