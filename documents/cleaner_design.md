# 🧼 Cleaner Module: Generalized Transformation Design

## 🎯 Core Philosophy
The Cleaner is a **domain-agnostic transformation engine**. It provides the "plumbing" (IO, validation, sequencing) while allowing the user to inject "domain science" via a unified **Custom Code Bridge**.

## 🏗️ The Logic Registry
Instead of hardcoded rules, the cleaner treats all operations as lookups within a registry. This allows a seamless blend of built-in vectorized operations and user-defined scripts.

### Configuration Contract (`config.yaml`)
```yaml
cleaner:
  custom_logic_path: "scripts/domain_logic.py"
  pipeline: [integrity, assessment, row_filter, column_filter, impute, standardize, derive]

  structural_assessment:
    dataset_type: "not_yet_inferred" # Options: cross-sectional, longitudinal, panel
    primary_keys: []         # Confirmed by user (e.g., ["LoanID", "LineItem"])
    auto_drop_constant: true
    null_threshold: 0.95
  
  # Each action group maps a column or logical type to a strategy
  missing_values:
    attribute_overrides:
      LoanAmount: "custom:risk_adjusted_impute"
  recoding:
    attribute_overrides:
      BorrState: "custom:map_to_regions"

  # Built-in specialized column filters (Structural)
  column_filters:
    drop_attributes: ["LocationID", "InternalNotes"] # Global drop list
    include_attributes: ["LoanID", "Amount", "Status"] # Global white list (optional)
    attribute_overrides:
      Email: "exclude-regex:.*@test\\.com$"
      LoanID: "include-regex:^L-[0-9]{5}$"
```

## 📜 Standard Signature Contracts
To prevent "signature inflation," all custom logic must adhere to one of three standardized functional contracts. This ensures the engine can call user code predictably.

| Contract | Targeted Actions | Signature | Return Type |
| :--- | :--- | :--- | :--- |
| **Transform** | Imputing, Recoding, Scaling | `func(df, col)` | `pd.Series` |
| **Row Filter** | Row Removal, Outlier Clipping | `func(df)` | `pd.Index` or `Boolean Mask` |
| **Derivation** | Feature Engineering, Merging | `func(df)` | `pd.DataFrame` |

### 🔧 Action-to-Signature Mapping
When implementing custom logic in `scripts/domain_logic.py`, the signature is determined by the pipeline step:

#### 1. Transform Actions (`impute`, `standardize`, `recoding`)
Used when modifying an existing column.
```python
def my_custom_transform(df: pd.DataFrame, col: str) -> pd.Series:
    # Example: Return column 'col' multiplied by a factor from another column
    return df[col] * df['Multiplier']
```

#### 2. Filter Actions (`filter`)
Used to reduce the dataset size by removing rows.
```python
def my_custom_filter(df: pd.DataFrame) -> pd.Index:
    # Example: Keep only rows where 'Status' is 'Active'
    return df[df['Status'] == 'Active'].index
```

#### 3. Derivation Actions (`derive`)
Used to append new columns or perform structural changes.
```python
def my_custom_derivation(df: pd.DataFrame) -> pd.DataFrame:
    # Example: Create a new 'Risk_Score' column
    df['Risk_Score'] = df['Debt'] / df['Income']
    return df
```

## 🔄 Execution Flow
The Cleaner operates as an idempotent sequence:
1.  **Integrity Sync**: Reconciles the Data Dictionary against physical headers (Bucket Strategy).
2.  **Type Alignment**: Coerces raw data into the physical types identified by the Profiler.
3.  **The Action Loop**: Iterates through the `pipeline` defined in config.
    *   **Lookup**: Check if the strategy is internal (e.g., `mean-imputation`) or `custom:`.
    *   **Dispatch**: The engine selects the Signature Contract based on the current Pipeline Step (e.g., `impute` always uses the **Transform** contract).
    *   **Validation**: Ensure the return type matches the contract expectations.

## 🛡️ Safety & Error Boundaries
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
*This document serves as the authoritative methodology for Task 5.x build-outs.*