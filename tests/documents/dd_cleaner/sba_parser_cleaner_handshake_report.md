# 📑 Data Dictionary: Provisional Entity Assignment Report
**Generation Timestamp:** `2026-07-04 11:56:35`
**Source Blueprint:** `sba_dd.csv`

### 🏗️ Structural Assessment
- **Dataset Type:** `cross-sectional`
> ⚠️ **Note:** This dataset type is provided by configuration and should match your workspace settings. Update `dataset_type` in `config.yaml` if the dataset is actually a panel or longitudinal dataset.

### 📊 Classification Summary
- **unassigned**: 23 fields
- **geographic**: 4 fields
- **[unassigned]**: 1 fields
- **7a General**: 1 fields
- **entity**: 1 fields
- **Partnership**: 1 fields

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
| Attribute               | Assignment     | Static/Dynamic   | Logical Type   | Physical Type   | Flag: Geographic   |
|-------------------------|----------------|------------------|----------------|-----------------|--------------------|
| `asofdate`              | `[unassigned]` | none             | `datetime`     | `datetime`      | `False`            |
| `program`               | `unassigned`   | none             | `numeric`      | `int`           | `False`            |
| `locationid`            | `unassigned`   | none             | `numeric`      | `int`           | `False`            |
| `borrname`              | `unassigned`   | none             | `text`         | `str`           | `False`            |
| `borrstreet`            | `geographic`   | none             | `text`         | `str`           | `True`             |
| `borrcity`              | `geographic`   | none             | `text`         | `str`           | `True`             |
| `borrstate`             | `unassigned`   | none             | `categorical`  | `str`           | `False`            |
| `borrzip`               | `geographic`   | none             | `numeric`      | `int`           | `True`             |
| `grossapproval`         | `unassigned`   | none             | `numeric`      | `int`           | `False`            |
| `approvaldate`          | `unassigned`   | none             | `datetime`     | `datetime`      | `False`            |
| `approvalfy`            | `unassigned`   | none             | `numeric`      | `int`           | `False`            |
| `firstdisbursementdate` | `unassigned`   | none             | `datetime`     | `datetime`      | `False`            |
| `processingmethod`      | `7a General`   | none             | `categorical`  | `str`           | `False`            |
| `subprogram`            | `unassigned`   | none             | `categorical`  | `str`           | `False`            |
| `terminmonths`          | `unassigned`   | none             | `numeric`      | `int`           | `False`            |
| `naicscode`             | `unassigned`   | none             | `numeric`      | `int`           | `False`            |
| `naicsdescription`      | `unassigned`   | none             | `text`         | `str`           | `False`            |
| `franchisecode`         | `unassigned`   | none             | `numeric`      | `float`         | `False`            |
| `franchisename`         | `unassigned`   | none             | `categorical`  | `str`           | `False`            |
| `projectcounty`         | `entity`       | none             | `text`         | `str`           | `True`             |
| `projectstate`          | `unassigned`   | none             | `categorical`  | `str`           | `False`            |
| `sbadistrictoffice`     | `unassigned`   | none             | `categorical`  | `str`           | `True`             |
| `congressionaldistrict` | `geographic`   | none             | `numeric`      | `int`           | `True`             |
| `businesstype`          | `Partnership`  | none             | `categorical`  | `str`           | `False`            |
| `businessage`           | `unassigned`   | none             | `categorical`  | `str`           | `False`            |
| `loanstatus`            | `unassigned`   | none             | `categorical`  | `str`           | `False`            |
| `paidinfulldate`        | `unassigned`   | none             | `datetime`     | `datetime`      | `False`            |
| `chargeoffdate`         | `unassigned`   | none             | `datetime`     | `datetime`      | `False`            |
| `grosschargeoffamount`  | `unassigned`   | none             | `numeric`      | `float`         | `False`            |
| `jobssupported`         | `unassigned`   | none             | `numeric`      | `int`           | `False`            |
| `collateralind`         | `unassigned`   | none             | `numeric`      | `float`         | `False`            |

---
*Report generated via automated dd-parser post-processing.*