# 🚀 Migrating Existing Projects

This document defines the specialized workflow for migrating existing data cleaning logic (e.g., from Jupyter Notebooks or legacy scripts) into the `dd-parser-cleaner` framework.

## 🔄 The "Extract & Baseline" Workflow
Migration is now an **Imperative Process** rather than an orchestrated one. Instead of injecting code into the cleaner's core pipeline, you consume its high-integrity output.

1.  **Generate Baseline**: Run the `clean-dataset --action full` command to establish the "Clean Bucket" and review LLM recommendations.
2.  **Notebook Porting**: Copy existing logic into a Jupyter Notebook that loads the cleaned baseline using `get_cleaned_data(coord)`.
3.  **Functional Chaining**: Refactor legacy code into the recommended sequence: Filter -> Impute -> Derive -> Rename/Drop.

## ⚖️ Implementation Rules

### 1. The Clean Bucket Constraint
All migrated logic must target the attributes synchronized in the `parser_cleaner_handshake.md`. If your legacy code references columns that were stripped (Orphans), you must address why they are missing from the Data Dictionary first.

### 2. Best-Practice Sequence
To prevent clobbering dependencies, migrated logic should follow this order:
1. **Filtering**: Remove invalid rows early.
2. **Imputation**: Fill NaNs before they affect calculations.
3. **Derivation**: Create features while original names are still present.
4. **Schema Management**: Rename or drop columns as the final act.

---
*This guide ensures that the migration from exploratory code to declarative pipelines is predictable, validated, and aligned with the project's Golden Rule.*