# 📑 Data Dictionary: Provisional Entity Assignment Report
**Generation Timestamp:** `2026-08-12 11:33:35`
**Source Blueprint:** `sba_dd.csv`

### 🏗️ Structural Assessment
- **Dataset Type:** `cross-sectional`
> ⚠️ **Note:** This dataset type is provided by configuration and should match your workspace settings. Update `dataset_type` in `config.yaml` if the dataset is actually a panel or longitudinal dataset.

### 📊 Classification Summary
- **Logical Categories**: 18 fields
- **Logical Category**: 3 fields
- **Organization**: 2 fields
- **Geographic**: 2 fields
- **geographic**: 2 fields
- **Logical Category: Unique Identifier**: 1 fields
- **Person**: 1 fields
- **Geographic Entity**: 1 fields
- **Conceptual Entity**: 1 fields

### ⚠️ Orphans in Data Dictionary
> These attributes exist in the dictionary but were **not found** in the raw data file. They have been excluded from the assignments below.

- `BankName`
- `BankFDICNumber`
- `BankNCUANumber`
- `BankStreet`
- `BankCity`
- `BankState`
- `BankZip`
- `SBAGuaranteedApproval`
- `InitialInterestRate`
- `FixedorVariableInterestInd`
- `RevolverStatus`
- `SoldSecMrktInd`

### 👻 Orphans in Data (Ghosts)
> These headers exist in the raw data file but have **no corresponding entry** in the data dictionary.

- `cdc_name`
- `cdc_street`
- `cdc_city`
- `cdc_state`
- `cdc_zip`
- `thirdpartylender_name`
- `thirdpartylender_city`
- `thirdpartylender_state`
- `thirdpartydollars`

---

### 📋 Detailed Assignments
| Attribute               | Assignment                            | Logical Type   | Physical Type   |
|-------------------------|---------------------------------------|----------------|-----------------|
| `asofdate`              | `Logical Categories`                  | `datetime`     | `datetime`      |
| `program`               | `Logical Categories`                  | `numeric`      | `int`           |
| `locationid`            | `Logical Category: Unique Identifier` | `numeric`      | `int`           |
| `borrname`              | `Organization`                        | `text`         | `str`           |
| `borrstreet`            | `Geographic`                          | `text`         | `str`           |
| `borrcity`              | `Geographic`                          | `text`         | `str`           |
| `borrstate`             | `Logical Categories`                  | `categorical`  | `str`           |
| `borrzip`               | `geographic`                          | `numeric`      | `int`           |
| `grossapproval`         | `Logical Categories`                  | `numeric`      | `int`           |
| `approvaldate`          | `Logical Categories`                  | `datetime`     | `datetime`      |
| `approvalfy`            | `Logical Category`                    | `numeric`      | `int`           |
| `firstdisbursementdate` | `Person`                              | `datetime`     | `datetime`      |
| `processingmethod`      | `Logical Categories`                  | `categorical`  | `str`           |
| `subprogram`            | `Logical Categories`                  | `categorical`  | `str`           |
| `terminmonths`          | `Logical Categories`                  | `numeric`      | `int`           |
| `naicscode`             | `Logical Categories`                  | `numeric`      | `int`           |
| `naicsdescription`      | `Logical Categories`                  | `text`         | `str`           |
| `franchisecode`         | `Logical Categories`                  | `numeric`      | `float`         |
| `franchisename`         | `Organization`                        | `categorical`  | `str`           |
| `projectcounty`         | `Geographic Entity`                   | `text`         | `str`           |
| `projectstate`          | `Logical Category`                    | `categorical`  | `str`           |
| `sbadistrictoffice`     | `Conceptual Entity`                   | `categorical`  | `str`           |
| `congressionaldistrict` | `geographic`                          | `numeric`      | `int`           |
| `businesstype`          | `Logical Categories`                  | `categorical`  | `str`           |
| `businessage`           | `Logical Categories`                  | `categorical`  | `str`           |
| `loanstatus`            | `Logical Categories`                  | `categorical`  | `str`           |
| `paidinfulldate`        | `Logical Category`                    | `datetime`     | `datetime`      |
| `chargeoffdate`         | `Logical Categories`                  | `datetime`     | `datetime`      |
| `grosschargeoffamount`  | `Logical Categories`                  | `numeric`      | `float`         |
| `jobssupported`         | `Logical Categories`                  | `numeric`      | `int`           |
| `collateralind`         | `Logical Categories`                  | `numeric`      | `float`         |

---
*Report generated via automated dd-parser post-processing.*