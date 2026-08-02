# 📑 Data Dictionary: Provisional Entity Assignment Report
**Generation Timestamp:** `2026-08-02 12:35:01`
**Source Blueprint:** `sba_dd.csv`

### 🏗️ Structural Assessment
- **Dataset Type:** `cross-sectional`
> ⚠️ **Note:** This dataset type is provided by configuration and should match your workspace settings. Update `dataset_type` in `config.yaml` if the dataset is actually a panel or longitudinal dataset.

### 📊 Classification Summary
- **Logical Categories**: 19 fields
- **Logical Category**: 14 fields
- **Geographic**: 4 fields
- **geographic**: 3 fields
- **Person**: 1 fields
- **date**: 1 fields
- **Conceptual Entity**: 1 fields

### 👻 Orphans in Data (Ghosts)
> These headers exist in the raw data file but have **no corresponding entry** in the data dictionary.

- `Unnamed: 21`

---

### 📋 Detailed Assignments
| Attribute                    | Assignment           | Logical Type   | Physical Type   |
|------------------------------|----------------------|----------------|-----------------|
| `AsOfDate`                   | `Logical Category`   | `datetime`     | `datetime`      |
| `Program`                    | `Logical Categories` | `numeric`      | `int`           |
| `LocationID`                 | `Logical Category`   | `numeric`      | `int`           |
| `BorrName`                   | `Person`             | `numeric`      | `int`           |
| `BorrStreet`                 | `geographic`         | `numeric`      | `int`           |
| `BorrCity`                   | `Geographic`         | `numeric`      | `int`           |
| `BorrState`                  | `Logical Category`   | `numeric`      | `int`           |
| `BorrZip`                    | `geographic`         | `numeric`      | `int`           |
| `BankName`                   | `Logical Category`   | `numeric`      | `int`           |
| `BankFDICNumber`             | `Logical Categories` | `numeric`      | `int`           |
| `BankNCUANumber`             | `Logical Categories` | `numeric`      | `int`           |
| `BankStreet`                 | `geographic`         | `numeric`      | `int`           |
| `BankCity`                   | `Geographic`         | `numeric`      | `int`           |
| `BankState`                  | `Logical Category`   | `numeric`      | `int`           |
| `BankZip`                    | `Geographic`         | `numeric`      | `int`           |
| `GrossApproval`              | `Logical Category`   | `numeric`      | `int`           |
| `SBAGuaranteedApproval`      | `Logical Categories` | `numeric`      | `int`           |
| `ApprovalDate`               | `Logical Category`   | `datetime`     | `datetime`      |
| `ApprovalFY`                 | `Logical Category`   | `numeric`      | `int`           |
| `FirstDisbursementDate`      | `date`               | `numeric`      | `int`           |
| `ProcessingMethod`           | `Logical Categories` | `numeric`      | `int`           |
| `Subprogram`                 | `Logical Category`   | `numeric`      | `int`           |
| `InitialInterestRate`        | `Logical Categories` | `numeric`      | `int`           |
| `FixedorVariableInterestInd` | `Logical Categories` | `numeric`      | `int`           |
| `TermInMonths`               | `Logical Categories` | `numeric`      | `int`           |
| `NaicsCode`                  | `Logical Categories` | `numeric`      | `int`           |
| `NaicsDescription`           | `Logical Categories` | `numeric`      | `int`           |
| `FranchiseCode`              | `Logical Category`   | `numeric`      | `int`           |
| `FranchiseName`              | `Conceptual Entity`  | `numeric`      | `int`           |
| `ProjectCounty`              | `Logical Category`   | `numeric`      | `int`           |
| `ProjectState`               | `Logical Category`   | `numeric`      | `int`           |
| `SBADistrictOffice`          | `Logical Category`   | `numeric`      | `int`           |
| `CongressionalDistrict`      | `Geographic`         | `numeric`      | `int`           |
| `BusinessType`               | `Logical Categories` | `numeric`      | `int`           |
| `BusinessAge`                | `Logical Categories` | `numeric`      | `int`           |
| `LoanStatus`                 | `Logical Categories` | `numeric`      | `int`           |
| `PaidInFullDate`             | `Logical Category`   | `numeric`      | `int`           |
| `ChargeOffDate`              | `Logical Categories` | `numeric`      | `int`           |
| `GrossChargeOffAmount`       | `Logical Categories` | `numeric`      | `int`           |
| `RevolverStatus`             | `Logical Categories` | `numeric`      | `int`           |
| `JobsSupported`              | `Logical Categories` | `numeric`      | `int`           |
| `CollateralInd`              | `Logical Categories` | `numeric`      | `int`           |
| `SoldSecMrktInd`             | `Logical Categories` | `numeric`      | `int`           |

---
*Report generated via automated dd-parser post-processing.*