# 📑 Project Stash: Data Dictionary Parser & Cleaner State

## 🤖 Agent Operational Directives
* **Domain Agnosticism**: Strict requirement. Zero hardcoded domain-specific items or assumptions.
* **Communication Style**: Brief, direct answers by default. Explanations provided only on request.
* **Config Management**: The agent must never modify `config.yaml` directly. If a configuration update is required (e.g., adding `tag_heuristics`), the agent must request the user to update the file and provide the intended YAML snippet.
* **Stash Maintenance**: Consolidate output to ~90% of allowable space. Prioritize active designs, the Resumption Backlog, and the Golden Rule; condense historical architectural logs.

## 🛠️ Active Project State (Last Updated: October 2024)

### 1. Core Architecture
* **Infrastructure**: `PathCoordinator` enforces zero-default path resolution; `logging` (INFO) provides uniform feedback. 
* **Cleaner Orchestration**: `PipelineRunner` established as an idempotent engine. It performs early type-casting to pivot cleaning logic off the authoritative parser output.
* **Data Quality & Grounding**: `DatasetDataProfiler` generates Markdown reports and JSON metadata sidecars (cardinality, samples) to ground LLM inference in physical reality (Task 4.1).
* **Design Decision**: Prefect was evaluated but rejected to maintain a lightweight, zero-infrastructure footprint and minimize dependency bloat.
* **Orchestrator**: Executes a two-phase LLM pipeline (Macro Discovery + Atomic Row Assignment) synchronized with physical headers.
* **Classification**: Phase 1 establishes logical entities/keywords; Phase 2 executes atomic row assignment via Llama 3.2.
* **Post-Processor**: Derives prefix stems algorithmically; strips prefixes to validate tags (e.g., `borr_zip` -> `zip`); applies case-insensitive `overrides` as authoritative final step.
* **Integrity Engine**: `IntegrityEngine` enforces a "Bucket Strategy" to validate the bridge between the Data Dictionary and Raw Data.
    * **Bucket A (Operational)**: Matches found; proceed to cleaning. **Bucket B (Orphans)**: In Dictionary but missing from Data; quarantined/stripped. **Bucket C (Ghosts)**: In Data but missing from Dictionary.
* **Reporting**: Unified `DS_type` inference; generates MD reports with "Critical Schema Mismatch" warnings and structured CSV matrices (stripped of orphans).
* **Structural Assessment (Phase 1.5)**: Integrated LLM-based inference to distinguish between `panel` and `cross-sectional` data structures.
    * **Logic**: Detects repeating temporal attribute sets vs. single snapshot timestamps (e.g., `asOfDate`). 
    * **HITL Design**: The parser remains non-blocking; inference is presented in the Markdown report for user confirmation in `config.yaml` prior to cleaning.
* **Testing Workspace Context**: The `tests/` directory is designated as the primary operational workspace for development and testing. The `PathCoordinator` is configured to handle `working_dir=tests/` and will correctly resolve paths, including the authoritative `config.yaml` located at the project root. Custom code for testing and development (e.g., `scripts/domain_logic.py`) should be placed relative to this `tests/` working directory (e.g., `tests/scripts/domain_logic.py`).


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
    * **Task 4.1**: [STABILIZED] `null_profiler.py` generates JSON metadata sidecar (cardinality, top 5 samples, normalized types).
    * **Task 4.2**: Update `orchestrator.py` to left-join this profile bundle with the Data Dictionary before LLM dispatch.
    * **Task 4.3**: Augment `LLMEntityClassifier` prompts to include the "Profile Sidecar" for improved zero-shot accuracy. 
    * **Task 4.4**: Harden `post_processor.py` to use profile stats as an authoritative safety check against semantic hallucination.
    *   **Task 4.5**: Verify "Notebook-first" validation by creating a sample test notebook that exercises a custom imputation handler before CLI execution.

2. **Phase 3: Cleaner Pipeline & Missing Values (Next Cycle)**:
    *   **Task 5.1**: [COMPLETED] Implement `PipelineRunner` core and CLI/Test alignment.
    *   **Task 5.2**: [DESIGNED] Integrity Sync (Bucket Strategy) implemented.
    *   **Task 5.2.1**: [STABILIZED] Phase 1.5 Structural Assessment implemented. Blocking wizard removed from parser to maintain non-interactive extraction.
    *   **Task 5.3**: [UPCOMING] Implement the `MissingValueHandler` core engine with hierarchical resolution.
    *   **Task 5.4**: [DESIGNED] Contracts established for generalized `CustomCodeBridge` across all pipeline stages.
    *   **Task 5.5**: Add CLI support for `--action` to trigger explicit atomic cleaning steps.

## 🧼 Phase 3: Cleaner Pipeline Design (LOCKED)

### 0. Execution Pipeline
The cleaner executes transformations in a strict, idempotent sequence:
1. **Integrity Sync**: Reconcile Dictionary vs Raw (Bucket Strategy).
2. **Structural Assessment**: Heuristic audit for constant and sparse columns (Gate 1).
3. **Manual Drop Gate**: Enforce explicit configuration updates in `config.yaml` for flagged attributes (Gate 2).
4. **Row Filtering**: Remove records based on semantic rules, primarily via custom logic.
5. **Column Filtering**: Execute the physical drop of attributes.
6. **Type Casting & Profiling**: Coerce types and generate the final Null Profile Report.
7. **Imputation**: Handle missing values (Resolution Hierarchy).
8. **Standardization**: Title-casing, zero-padding, etc.
9. **Derivation**: Custom feature engineering.

### 1. Resolution Hierarchy
For any column containing null values, the cleaner resolves the cleaning action using the following priority:
1. **Attribute Override**: Check `cleaner.missing_values.attribute_overrides` for the specific column name. Supports both predefined actions and `custom:` hooks.
2. **Logical Type Default**: Check `cleaner.missing_values.logical_defaults` using the `logical_type` assigned by the parser (e.g., numeric, categorical). Supports both predefined and `custom:` hooks.
3. **System Fallback**: Leave as `NaN` and log a warning.
*Note: This hierarchy applies to all transformation stages (Impute, Recode, Standardize).*

### 2. The "Custom Code Bridge"
* **Mechanism**: Dynamic module loading via `importlib.util`. The cleaner loads the script specified in `custom_logic_path`.
* **Trigger**: Any rule string starting with the prefix `custom:` (e.g., `custom:calc_weighted_mean`).
* **Standardized Contracts**: 
    * **Transform**: `func(df, col) -> pd.Series`
    * **Filter**: `func(df) -> pd.Index`
    * **Derivation**: `func(df) -> pd.DataFrame`
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
* `include-regex:[pattern]`, `exclude-regex:[pattern]` (Primarily for column filtering)
* `drop-list`, `include-list` (Global attribute column filtering)
* `constant:[value]` (e.g., `constant:Unknown` or `constant:0`)

### 5. Configuration Schema Example
```yaml
cleaner:
  pipeline: [integrity, row_filter, column_filter, impute, standardize, derive]
  column_filters:
    drop_attributes: ["LocationID", "InternalNotes"]
    attribute_overrides: { Email: "exclude-regex:.*@test\\.com$" }
  structural_assessment:
    dataset_type: "not_yet_inferred"
    primary_keys: []
    auto_drop_constant: true
    null_threshold: 0.95
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