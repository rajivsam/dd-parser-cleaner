# 🚀 Migration Bridge: Context Transfer Manifest

## 📌 Baseline Project State (Post-Fix)
* **Version**: `dd-parser-cleaner==0.2.1` (Published to PyPI).
* **Core Architecture**: `PathCoordinator` (Resource Routing), `IntegrityEngine` (Bucket Reconciliation), `UniversalValidator` (Policy Manifests).
* **Current Workspace Status**: Baselined. `config.yaml` is purged of legacy custom logic to verify Phase 0 (Discovery) stability in the new environment.

## 🤖 Operational Guardrails (STRICT)
1. **Zero-Hardcoding**: All domain logic must be injected via `scripts/domain_logic.py` or configured in `config.yaml`.
2. **KMDS Structure**: The engine enforces and expects:
    - `data/`: Raw and Clean CSVs.
    - `data_dictionary/`: Source metadata.
    - `agent_documents/`: Agent operational guides, stash, and handshakes.
    - `documents/`: KMDS source documents for LLM ingest (SOPs, requirements).
    - `scripts/`: Custom logic hooks.
3. **Path 2 Protocol (Notebook-Led Explorer)**:
    - Logic is written to `scripts/domain_logic.py`.
    - Verification happens live in a Jupyter notebook via `importlib.reload`.
    - Standard signatures:
        - **Transform**: `func(df, col) -> pd.Series`
    	- **Filter**: `func(df) -> pd.Index`
    	- **Derivation**: `func(df) -> pd.DataFrame`

## 🎯 Resumption Backlog: The Migration Trial

### Phase 1: Environment Stabilization
1. **Initialization**:
    - User runs `uv pip install dd-parser-cleaner==0.2.1`.
    - **Config Selection**: Pick the relevant configuration file from the `example_config/` directory, move it to the workspace root, and rename it to `config.yaml`.
    - User runs `prepare_workspace(working_dir="<NEW_PATH>")` to generate directories.
2. **Discovery Verification**:
    - Run `classify-entities` to generate `parser_cleaner_handshake.md`.
    - Run `clean-dataset --action discovery` to generate `cleaning_recommendations.md`.

### Phase 2: Custom Logic Migration ("Tag & Inject")
1. **The Categorical Handler**:
    - **Objective**: Implement a handler that fills missing categorical values with the string `"MISSING"`.
    - **Location**: `scripts/domain_logic.py`.
    - **Action**: Add `custom:impute_categorical_missing` to `config.yaml` under `missing_values.logical_defaults.categorical`.

## 📂 Config Selection
The configuration files (e.g., `insconfig.yaml`, `mn_traffic.yaml`, `sbaconfig.yaml`) are located in the `example_config/` directory. 
1. Select the configuration that matches your dataset.
2. Copy it to the root of your migration workspace.
3. Rename it to `config.yaml` so the `PathCoordinator` can resolve it automatically.

## ⚙️ Baseline Config Snippet (Context Preservation)
```yaml
cleaner:
  custom_logic_path: scripts/domain_logic.py
  pipeline: [integrity, assessment, row_filter, impute, derive, column_filter]
  missing_values:
    logical_defaults: {} # To be populated with "custom:impute_categorical_missing"
    attribute_overrides: {}
```

## 🧩 Logic Snippet to Re-Inject
```python
import pandas as pd

def impute_categorical_missing(df: pd.DataFrame, col: str) -> pd.Series:
    """Vectorized handler for 'MISSING' category encoding."""
    return df[col].fillna("MISSING")
```

---
**Note to Assistant**: Upon initialization in the new workspace, read `agent_user_guide.md` and `migrating_existing_projects.md` to ensure Path 2 compliance.
```