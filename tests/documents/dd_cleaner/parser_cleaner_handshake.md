# 📑 Data Dictionary: Provisional Entity Assignment Report
**Generation Timestamp:** `2026-06-30 13:19:49`
**Source Blueprint:** `sba_dd.csv`

### 🏗️ Structural Assessment
- **Inferred Dataset Type:** `cross-sectional`
> ⚠️ **Note:** This inference is an automated suggestion based on schema patterns and may be incorrect. The `dataset_type` must be explicitly confirmed or defined in `config.yaml` before the Cleaner phase begins.

### 📊 Classification Summary
- **Borrower**: 11 fields
- **Location**: 11 fields
- **Loan**: 6 fields
- **Program**: 3 fields

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
| Attribute               | Assignment   | Logical Type   | Physical Type   | Flag: Geographic   |
|-------------------------|--------------|----------------|-----------------|--------------------|
| `asofdate`              | `Borrower`   | `datetime`     | `datetime`      | `False`            |
| `program`               | `Program`    | `numeric`      | `int`           | `False`            |
| `locationid`            | `Location`   | `numeric`      | `int`           | `True`             |
| `borrname`              | `Borrower`   | `text`         | `str`           | `False`            |
| `borrstreet`            | `Borrower`   | `text`         | `str`           | `True`             |
| `borrcity`              | `Location`   | `text`         | `str`           | `True`             |
| `borrstate`             | `Borrower`   | `categorical`  | `str`           | `True`             |
| `borrzip`               | `Borrower`   | `numeric`      | `int`           | `True`             |
| `grossapproval`         | `Loan`       | `numeric`      | `int`           | `False`            |
| `approvaldate`          | `Loan`       | `datetime`     | `datetime`      | `False`            |
| `approvalfy`            | `Loan`       | `numeric`      | `int`           | `False`            |
| `firstdisbursementdate` | `Borrower`   | `datetime`     | `datetime`      | `False`            |
| `processingmethod`      | `Program`    | `categorical`  | `str`           | `False`            |
| `subprogram`            | `Program`    | `categorical`  | `str`           | `False`            |
| `terminmonths`          | `Loan`       | `numeric`      | `int`           | `False`            |
| `naicscode`             | `Location`   | `numeric`      | `int`           | `True`             |
| `naicsdescription`      | `Location`   | `text`         | `str`           | `True`             |
| `franchisecode`         | `Location`   | `numeric`      | `float`         | `True`             |
| `franchisename`         | `Location`   | `categorical`  | `str`           | `True`             |
| `projectcounty`         | `Location`   | `text`         | `str`           | `True`             |
| `projectstate`          | `Location`   | `categorical`  | `str`           | `True`             |
| `sbadistrictoffice`     | `Location`   | `categorical`  | `str`           | `True`             |
| `congressionaldistrict` | `Location`   | `numeric`      | `int`           | `True`             |
| `businesstype`          | `Borrower`   | `categorical`  | `str`           | `False`            |
| `businessage`           | `Location`   | `categorical`  | `str`           | `True`             |
| `loanstatus`            | `Borrower`   | `categorical`  | `str`           | `False`            |
| `paidinfulldate`        | `Borrower`   | `datetime`     | `datetime`      | `False`            |
| `chargeoffdate`         | `Borrower`   | `datetime`     | `datetime`      | `False`            |
| `grosschargeoffamount`  | `Loan`       | `numeric`      | `float`         | `False`            |
| `jobssupported`         | `Borrower`   | `numeric`      | `int`           | `False`            |
| `collateralind`         | `Loan`       | `numeric`      | `float`         | `False`            |

---
*Report generated via automated dd-parser post-processing.*