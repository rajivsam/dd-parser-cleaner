# 📑 Data Dictionary: Provisional Entity Assignment Report
**Generation Timestamp:** `2026-05-30 07:49:36`
**Source Blueprint:** `sba_dd.csv`

### 🏗️ Structural Assessment
- **Inferred Dataset Type:** `cross-sectional`
> ⚠️ **Note:** This inference is an automated suggestion based on schema patterns and may be incorrect. The `dataset_type` must be explicitly confirmed or defined in `config.yaml` before the Cleaner phase begins.

### 📊 Classification Summary
- **BorrowerInformation**: 16 fields
- **LocationMetadata**: 16 fields
- **LoanApplication**: 4 fields
- **SBAProgramIndicator**: 3 fields
- **Lender**: 1 fields
- **BankDetails**: 1 fields

### ⚠️ CRITICAL SCHEMA MISMATCH (Orphaned Attributes)
> The following attributes were found in your Data Dictionary but are missing from the raw data file. They have been **excluded** from the operational cleaning matrix.

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


---

### 📋 Detailed Assignments
| Attribute                | Assignment            | Logical Type   | Physical Type   | Flag: Geographic   |
|--------------------------|-----------------------|----------------|-----------------|--------------------|
| `asofdate`               | `BorrowerInformation` | `datetime`     | `datetime`      | `False`            |
| `program`                | `SBAProgramIndicator` | `numeric`      | `int`           | `False`            |
| `locationid`             | `Lender`              | `numeric`      | `int`           | `False`            |
| `borrname`               | `BorrowerInformation` | `text`         | `str`           | `False`            |
| `borrstreet`             | `BorrowerInformation` | `text`         | `str`           | `True`             |
| `borrcity`               | `LocationMetadata`    | `text`         | `str`           | `True`             |
| `borrstate`              | `BorrowerInformation` | `categorical`  | `str`           | `True`             |
| `borrzip`                | `BorrowerInformation` | `numeric`      | `int`           | `True`             |
| `grossapproval`          | `LoanApplication`     | `numeric`      | `int`           | `False`            |
| `approvaldate`           | `LoanApplication`     | `datetime`     | `datetime`      | `False`            |
| `approvalfy`             | `LoanApplication`     | `numeric`      | `int`           | `False`            |
| `firstdisbursementdate`  | `BorrowerInformation` | `datetime`     | `datetime`      | `False`            |
| `processingmethod`       | `LoanApplication`     | `categorical`  | `str`           | `False`            |
| `nan`                    | `BorrowerInformation` | `unknown`      | `unknown`       | `False`            |
| `subprogram`             | `BorrowerInformation` | `categorical`  | `str`           | `False`            |
| `terminmonths`           | `BorrowerInformation` | `numeric`      | `int`           | `False`            |
| `naicscode`              | `LocationMetadata`    | `numeric`      | `int`           | `True`             |
| `naicsdescription`       | `LocationMetadata`    | `text`         | `str`           | `True`             |
| `franchisecode`          | `LocationMetadata`    | `numeric`      | `float`         | `True`             |
| `franchisename`          | `LocationMetadata`    | `categorical`  | `str`           | `True`             |
| `projectcounty`          | `LocationMetadata`    | `text`         | `str`           | `True`             |
| `projectstate`           | `LocationMetadata`    | `categorical`  | `str`           | `True`             |
| `sbadistrictoffice`      | `LocationMetadata`    | `categorical`  | `str`           | `True`             |
| `congressionaldistrict`  | `LocationMetadata`    | `numeric`      | `int`           | `True`             |
| `businesstype`           | `BorrowerInformation` | `categorical`  | `str`           | `False`            |
| `businessage`            | `BorrowerInformation` | `categorical`  | `str`           | `False`            |
| `loanstatus`             | `BorrowerInformation` | `categorical`  | `str`           | `False`            |
| `paidinfulldate`         | `BorrowerInformation` | `datetime`     | `datetime`      | `False`            |
| `chargeoffdate`          | `SBAProgramIndicator` | `datetime`     | `datetime`      | `False`            |
| `grosschargeoffamount`   | `BorrowerInformation` | `numeric`      | `float`         | `False`            |
| `jobssupported`          | `BorrowerInformation` | `numeric`      | `int`           | `False`            |
| `collateralind`          | `SBAProgramIndicator` | `numeric`      | `float`         | `False`            |
| `cdc_name`               | `LocationMetadata`    | `categorical`  | `str`           | `True`             |
| `cdc_street`             | `LocationMetadata`    | `categorical`  | `str`           | `True`             |
| `cdc_city`               | `LocationMetadata`    | `categorical`  | `str`           | `True`             |
| `cdc_state`              | `LocationMetadata`    | `categorical`  | `str`           | `True`             |
| `cdc_zip`                | `LocationMetadata`    | `numeric`      | `int`           | `True`             |
| `thirdpartylender_name`  | `BankDetails`         | `text`         | `str`           | `False`            |
| `thirdpartylender_city`  | `LocationMetadata`    | `text`         | `str`           | `True`             |
| `thirdpartylender_state` | `LocationMetadata`    | `categorical`  | `str`           | `True`             |
| `thirdpartydollars`      | `BorrowerInformation` | `numeric`      | `float`         | `False`            |

---
*Report generated via automated dd-parser post-processing.*