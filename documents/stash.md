# 📑 Project Stash: Data Dictionary Parser & Cleaner State

## 🤖 Agent Operational Directives
* **Domain Agnosticism**: Strict requirement. Zero hardcoded domain-specific items.
* **Communication Style**: Brief, direct answers by default. Explanations provided only on request.
* **Config Management**: The agent must never modify `config.yaml` directly. If a configuration update is required (e.g., adding `tag_heuristics`), the agent must request the user to update the file and provide the intended YAML snippet.
* **Stash Maintenance**: Consolidate output to ~90% of allowable space. Prioritize active designs, the Resumption Backlog, and the Golden Rule; condense historical architectural logs.

## 🛠️ Active Project State (Last Updated: May 2024)

### 1. Core Architecture
* **Infrastructure**: `PathCoordinator` enforces zero-default path resolution; `logging` (INFO) provides uniform feedback. 
* **Orchestrator**: Executes a two-phase LLM pipeline (Macro Discovery + Atomic Row Assignment) synchronized with physical headers.
* **Classification**: Phase 1 establishes logical entities/keywords; Phase 2 executes atomic row assignment via Llama 3.2.
* **Post-Processor**: Derives prefix stems algorithmically; strips prefixes to validate tags (e.g., `borr_zip` -> `zip`); applies case-insensitive `overrides` as authoritative final step.
* **Integrity & Profiling**: `DatasetDataProfiler` generates JSON metadata (cardinality, null ratios, samples) for LLM grounding. `Mixed Value Quarantine` isolates inconsistent types before cleaning.
* **Reporting**: Unified `DS_type` inference; generates MD reports and CSV replicas with SHA-256 `.signature` security sidecars.

---

## ⚙️ Authoritative Config Contract (`config.yaml`)

```yaml
parser:
  entity_tagging: [geographic]
  overrides: {LocationID: {is_geographic: false, provisional_entity_assignment: Lender}}
cleaner:
  quarantine_directory: quarantine; quarantine_filename: isolated_records.csv
```

---

## 🧩 Key Code Snippet: Prefix-Stripping Heuristics
```python
def _apply_name_heuristics(self, df, target, keywords, prefixes):
    keywords_lower = {str(k).lower().strip() for k in keywords}
    col_name = f"is_{target}"
    for idx in range(len(df)):
        if df.at[idx, col_name]: continue
        attr_clean = str(df.at[idx, "attribute_name"]).lower().strip()
        
        # Direct match
        if any(attr_clean.endswith(kw) or attr_clean == kw for kw in keywords_lower):
            df.at[idx, col_name] = True
            continue
        
        # Prefix-stripped match
        for prefix in prefixes:
            p_lower = prefix.lower()
            if attr_clean.startswith(p_lower):
                stripped = attr_clean[len(p_lower):].lstrip('_').lstrip('-')
                if any(stripped == kw or stripped.startswith(kw) for kw in keywords_lower):
                    df.at[idx, col_name] = True
                    break
```

---

## 🎯 Resumption Backlog

1. **Grounded Inference Implementation**: 
    * **Task 4.1**: Enhance `null_profiler.py` or integrate `fg-data-profiling` to generate a lightweight JSON metadata bundle (cardinality, top 5 samples, inferred physical type).
    * **Task 4.2**: Update `orchestrator.py` to left-join this profile bundle with the Data Dictionary before LLM dispatch.
    * **Task 4.3**: Augment `LLMEntityClassifier` prompts to include the "Profile Sidecar" for improved zero-shot accuracy.
    * **Task 4.4**: Harden `post_processor.py` to use profile stats as an authoritative safety check against semantic hallucination.
    *   **Task 4.5**: Verify "Notebook-first" validation by creating a sample test notebook that exercises a custom imputation handler before CLI execution.

2. **Phase 3: Missing Value Handler Implementation**:
    *   **Task 5.1**: Implement the `MissingValueHandler` core engine with hierarchical resolution (Override > Logical Default > Fallback).
    *   **Task 5.2**: Develop the `CustomCodeBridge` using `importlib` to support the `custom:` prefix in `config.yaml`.

## 🧼 Phase 3: Cleaner Missing Value Design (LOCKED)

### 1. Resolution Hierarchy
For any column containing null values, the cleaner resolves the cleaning action using the following priority:
1. **Attribute Override**: Check `cleaner.missing_values.attribute_overrides` for the specific column name. Supports both predefined actions and `custom:` hooks.
2. **Logical Type Default**: Check `cleaner.missing_values.logical_defaults` using the `logical_type` assigned by the parser (e.g., numeric, categorical). Supports both predefined and `custom:` hooks.
3. **System Fallback**: Leave as `NaN` and log a warning.

### 2. The "Custom Code Bridge"
* **Mechanism**: Dynamic module loading via `importlib.util`. The cleaner loads the script specified in `custom_logic_path`.
* **Trigger**: Any rule string starting with the prefix `custom:` (e.g., `custom:calc_weighted_mean`).
* **User Contract (The Signature)**: Data Scientists implement functions with the following signature:
  `def function_name(df: pd.DataFrame, col: str) -> pd.Series`
* **Persona Focus**: Minimal plumbing; the user writes standard Pandas logic in a local file.

### 3. Guidelines & Validation
* **Portability**: All paths in `custom_logic_path` must be relative to the `--workspace` root to ensure reproducibility across environments.
* **Interactive Testing (Best Practice)**: Before running the CLI, users should test their imputation functions in a Jupyter notebook by passing a sample DataFrame slice to verify the transformation behavior.
* **Dependency Safety**: Custom logic should rely only on libraries already present in the tool's runtime (Pandas/Numpy).

### 4. Predefined Action Library
The cleaner provides these internal vectorized operations:
* `mean-imputation`, `median-imputation`, `mode-imputation`
* `ffill`, `bfill`
* `drop-row` (Removes the record if the value is missing)
* `constant:[value]` (e.g., `constant:Unknown` or `constant:0`)

### 5. Configuration Schema Example
```yaml
cleaner:
  missing_values:
    custom_logic_path: "scripts/my_imputers.py"
    logical_defaults:
      numeric: "mean-imputation"
      categorical: "mode-imputation"
      temporal: "ffill"
      text: "constant:Missing"
    attribute_overrides:
      LoanAmount: "custom:risk_adjusted_impute"
      BorrZip: "constant:00000"
      SocialSecurity: "drop-row"
```

---
*This stash ensures that the "Golden Rule" is maintained: any future updates must build upon the logic summarized here.*