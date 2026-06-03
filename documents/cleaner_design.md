# 🧼 Cleaner Module: Generalized Transformation Design

## 🎯 Core Philosophy
The Cleaner is a **Diagnostic Shell** designed to establish a high-integrity "Clean Baseline." Its mission is to perform the non-destructive grunt work (IO, metadata synchronization, and profiling) so that domain-specific cleaning can happen in a flexible, imperative environment.

## 🏗️ The Diagnostic Pipeline
The cleaner executes a fixed, deterministic sequence to ensure the resulting dataset is fit for purpose:

1.  **Integrity Sync**: Reconciles the Data Dictionary against physical headers (Bucket Strategy).
2.  **Null Profiling**: Generates Markdown and JSON quality baselines.
3.  **Assessment**: LLM-augmented cleaning recommendations based on the grounded data profile.
4.  **Persistence**: Exports the synchronized "Clean Bucket" dataset.

## 🔄 Implementation Boundary
The Cleaner deliberately stops after producing the baseline. 
*   **Framework Duty**: Ensure the headers match, types are identified, and quality issues are flagged.
*   **User Duty**: Implement domain-specific logic (Filtering, Imputing, Deriving) in a Jupyter Notebook using standard Pandas operations.

This boundary prevents "YAML-programming" complexity and ensures the user has total imperative control over their final analytical payload.

## 🛡️ The Quarantine Workflow
Before transformations, the cleaner scans for **Mixed Values**. 
* **Detection**: Identifies columns containing multiple data types (e.g., numeric and string).
* **Isolation**: Records deviating from the dominant type are moved to the `quarantine/` directory.
* **Safety**: This ensures that any subsequent logic applied in a notebook processes a structurally consistent schema.

## 🔄 Execution Flow
The Cleaner operates as an idempotent sequence with a **Consolidated Safety Gate**:

1.  **Readiness Check**: The engine determines if all phases (`row_filter`, `column_filter`, `impute`, `derive`) are defined in `config.yaml`. 
    *   If **Complete**: Present a single unified summary for user acknowledgement.
    *   If **Partial**: Execute using provisional defaults (e.g., from `structural_assessment`) and print a "Provisional Execution" warning.

1.  **Integrity Sync**: Reconciles the Data Dictionary against physical headers (Bucket Strategy).
2.  **Type Alignment**: Coerces raw data into the physical types identified by the Profiler.
3.  **The Action Loop**: Iterates through the `pipeline` defined in config.
4.  **Persistence**: Writes the final baseline to the `dd_cleaner/` data directory.

## 🛡️ Safety Boundaries
*   **Immutable Raw Data**: The engine never modifies the source file.
*   **Handshake Protocol**: Requires the Parser's output to ensure semantic grounding.
*   **No Silent Failures**: Critical schema mismatches (Orphans/Ghosts) are explicitly flagged in the diagnostic report.

## 🧪 User Workflow
1.  **Run CLI**: `clean-dataset --action full` to get the baseline.
2.  **Open Notebook**: Use `imperative_migration_example.ipynb` to apply domain logic.
Custom code is treated as an "untrusted" layer. 

*   **Vectorization Requirement**: Functions receive the full `pd.DataFrame` context. Row-based iteration (e.g. `.iterrows()`) is discouraged; users should use vectorized Pandas/NumPy operations.
*   **Failure Isolation**: 
    *   If a custom function raises an exception, the Cleaner **stops execution** and logs a critical error. 
    *   Unlike null-handling, complex transformations (recoding/filtering) do not use "blind fallbacks" to prevent silent data corruption.
*   **Quarantine**: Records that fail structural type-checks *prior* to custom logic are moved to the `quarantine/` directory, ensuring custom code only processes "clean" schemas.

## 🧪 User Workflow (The 10-Minute Cycle)
1.  **Define**: Add a strategy string (e.g., `custom:my_logic`) to `config.yaml`.
2.  **Implement**: Write a standard Python function in the local script matching the Signature Contract.
3.  **Verify**: Pass a sample slice of the dataframe to the function in a Notebook to verify the logic.
4.  **Execute**: Run the Cleaner CLI to apply the logic at scale.

---

## 🧠 LLM Prompt Externalization for Cleaning Assistant

The `CleaningAssistant` now leverages externalized LLM prompts, moving the "intelligence" of recommendation generation from hardcoded logic to declarative configuration. This offers significant advantages:

*   **Flexibility**: Prompts can be easily tuned or updated in `config.yaml` without modifying core Python code, allowing for rapid iteration on recommendation quality.
*   **Transparency**: The instructions given to the LLM are visible and auditable in the configuration file, making the system's behavior more understandable for both human users and other AI agents.
*   **Domain Agnosticism**: The core `CleaningAssistant` logic remains generic, while domain-specific nuances for generating recommendations can be injected via the prompts.

### Assembly -> Execution -> Processing Pattern

LLM interactions within the `CleaningAssistant` follow a clear pattern:
1.  **Assembly**: Prompts are constructed dynamically by reading templates from `config.yaml` and injecting relevant runtime data (e.g., the dataset profile).
2.  **Execution**: The assembled prompt is sent to the LLM (via `_call_llm`).
3.  **Processing**: The LLM's JSON response is parsed, validated, and integrated into the overall recommendations.

---
*This document serves as the authoritative methodology for Task 5.x build-outs.*