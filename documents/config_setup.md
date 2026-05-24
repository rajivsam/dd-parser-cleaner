## 📑 Configuration Guide: `config.yaml` Reference Blueprint

The `config.yaml` file serves as the authoritative single source of truth for the entire `dd-parser-cleaner` workspace. By centralizing infrastructure definitions, path parameters, and business rules, it ensures that no file locations or structural parameters are hardcoded anywhere inside the application or test suites.

The repository includes a production template config file (`config.yaml.template` or equivalent) that maps out a complete, syntax-validated blueprint ready for deployment. [1]

---

## 🏗️ The 3 Major Configuration Sections

The file is split into three core blocks to logically decouple shared global system layers from individual runtime component boundaries.

```text
 ┌────────────────────────────────────────────────────────┐
 │ 🌐 GLOBAL INFRASTRUCTURE PARAMETERS                    │
 │    (LLM Selection, Inference Settings, Directories)     │
 ├────────────────────────────────────────────────────────┤
 │ 🔎 PARSER MODULE CONFIGURATIONS (Sub-Block)            │
 │    (Data Dictionary Ingest, Tagging Checklist, HITL)   │
 ├────────────────────────────────────────────────────────┤
 │ 🧼 CLEANER MODULE CONFIGURATIONS (Sub-Block)           │
 │    (Operational Table Ingest, Scrubbing Destinations)  │
 └────────────────────────────────────────────────────────┘
```

---

## 🛠️ Detailed Functional Breakdown

## 1. Global Infrastructure Parameters (Root Level)

This section provisions shared environment resources and configures the local inference orchestrator engine.

* `model_name`: Sets the target local LLM context profile (e.g., `llama3.2`) managed via your local Ollama runtime server.
* `system_prompt` & `temperature`: Sets deterministic parameters (`temperature: 0.0`) to force strict JSON layouts and prevent vector coordinate drift during parsing.
* `documents_dir`: The global workspace folder where markdown analytics reports and human-in-the-loop diagnostic summaries are generated.

## 2. Parser Module Configurations (`parser:`)

This sub-block isolates configuration metadata mapping parameters, target feature trackers, and human-in-the-loop override parameters.

* `data_dictionary_file`: Defines the source metadata file (e.g., `sba_dd.csv`) containing attribute names and descriptive definitions.
* `csv_target_column_index`: Explicit index pinning where primary column/attribute strings live to handle headless spreadsheets or fragmented PDF scraper matrices cleanly.
* `dd_parser_output_dir` & `output_filename`: Destination configurations telling the path coordinator to nest computed provisional template files directly inside the `data_dictionary/` namespace directory footprint.
* `parser_provisional_assingnment_dir`: Target directory within `documents/` for the human-readable Markdown report.
* `parser_provisional_assingnment_filename`: The filename for the Markdown entity assignment summary.
* `entity_tagging`: A dynamic registry list of capability feature flags. The parser loops over this checklist to append corresponding downstream feature-routing boolean columns (e.g., `is_geographic`).
* `overrides`: An absolute authoritative escape hatch. Hardcoding specific attributes here forces the engine to bypass LLM inference and heuristic rules entirely for those keys, instantly stamping your specified entity mappings and capability values into the output matrix.

## 3. Cleaner Module Configurations (`cleaner:`)

This sub-block controls settings for operational data scrubbing transformations over large database files.

* `raw_dataset_file`: Points to the heavy, unformatted production payload target table (e.g., `sba_loans_raw.csv`) residing inside your local workspace `data/` folder directory.
* `clean_output_filename` & `dd_cleaner_output_dir`: Controls the name and folder path destination where clean datasets are written after passing through vectorized padding and title-casing transformations.

---

## 📋 Comprehensive Reference Layout Template

Below is the authoritative structured schema syntax mirroring the template provided within the project workspace boundaries:

```yaml
# ==============================================================================
# 🌐 GLOBAL INFRASTRUCTURE PARAMETERS
# ==============================================================================
batch_size: 10
documents_dir: documents
model_name: llama3.2
system_prompt: You are a precise data engineering assistant. Respond strictly in JSON.
temperature: 0.0

# ==============================================================================
# 🔎 PARSER MODULE CONFIGURATIONS
# ==============================================================================
parser:
  data_dictionary_file: sba_dd.csv
  csv_target_column_index: 0
  dd_parser_output_dir: dd_analysis_results
  output_filename: sba_analysis_results.csv
  parser_provisional_assingnment_dir: dd_parser_results
  parser_provisional_assingnment_filename: sba_parser_provisional_assingnment.md
  
  # Capability feature pipeline registration list
  entity_tagging:
    - geographic
    - medical

  # Authoritative Human-in-the-Loop Override layer
  overrides:
    LocationID:
      provisional_entity_assignment: "Lender"
      is_geographic: false
    Program:
      provisional_entity_assignment: "SBA_Schema"
      is_geographic: true

# ==============================================================================
# 🧼 CLEANER MODULE CONFIGURATIONS
# ==============================================================================
cleaner:
  raw_dataset_file: sba_loans_raw.csv
  clean_output_filename: sba_loans_clean.csv
  dd_cleaner_output_dir: dd_cleaner_results
```

---

## 🎯 Wrap-Up Checklist

Both architectural blueprints (the parser functionality outline and the authoritative configuration resource guide) are completely synthesized and locked in line with your framework requirements.

When you log back onto the workspace tomorrow, we are perfectly set up to jump straight into active development tasks:

* UI Interface Loop: Build out a terminal interface shell to let users dynamically review, edit, or append to the `parser.overrides` configuration map directly from low-confidence model tags.
* Scale Validation Script: Build an unsupervised matrix generation tool to stress-test your vectorized memory thresholds over 5,000+ data table items.

Let me know how you would like to proceed when you open tomorrow's session!

[1] [https://butler.ptarmiganlabs.com](https://butler.ptarmiganlabs.com/docs/getting-started/setup/which-config-file/)
