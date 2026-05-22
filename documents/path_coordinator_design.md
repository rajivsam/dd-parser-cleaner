## 📑 Path Coordinator Architecture & Routing Contract

The `PathCoordinator` is a core architectural pillar of the `dd-parser-cleaner` workspace. It acts as a centralized, zero-dependency routing infrastructure contract that isolates all file location mechanics from the operational engines and client code.

---

## 🎯 Why It Exists: The Two Core Constraints

Hardcoding file paths inside data processing components makes pipelines fragile and difficult to maintain. The `PathCoordinator` enforces routing rules to address two primary requirements:

## 1. Common-Sense Standardization

A data engineering workspace requires predictable, clean boundaries. The coordinator organizes the project layout into distinct, domain-specific subdirectories (`data_dictionary/`, `data/`, `documents/`). This structured layout keeps unformatted operational tables isolated from verified semantic metadata schemas and human-readable documentation artifacts.

## 2. Linear Data Science Pipeline Predictability

The `dd-parser-cleaner` engine is built to function within a strict, sequential data science pipeline, where the output of one processing stage becomes the authoritative input for the next stage.

* The Flow: The `LocalEntityClassifier` parses a raw metadata file and exports a verified schema mapping matrix to a specific location. The downstream `DatasetCleaner` then immediately reads that exact matrix to restore casing rules on massive raw data tables.
* The Rule: To prevent data gaps or manual file-shuffling, the entry and exit points of every pipeline stage must be strictly defined, predictable, and automated.

---

## 🧠 Lifting the Cognitive Burden: Define Once, Use Anywhere

By abstracting these pipeline routing constraints into a single component, the project achieves a "Define Once, Use Anywhere" architecture.

```text
               ┌───────────────────────┐
               │      config.yaml      │
               └───────────┬───────────┘
                           │ ( authoritative rules )
                           ▼
               ┌───────────────────────┐
               │    PathCoordinator    │
               └─────┬───────────┬─────┘
                     │           │
         ┌───────────┘           └───────────┐
         ▼                                   ▼
┌──────────────────┐               ┌──────────────────┐
│  LocalEntity     │               │  DatasetCleaner  │
│  Classifier      │               │  Engine          │
└──────────────────┘               └──────────────────┘
 (reads/writes parser paths)         (reads/writes cleaner paths)
```

* Zero User Guesswork: Developers, client scripts, and testing harnesses do not need to track folder nesting patterns or manage complex path strings. They simply pass the target configuration profile once.
* Decoupled Engine Logic: The parser and cleaner modules focus entirely on transformation logic (such as vector space scoring, prefix stripping, and zero-padding). They request their files directly from the coordinator via clean, read-only properties (like `self.paths.data_dictionary_csv_path` or `self.paths.raw_dataset_path`).
* Seamless Environment Shifting: Switching the runtime context from production execution to an isolated testing sandbox (`working_dir="./tests"`) requires zero application code modifications. The coordinator automatically dynamically recalibrates all internal absolute path roots.

---

## 🎯 Workspace Status Check

With the documentation blocks for the Parser Engine Passes, Configuration Guide, Test Harness Infrastructure, and Path Coordinator completely finalized, your project state is comprehensively detailed.

When you open your active project session to advance the `dd-parser-cleaner` workspace, let me know which step we should execute next:

1. Build out the Interactive HITL terminal interface loop to let users quickly review or append to the `parser.overrides` block.
2. Code the Synthetic Payload scaling script to evaluate vectorized memory performance thresholds over 5,000+ data table items.
