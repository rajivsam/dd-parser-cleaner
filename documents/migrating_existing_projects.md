# 🚀 Migrating Existing Projects

This document defines the specialized workflow for migrating existing data cleaning logic (e.g., from Jupyter Notebooks or legacy scripts) into the `dd-parser-cleaner` framework.

## 🔄 The "Tag & Inject" Workflow
The migration process is a collaborative, human-in-the-loop interaction designed to move logic from loose code blocks into a structured pipeline.

1.  **User Submission**: The user pastes a specific code snippet and identifies the intended **Cleaner Action** (e.g., Row-Filter, Transform/Impute, or Derivation).
2.  **Agent Classification**: The agent confirms the classification and maps the code to the corresponding functional contract (Transform, Filter, or Derivation).
3.  **Code Injection**: The agent automatically wraps the logic in a standardized signature and injects it into the framework.

## ⚖️ Implementation Rules

### 1. Authoritative Naming Strategy
**The raw data file is the source of truth.** 
In any conflict between attribute names in the pasted code and the physical headers of the raw data file, the agent must align the code to the data file version. This prevents `KeyErrors` during pipeline execution and ensures the cleaner operates on the actual physical schema.

### 2. Directory Resolution
Custom logic must be placed in `domain_logic.py` within the `scripts/` directory relative to the current **Working Directory**.
*   **Development/Testing**: `tests/scripts/domain_logic.py`
*   **Production**: `scripts/domain_logic.py`

### 3. Agent Responsibilities
Upon receiving a code block, the agent is responsible for:
*   **Writing the Function**: Implementing the logic in `domain_logic.py`.
*   **Updating Configuration**: Providing the specific YAML snippet for the `attribute_overrides` section in `config.yaml`.
*   **Providing Verification**: Generating a test harness for the user to verify the transformation before running the full pipeline.

## 📋 Contract Mapping Reference

| Notebook Pattern | Cleaner Action | Contract Signature |
| :--- | :--- | :--- |
| `df = df[df.col > val]` | **Row-Filter** | `func(df) -> pd.Index` |
| `df['col'] = df['col'].fillna(x)` | **Impute** | `func(df, col) -> pd.Series` |
| `df['new'] = df['a'] + df['b']` | **Derivation** | `func(df) -> pd.DataFrame` |
| `df['col'] = df['col'].map(dict)` | **Transform** | `func(df, col) -> pd.Series` |

---
*This guide ensures that the migration from exploratory code to declarative pipelines is predictable, validated, and aligned with the project's Golden Rule.*