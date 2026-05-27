# dd-parser-cleaner

A private, local LLM-powered data dictionary parser, entity mapper, and case-preserving data transformation pipeline. This package crawls raw dataset structures, classifies attributes through local inference, and executes deterministic data cleaning routines while protecting case variations and file formats.

## 🚀 Quick Start

### 1. Installation

This repository uses `uv` for environment management and dependency tracking.

```bash
# Clone the repository and sync the local virtual environment
cd dd_parser_cleaner
uv sync

# Install package command entry points in editable mode
pip install -e .
```

### 2. Run the Pipeline CLI

```bash
# Step 1: Ingest layout and classify data dictionary entities
classify-entities --workspace . --config config.yaml

# Step 2: Validate signatures and execute geographic scrubbing routines
clean-dataset --workspace . --config config.yaml
```

### 3. Run Automated Tests (`pytest`)

All integration tests run inside an isolated folder context to ensure production directories are never contaminated.

```bash
uv run pytest -v tests/
```

---

## 📑 Core Documentation Index

For deep-dive architectural specifications, path coordinator details, and pipeline handshake rules, please consult the full documentation suite:

* 👉 **[USER_GUIDE.md](USER_GUIDE.md)**: Exhaustive manual detailing hardened engineering constraints, file-routing abstraction schemas, data transformation algorithms, and structural testing profiles.
