# dd-parser-cleaner

A lightweight framework for documenting and automating dataset preparation with AI-driven metadata discovery.

## What it does
- Builds a documented cleaning workflow for raw datasets.
- Creates structured metadata and transformation guidance for later featurization.
- Supports repeatable, deterministic dataset preparation in local environments.

## Real-world examples
For complete, real-world migration examples, see:
- SBA dataset: https://github.com/rajivsam/kmds_migration/blob/main/sba_migration/documents/sba_development_example_full_doc.md
- Olist dataset: https://github.com/rajivsam/kmds_migration/blob/main/olist_migration/documents/olist_development_example_full_doc.md

These examples show how the tool is applied to cross-sectional datasets. An example for longitudinal/panel datasets is coming soon.

## Why it matters
- Saves time by automating metadata discovery and documentation.
- Keeps data cleaning transparent and audit-ready.
- Makes downstream featurization easier because the cleaning process is already documented.

## Quick start

### Install
```bash
pip install dd-parser-cleaner
```

### Initialize a workspace
```bash
uv run init-workspace ./my_project
uv run bootstrap-config ./my_project
```

### Run the core workflow
```bash
classify-entities
uv run clean-dataset --action full --workspace ./my_project
```

## Where to look next
- `USER_GUIDE.md` for usage details
- `documents/` for methodology and internal design notes
- `tests/notebooks/` for example notebook workflows
