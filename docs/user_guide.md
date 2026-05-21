# 📑 dd-parser-cleaner: Comprehensive Developer & User Guide

This guide establishes the architectural specs, hardened engineering rules, and technical data transformation boundaries governing the `dd-parser-cleaner` pipeline environment.

---

## 🏗️ Architecture & Core Workspace Layout

The application isolates functional concerns into two standalone package modules alongside a unified path coordinator module, bundled as an active Python distribution using `hatchling`.

```text
dd_parser_cleaner/                      # Project Root Workspace
├── pyproject.toml                     # Distribution configuration & Hatch wheel include rules
├── config.yaml                        # Global parameter setting definitions
└── src/
    ├── path_coordinator.py            # PlatformPathResolver Dynamic Path Routing Abstraction
    ├── dd_parser/                     # LLM Inference and Suffix Heuristic Sweeper
    │   ├── __init__.py
    │   ├── cli.py                     # Execution hook wrapper for 'classify-entities'
    │   ├── core.py                    # Case-Preserving Parser Matrix & Metadata Generator
    │   └── models.py                  # Pydantic Structural Constraints Contracts
    └── dd_cleaner/                    # Case-Insensitive Transformation Engine
        ├── __init__.py
        ├── cli.py                     # Execution hook wrapper for 'clean-dataset'
        └── engine.py                  # Safe Element-Wise Geographic Transformation Engine
```

---

## 🔒 Hardened Engineering Constraints

### 1. Total Case-Preservation Mapping

Downstream machine learning featurization pipelines fail silently on basic identity mismatches if tabular lookup attributes switch case styles. To mitigate this risk:

* The parser crawls 100% of real field attributes straight from the user's raw input payload data headers.
* It employs case-insensitive suffix sweeps (`_city`, `_zip`, `_street`) to discover geospatial fields.
* It **strictly preserves the original character casing** of the source file inside the final generated metadata dictionary (`sba_analysis_results.csv`).

### 2. Tabular Stream Separation (Anti-Contamination Check)

Prepending tracking hashes or comment signature flags (e.g., `# DD-PARSER-SIGNATURE`) onto the first row of a output CSV forces standard downstream parsers like `pandas.read_csv` to misinterpret tabular data offsets, pushing real column headers down into the data array rows.

* **The Solution:** The pipeline verification tag is extracted entirely into a separate sidecar check file (`.signature`) stored adjacent to the tabular data dictionary spreadsheet, maintaining clean standard parsing mechanics.

### 3. Centralised File-Routing Abstraction

Conversational code modification memory drifts over time. To prevent application processes or test harnesses from falling out of alignment with the **Unified Platform Integration Layout**, no core module is allowed to compute local drive paths manually. Everything inherits paths from the `PlatformPathResolver` instance class:

* **Raw Payloads Input Directory**: `{working_dir}/data/`
* **Cleaned Datasets Destination**: `{working_dir}/data/dd_cleaner_results/`
* **Data Dictionary Target folder**: `{working_dir}/data_dictionary/dd_analysis_results/`
* **Executive Summary Markdown Deliverables**: `{working_dir}/documents/`

---

## 🛠️ Data Cleaning Transformation Algorithms

When the cleaning data pipeline processes variables flagged as `is_geographical = True`, it intentionally avoids vectorized pandas transformations (which convert empty cells into literal strings like `"Nan"` or `"None"`). Instead, it applies row-by-row element-wise algorithms:

* **City Strings**: Stripped of outer whitespace and transformed into pure **Title Case** layouts (`SAN JOSE` \(\rightarrow\) `San Jose`).
* **State Abbreviations**: Stripped of outer whitespace and converted into complete **Uppercase** characters (`ma` \(\rightarrow\) `MA`).
* **ZIP Sequences**: Safely handles numeric floating-point decimal point variants (`"95112.0"` \(\rightarrow\) `"95112"`), clears whitespace, and forces a strict **5-digit zero-padding** length constraint (`"2108"` \(\rightarrow\) `"02108"`). Empty cells pass through cleanly as pure Python `None` targets.

---

## 🧪 Isolated Testing Blueprint (`pytest`)

All regression checking suites are located inside the isolated `./tests` ecosystem context, driven by a global session fixture inside `tests/conftest.py` that configures environment execution variables on the fly.

### Enforced Test Assertions Profile Matrix:

1. **`tests/test_parser.py`**: Validates mixed-case column index discovery (`BorrCity`, `cdc_zip`, `ThirdPartyLender_City`) and proves that non-geographic items (`GrossApproval`) are successfully mapped to null values without hallucinating geographic links.
2. **`tests/test_cleaner.py`**: Passes messy strings, float zips, and missing data points through the transformation loops. Explicitly overrides default reader options using `dtype={"cdc_zip": str}` to assert that zero-padded character tokens are perfectly preserved on disk.
