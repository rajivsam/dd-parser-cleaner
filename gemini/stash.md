# 📑 Unified Project Session Stash: dd-parser-cleaner

## 📑 Unified Project Session Stash: dd-parser-cleaner

## 🛠️ Active Project State

* Workspace Title: `dd-parser-cleaner`
* Core Strategy: Human-in-the-Loop (HITL) Workflow via KMDS Framework. The parser creates a rapid Provisional Template to eliminate 90% of spreadsheet busywork, designed for quick user verification before downstream consumption.
* Classification Engine: Local LLM Domain Clustering (`llama3.2` via Ollama) paired with character-level n-gram frequency cosine similarity fallbacks. Includes an explicit Prefix-Stripping Pre-Processor to catch shorthand variations (e.g., `Borr`, `Bank`, `Lend`, `Loc`).
* Feature Pipeline Routing: Dynamic, checklist-driven generation of capability boolean columns (e.g., `is_geographic`, `is_medical`) based on configuration rules applied to stripped attribute names.
* Testing Status: Both structural pipeline suites (`test_parser.py` and `test_cleaner.py`) are fully resolved, aligned with the authoritative configuration schema, and marked PASSED.

## 📂 Production Workspace Architecture

```text
/home/rajiv/programming/dd_parser_cleaner/
├── config.yaml           <-- Authoritative single source of truth for runtime configs
├── src/
│   ├── path_coordinator.py <-- Centralised path router; enforces linear data pipeline contracts
│   ├── dd_parser/
│   │   ├── __init__.py
│   │   └── core.py       <-- Local LLM domain discovery, prefix-stripping, & tag engine
│   └── dd_cleaner/
│       ├── __init__.py
│       └── engine.py     <-- Vectorised pandas title-casing & zero-padding case protector
├── tests/
│   ├── conftest.py       <-- Automated session fixture; script-recreated tests/config.yaml
│   ├── test_parser.py    <-- Case preservation & LLM category validation checks
│   └── test_cleaner.py   <-- End-to-end data scrubbing & case lookup restoration checks
└── pyproject.toml        <-- Active project environment workspace boundaries (uv run pytest)
```

## ⚙️ Authoritative Contract Specifications

## 1. Unified Configuration Schema (`config.yaml`)

```yaml
batch_size: 10
documents_dir: documents
model_name: llama3.2
system_prompt: You are a precise data engineering assistant. Respond strictly in JSON.
temperature: 0.0

parser:
  data_dictionary_file: sba_dd.csv
  csv_target_column_index: 0
  dd_parser_output_dir: dd_analysis_results
  output_filename: sba_analysis_results.csv
  entity_tagging:
    - geographic
  overrides:
    LocationID:
      provisional_entity_assignment: "Lender"
      is_geographic: false

cleaner:
  raw_dataset_file: sba_loans_raw.csv
  clean_output_filename: sba_loans_clean.csv
  dd_cleaner_output_dir: dd_cleaner_results
```

## 2. Linear Pipeline Folder Rules (Enforced by `PathCoordinator`)

* Inputs: Data Dictionary must reside inside `{$working_dir}/data_dictionary/{$data_dictionary_file}`. Raw heavy files must reside inside `{$working_dir}/data/{$raw_dataset_file}`.
* Parser Outputs: Matrix result tables are cleanly nested inside `{$working_dir}/data_dictionary/{dd_parser_output_dir}/{$output_filename}`, generating a `.signature` sidecar file alongside.
* Cleaner Outputs: Casing-restored operational tables write cleanly to `{$working_dir}/{$dd_cleaner_output_dir}/{$clean_output_filename}`.

---

## 🎯 Next Steps Checklist (For Tomorrow)

* Implement User Interface Loop: Create an interactive human-in-the-loop CLI workflow to display low-confidence models/heuristics tags and allow quick interactive editing of the provisional matrix before committing to `parser.overrides`.
* Scale & Volume Stress Test: Write a script to synthesize a massive 5,000+ column payload dataset to check for vector processing drift and memory efficiency under load.
* Extended Custom Domain Anchors: Test edge-case dataset mappings on custom financial ledger templates or medical payload definitions.

/init please

## 🛠️ Active Project State

* **Workspace Title**: `dd-parser-cleaner`
* **Core Strategy**: Human-in-the-Loop (HITL) Workflow via KMDS Framework. The parser creates a rapid **Provisional Template** to eliminate 90% of spreadsheet busywork, designed for quick user verification before downstream consumption.
* **Classification Engine**: Pure Vector Embedding Centroid Space with confidence boundary thresholding (Deterministic coordinate math).
* **Execution Benchmark**: ~0.67 Seconds for a 40-element file matrix (~60x faster performance optimization over token generation).
* **Testing Status**: Both structural pipeline suites (`test_parser.py` and `test_cleaner.py`) are fully resolved and marked **PASSED**.

## 📂 Production Workspace Architecture

```text
/home/rajiv/programming/dd_parser_cleaner/
├── src/
│   ├── dd_parser/
│   │   └── core.py       <-- Pure mathematical vector decomposition & centroid engine
│   └── dd_cleaner/
│       └── engine.py     <-- Vectorized pandas title-casing and zero-padding scrapper
├── tests/
│   ├── test_parser.py    <-- Schema tracking & case-preservation verification check
│   └── test_cleaner.py   <-- End-to-end dynamic state transformation loop check
└── pyproject.toml        <-- Active project environment workspace boundaries
```

## 🎯 Next Steps Checklist (For Tomorrow)

- [ ] Implement user-facing interface loop to easily allow quick revision of the provisional matrix.
- [ ] Check parsing stability on a multi-thousand column production raw payload dataset.
- [ ] Extend semantic anchors to test custom domain pivots (e.g., Medical or Financial Ledger sets).
