# 📖 User Guide: dd-parser-cleaner

## 📑 Overview
This system is a modular data engineering framework designed to bridge the gap between messy data dictionaries and clean, production-ready datasets. It uses local LLMs (Llama 3.2) to classify metadata and deterministic vectorized rules to transform data.

## 🔎 Component 1: The Parser (`classify-entities`)
The parser analyzes your Data Dictionary to create a structured mapping matrix.

### Grounded Inference
Unlike standard LLM parsers, this engine performs **Grounded Inference**. It profiles a sample of your raw dataset to generate physical metrics (cardinality, samples, types) and injects this context into the LLM prompts. This ensures the LLM doesn't label a column as "City" if it physically contains integers.

### Post-Processing & Validation
1. **Prefix Discovery**: Algorithmic detection of prefixes (e.g., `borr_`, `bank_`).
2. **Heuristic Stripping**: Strips prefixes to validate semantic tags (e.g., `borr_zip` -> `zip` -> `is_geographic`).
3. **authoritative Overrides**: Absolute manual control via `config.yaml`.
4. **Bridge Integrity (Orphan Quarantine)**: Automatically reconciles the Dictionary against Raw Headers using three buckets:
    * **Bucket A (Operational)**: Valid matches sent to the cleaner.
    * **Bucket B (Orphans)**: Definitions with no matching data column. These are **stripped** from the CSV matrix and flagged as "Critical Schema Mismatches" in the report.
    * **Bucket C (Ghosts)**: Raw data columns with no dictionary definition.

This prevents the cleaner from attempting to process non-existent data.

## 🧼 Component 2: The Cleaner (`clean-dataset`)
The cleaner uses the parser's output to scrub and normalize your operational data.

### The Quarantine Workflow
Before any transformations, the cleaner scans for **Mixed Values**. 
* **Detection**: Uses `pandas` to find columns containing multiple data types (e.g., a mix of `float` and `str`).
* **Isolation**: Records deviating from the dominant type are moved to a `quarantine/` directory.
* **Safety**: This prevents cleaning rules (like title-casing) from crashing or corrupting non-string data.

### Data Profiling
Every cleaning run generates a `profiling_report.md`. This summarizes:
* Total record counts.
* Missingness (Null) percentages per column.
* Warnings for high-missingness alerts.

## 🛠️ Configuration & Routing
All paths and rules are managed in `config.yaml`.

### Path Coordination
The `PathCoordinator` ensures zero-hardcoding. All inputs and outputs are resolved relative to the `--workspace` flag provided at the CLI.
* **Data Dictionary**: `data_dictionary/`
* **Raw/Clean Data**: `data/`
* **Reports/Logs**: `documents/`

## 🧪 Running Tests
The system is fully covered by decoupled integration tests:
```bash
uv run pytest tests/test_parser.py   # Validates LLM logic
uv run pytest tests/test_cleaner.py  # Validates scrubbing and quarantine logic
```

---
*Next Session: Design interaction for missing value handling strategies.*