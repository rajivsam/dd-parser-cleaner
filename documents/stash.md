# 📑 Project Stash: Data Dictionary Parser & Cleaner State

## 🤖 Agent Operational Directives
* **Domain Agnosticism**: Strict requirement. Zero hardcoded domain-specific items, magic numbers, or regulatory assumptions. All domain logic must be injected via config or discovered via the "Domain Discovery" phase.
* **Communication Style**: Brief, direct answers by default. Explanations provided only on request. (Refined: Conversational but concise).
* **Config Management**: The agent must never modify `config.yaml` directly. If a configuration update is required (e.g., adding `tag_heuristics`), the agent must request the user to update the file and provide the intended YAML snippet.
*   **Behavioral Change Awareness**: Before suggesting changes that modify existing logic in `domain_logic.py` or functional settings in `config.yaml`, the agent must explicitly notify the user of the expected change in behavior.
*   **Raw Data Verification**: The agent must strictly verify that every attribute name referenced in code or configuration changes matches an existing column in the raw dataset file to prevent schema drift and runtime errors.
* **KMDS Handshake Protocol**: The Cleaner enforces the existence of `parser_cleaner_handshake.md` (the "handshake file") in `documents/dd_cleaner/` before execution. This file serves as the fixed "Inbox" artifact produced by the Parser and contains semantic context for discovery.
*   **Migration Role**: The agent acts as a facilitator for "Tag & Inject" workflows. Users provide legacy code or regulatory docs; the agent translates them into standardized hooks in `scripts/domain_logic.py` or Policy Manifests.
* **Stash Maintenance**: Consolidate output to ~90% of allowable space. Prioritize active designs, the Resumption Backlog, and the 7-Point Framework.
* **Single Source of Truth**: This `documents/stash.md` is the sole authoritative record of the project's state. All other historical or redundant stashes have been removed.

## 🛠️ Active Project State (Last Updated: May 29, 2026)

### 1. Core Architecture
* **Infrastructure**: `PathCoordinator` enforces zero-default path resolution; `logging` (INFO) provides uniform feedback. 
* **Baseline Status**: Cleaner 'profile', 'discovery', and 'assessment' (recommendations) actions verified in ./tests workspace; system is logically locked and ready for full transformation execution.
* **Phase 0: Domain Discovery (Design Goal)**: Shifting from hard-coded rules to "Policy-as-Configuration." Ingests supplemental docs (PDF/SOPs) via LLM to generate machine-readable JSON/YAML manifests.
* **Cleaner Orchestration**: `PipelineRunner` established as an idempotent engine. It performs early type-casting to pivot cleaning logic off the authoritative parser output.
* **Data Quality & Grounding**: `DatasetDataProfiler` generates Markdown reports and JSON metadata sidecars (cardinality, samples) to ground LLM inference in physical reality (Task 4.1).
* **Project Cleanup**: The `gemini/` directory has been deleted to resolve context drift andtechnical debt. Redundant configurations (`insconfig.yaml`, `mn_traffic.yaml`, `sbaconfig.yaml`) are retained as legitimate counterparts for secondary datasets.
* **Orchestrator**: Executes a two-phase LLM pipeline (Macro Discovery + Atomic Row Assignment) synchronized with physical headers.
* **Classification**: Phase 1 establishes logical entities/keywords; Phase 2 executes atomic row assignment via Llama 3.2.
* **Post-Processor**: Derives prefix stems algorithmically; strips prefixes to validate tags (e.g., `borr_zip` -> `zip`); applies case-insensitive `overrides` as authoritative final step.
* **Integrity Engine**: `IntegrityEngine` enforces a "Bucket Strategy" to validate the bridge between the Data Dictionary and Raw Data.
    * **Bucket A (Operational)**: Matches found. **Bucket B (Orphans)**: In Dictionary but missing from Data. **Bucket C (Ghosts)**: In Data but missing from Dictionary.
* **Policy Engine**: `UniversalValidator` consumes externalized manifests for domain logic. Legacy hard-coded SBA thresholds ($350k caps) have been retired.
* **Reporting**: Unified `DS_type` inference; generates MD reports with "Critical Schema Mismatch" warnings and structured CSV matrices (stripped of orphans).
* **Structural Assessment (Phase 1.5)**: Integrated LLM-based inference in `LLMEntityClassifier` to distinguish between `panel` and `cross-sectional` data structures.
    * **Logic**: Detects repeating temporal attribute sets vs. single snapshot timestamps (e.g., `asOfDate`). 
    * **Implementation**: The orchestrator persists the inferred `dataset_type` to `config.yaml` with an `(inferred)` tag using absolute path resolution.
* **Standardized CLI Entry Points**: The project is configured with authoritative CLI commands: `classify-entities` for the Metadata Parser and `clean-dataset` for the Dataset Cleaner. Users should always run these commands instead of direct python calls to ensure consistent path resolution and orchestration.
* **Installation Protocol**: This project strictly uses `uv`. To register CLI entry points in the local environment, use `uv pip install -e .`. Standard `pip` commands are deprecated for this workspace.
* **Testing Workspace Context**: The `tests/` directory is the primary sandbox for development. **CRITICAL**: When executing CLI tools (e.g., `clean-dataset --workspace ./tests/ --action discovery`), you must point `--workspace` to `./tests/`. This ensures the `PathCoordinator` resolves the simulated KMDS hierarchy correctly.
* **Cleaning Assistant**: LOCKED 7-point heuristic framework producing segmented reports. Artifacts from interactive loops and Phase 2 filtering have been removed.
* **Loan Health & Distress Monitoring**: LOCKED ordinal metric system.
    * **Universe Filter**: Excludes administrative/integrity noise (`CANCLD`, `EXEMPT`, `COMMIT`, `pna`).
    * **Distress Metric**: 3-tier ordinal score (0: Healthy, 1: Under Duress, 2: Written Off) derived via `custom:derive_loan_distress_metric`.


---

## ⚙️ Authoritative Config Contract (`config.yaml`)

```yaml
parser:
  entity_tagging: [geographic]
  overrides: {LocationID: {is_geographic: false, provisional_entity_assignment: Lender}}
cleaner:
  column_filters:
    drop_attributes: ["firstdisbursementdate", "asofdate", "paidinfulldate"]
  quarantine_directory: quarantine
  quarantine_filename: isolated_records.csv
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

## 🎯 Resumption Backlog (High Priority Pivot)

0. **Phase 0: Domain Discovery & Zero-Hardcoding**:
    * **Task 6.1**: [STABILIZED] Generic **Policy Manifest** schema implemented.
    * **Task 6.2**: [STABILIZED] `DocumentProcessor` integrated into CLI for automated rule extraction.
    * **Task 6.3**: [STABILIZED] `UniversalValidator` implemented and wired into the pipeline; legacy SBA engine retired.

1. **Grounded Inference & Data Quality**: 
    * **Task 4.1**: [STABILIZED] `null_profiler.py` generates JSON metadata sidecar (cardinality, top 5 samples, normalized types).
    * **Task 4.2**: [STABILIZED] Orchestrator performs bootstrap profiling and joins metadata for the Cleaning Assistant.
    * **Task 4.2.1**: [REMOVED] Blocking structural safety gate removed in favor of non-halting NL-Edit reporting.
    * **Task 4.3**: [STABILIZED] Augmented `LLMEntityClassifier` prompts to include the "Profile Sidecar" and SBA SOP 50 10 8 Domain Rules.
    * **Task 4.3.1**: [RETIRED] `SOPProcessor` replaced by decoupled `DocumentProcessor` and `UniversalValidator`.
    * **Task 4.4**: [LOCKED] Cleaning Assistant implements simplified 7-point heuristic framework and segmented reporting.
    * **Task 4.5**: [LOCKED] 'Edit Cycle' Verification established in `tests/test_cleaner_edit_cycle.py`.
    * **Task 4.6**: [LOCKED] Provisional Recommendation Sandbox test established in `tests/test_provisional_recommendations.py`.

2. **Phase 3: Cleaner Pipeline & Missing Values**:
    *   **Task 5.1**: [COMPLETED] Implement `PipelineRunner` core and CLI/Test alignment.
    *   **Task 5.2**: [STABILIZED] Integrity Sync (Bucket Strategy) implemented.
    *   **Task 5.2.1**: [STABILIZED] Phase 1.5 Structural Assessment & Cleaning Assistant Report generation implemented.
    *   **Task 5.3**: [STABILIZED] PipelineRunner refactored to delegate to MissingValueHandler engine.
    * **Task 5.4**: [STABILIZED] Unified `CustomCodeBridge` implemented; `profile` action added as independent feature.
    *   **Task 5.5**: [COMPLETED] Add CLI support for `--action` to trigger explicit atomic cleaning steps.
    * **Task 5.6**: [LOCKED] Loan Health Monitoring suite (Active Universe Filter + Distress Metric) integrated and verified.
    * **Task 5.7**: [LEGACY] Policy Engine implemented with hard-coded logic; scheduled for Task 6.3 refactor.

## 🧼 Phase 3: Cleaner Pipeline Design (LOCKED)

### 0. Execution Pipeline
The cleaner executes transformations in a strict, idempotent sequence:
1. **Integrity Sync**: Reconcile Dictionary vs Raw (Bucket Strategy).
2. **Structural Assessment**: Heuristic audit; generates recommendations.
3. **Row Filtering**: Remove records via semantic rules.
4. **Type Casting & Imputation**: Resolve missing values via Hierarchy.
5. **Derivation**: Custom feature engineering.
6. **Column Filtering**: Final physical removal of attributes (Safety for derivations).

### 0.1 Streamlined Execution
The engine operates in two primary modes:
*   **Profile Mode**: Generates independent missingness and structural health reports (Task 5.4).
*   **Assessment Mode**: Generates reports and identifies unhandled structural anomalies.
*   **Full Mode**: Executes the declarative pipeline defined in `config.yaml`.
*   **Non-Blocking Logic**: The "Structural Safety Gate" has been transitioned to a reporting-only phase. The pipeline no longer halts on unhandled recommendations, allowing for fluid Agent-mediated configuration management.

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
  pipeline: [integrity, assessment, column_filter, row_filter, impute, derive]
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
      BorrZip: "constant:00000"
      SocialSecurity: "drop-row"
```

---
*This stash ensures that the "Golden Rule" is maintained: any future updates must build upon the logic summarized here.*