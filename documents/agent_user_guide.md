# 🤖 Agent User Guide: Extending the Cleaner

This guide provides the absolute technical constraints and operational patterns required for an AI Agent to extend the `dd-parser-cleaner`. If you are an AI, follow this guide to produce code and configurations that are 100% compatible with the core engine.

## 1. The Agent's Mission
Your objective is to transform raw data into a clean state based on a **Data Dictionary**. You do this by:
1.  Identifying columns that need cleaning (Missing values, bad formatting, outliers).
2.  Determining if a **Built-in Action** exists or if a **Custom Hook** is required.
3.  Implementing the logic in `scripts/domain_logic.py`.
4.  Registering the logic in `config.yaml`.

## 1.1 The Two Interaction Paths
*   **Path 1 (Chat-to-Pipeline)**: You implement the logic directly based on user instructions and update the config.
*   **Path 2 (Notebook-to-Pipeline)**: You provide the user with code snippets to test in a Notebook. Once the user confirms the results are correct, you "wire" those snippets into Path 1.

## 2. Project File Structure
Expect the following layout. Never use absolute paths in your code; use relative paths from the workspace root.
```text
workspace/
├── config.yaml          # Your primary control plane
├── scripts/
│   └── domain_logic.py  # Where you write your Python code
├── documents/           # Where Data Dictionaries and Profiles live
└── data/                # Where the raw and clean CSVs live
```

## 3. The Decision Tree (Resolution Hierarchy)
When the engine processes a column, it looks for instructions in this specific order. Use this to determine where to place your configuration:

1.  **Attribute Override**: Specific rule for a specific column name (e.g., `LoanAmount`).
2.  **Logical Type Default**: Default rule for a class of data (e.g., all `numeric` columns).
3.  **System Fallback**: If neither is found, the engine leaves the value as-is and logs a warning.

## 4. Built-in Action Library
Before writing custom code, check if a built-in vectorized action exists:

| Category | Action | Usage Example |
| :--- | :--- | :--- |
| **Impute** | `mean`, `median`, `mode`, `ffill`, `bfill` | `LoanAmount: "mean"` |
| **Impute** | `constant:[value]` | `Status: "constant:Unknown"` |
| **Row Filter** | `drop-row` | `Email: "drop-row"` (removes row if null) |
| **Column Filter** | `include-regex:[pattern]` | `ID: "include-regex:^L-.*"` |
| **Column Filter** | `exclude-regex:[pattern]` | `Email: "exclude-regex:.*@test.com"` |
| **Column Filter** | `drop-list` (in config) | `drop_attributes: ["ColA", "ColB"]` |

## 5. Writing Custom Logic (`scripts/domain_logic.py`)
If built-ins are insufficient, write a function in the logic script. **You must use one of these three exact signatures.**

### A. The Transform Contract
**Use for:** Imputing, Recoding, Scaling (Modifying data within a column).
**Signature:** `def func_name(df: pd.DataFrame, col: str) -> pd.Series:`
```python
import pandas as pd

def risk_adjusted_impute(df: pd.DataFrame, col: str) -> pd.Series:
    # Example: If 'Score' > 10, fill nulls with 5, else fill with 0
    fill_val = df.apply(lambda x: 5 if x['Score'] > 10 else 0, axis=1)
    return df[col].fillna(fill_val)
```

### B. The Filter Contract
**Use for:** Removing rows based on complex multi-column logic.
**Signature:** `def func_name(df: pd.DataFrame) -> pd.Index:`
```python
def remove_test_entities(df: pd.DataFrame) -> pd.Index:
    # Return the index of rows we want to KEEP
    mask = (df['EntityName'] != 'TEST') & (df['Amount'] > 0)
    return df[mask].index
```

### C. The Derivation Contract
**Use for:** Creating new features or structural changes.
**Signature:** `def func_name(df: pd.DataFrame) -> pd.DataFrame:`
```python
def calculate_roi(df: pd.DataFrame) -> pd.DataFrame:
    df['ROI'] = (df['Revenue'] - df['Cost']) / df['Cost']
    return df
```

## 6. Configuring the Pipeline (`config.yaml`)
Register your custom functions using the `custom:` prefix.

```yaml
cleaner:
  custom_logic_path: "scripts/domain_logic.py"
  pipeline: [integrity, filter, impute, standardize, derive]
  
  filters:
    drop_attributes: ["InternalID"]
    attribute_overrides:
      Email: "custom:remove_test_entities"
      
  missing_values:
    logical_defaults:
      numeric: "mean"
      categorical: "mode"
    attribute_overrides:
      LoanAmount: "custom:risk_adjusted_impute"
```

## 🛡️ Operational Guardrails for Agents
1.  **Vectorization**: Never use `.iterrows()` or `.apply()`. Always use vectorized Pandas/NumPy operations.
2.  **Immutability**: Treat the input `df` as read-only inside Transform/Filter contracts; return a new Series or Index.
3.  **Dependencies**: Use only `pandas`, `numpy`, and standard library modules unless the user explicitly installs more.
4.  **Error Handling**: Let exceptions bubble up; the Cleaner Engine handles the crash/log boundary. Do not return "None" or "Error" strings.

## 🧪 Verification Protocol

### The Notebook Trial (Path 2)
Before committing logic to the pipeline, encourage the user to test it. Provide this template:
```python
import pandas as pd
from scripts.domain_logic import your_new_function

df = pd.read_csv("data/sba_loans_raw.csv").head(100)
col = "TargetColumn"
df[col] = your_new_function(df, col)
print(df[col].head())
```

Before telling the user "I am done," provide a test snippet they can run in a Notebook:
```python
# AGENT TEST SCRIP
from scripts.domain_logic import your_function
import pandas as pd
df_test = pd.read_csv("path_to_sample.csv")
result = your_function(df_test, "target_col") # Or appropriate signature
print(result.head())
```