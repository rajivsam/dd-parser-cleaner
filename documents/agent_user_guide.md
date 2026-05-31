# 🤖 Agent User Guide: Extending the Cleaner

This guide provides the absolute technical constraints and operational patterns required for an AI Agent to extend the `dd-parser-cleaner`, including specialized workflows like **Migration Assistant Mode**.

## 1. The Agent's Mission
Your objective is to transform raw data into a clean state based on a **Data Dictionary**. You do this by:
1.  Identifying columns that need cleaning (Missing values, bad formatting, outliers).
2.  Determining if a **Built-in Action** exists or if a **Custom Hook** is required.
3.  Implementing the logic STRICTLY in `scripts/domain_logic.py`.
4.  Registering the logic in `config.yaml`.

## 1.1 The Two Interaction Paths

### Path 1: The Agent-Led Workflow (Direct)
Best for simple built-ins or straightforward transformations.
1. User describes intent.
2. Agent updates `scripts/domain_logic.py` and `config.yaml`.
3. User runs CLI: `clean-dataset --action full`.

### Path 2: The Notebook-Led Explorer (Sandbox)
Best for complex domain science or exploratory logic.
1. **The Hand-off**: User creates the workspace directory and provides the path.
2. **Initialization**: User runs the `prepare_workspace()` snippet. This authorizes the Agent to begin integrating code into `scripts/`.
3. **Implementation**: User describes intent; Agent writes code to `domain_logic.py` and configuration to `config.yaml`.
4. **Verification**: User imports the logic and verifies it in the notebook.
5. **Acceptance**: If successful, the logic is "locked in."
6. **Abort/Cleanup**: If the experiment fails, user instructs Agent to "Abort," which triggers a revert of the integrated code.

## 1.2 Migration Assistant Mode (Incremental Extension)
This mode is active when the Agent helps migrate existing code or incrementally add new features. 

### Initialization Pattern
When starting a session in a notebook, use this standard snippet. It ensures the `PathCoordinator` resolves KMDS directories correctly even if the notebook is running from the `notebooks/` folder.

```python
from dd_cleaner.notebook_utils import prepare_workspace, init_notebook_session

# 1. Prepare & Initialize (Detects root, ensures scripts/ exists)
prepare_workspace() 
coord, df = init_notebook_session()

# 2. Import logic (MUST happen after init adds scripts to path)
import domain_logic

print(f"✅ Session initialized for: {coord.base_dir}")

# 3. Test the specific Agent-implemented function
# Example: testing a transform function
target_col = "LoanAmount"
df[target_col] = domain_logic.your_function_name(df, target_col)

# 4. Review Results
print(df[target_col].head())
```

## 2. Project File Structure
Expect the following layout. Never use absolute paths in your code; use relative paths from the workspace root.
```text
workspace/
├── src/
│   └── dd_common/path_coordinator.py # Resource Routing
│   └── dd_cleaner/notebook_utils.py # Session Helper
├── config.yaml          # Authoritative Single Source of Truth
├── scripts/
│   └── domain_logic.py  # Where you write your Python code
├── notebooks/           # KMDS: Experimental code (.ipynb)
├── data_dictionary/     # KMDS: Data dictionary assets
├── documents/           # KMDS: Project documentation (.pdf, .txt)
└── data/                # KMDS: Physical data assets (CSVs)
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
If built-ins are insufficient, write a function in the logic script located at `scripts/domain_logic.py`. **You must use one of these three exact signatures.**

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