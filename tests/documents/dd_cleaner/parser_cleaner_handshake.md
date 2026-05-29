# 📑 Data Dictionary: Provisional Entity Assignment Report
**Generation Timestamp:** `2026-05-29 06:28:07`
**Source Blueprint:** `sba_dd.csv`

### 🏗️ Structural Assessment
- **Inferred Dataset Type:** `cross-sectional`
> ⚠️ **Note:** This inference is an automated suggestion based on schema patterns and may be incorrect. The `dataset_type` must be explicitly confirmed or defined in `config.yaml` before the Cleaner phase begins.

### 📊 Classification Summary
- **Borrower**: 20 fields
- **LoanProgram**: 10 fields
- **LenderInformation**: 10 fields
- **Lender**: 1 fields

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
| Attribute                | Assignment          | Logical Type   | Physical Type   | Flag: Geographic   |
|--------------------------|---------------------|----------------|-----------------|--------------------|
| `asofdate`               | `Borrower`          | `datetime`     | `datetime`      | `False`            |
| `program`                | `LoanProgram`       | `numeric`      | `int`           | `False`            |
| `locationid`             | `Lender`            | `numeric`      | `int`           | `False`            |
| `borrname`               | `Borrower`          | `text`         | `str`           | `False`            |
| `borrstreet`             | `Borrower`          | `text`         | `str`           | `True`             |
| `borrcity`               | `Borrower`          | `text`         | `str`           | `True`             |
| `borrstate`              | `Borrower`          | `categorical`  | `str`           | `True`             |
| `borrzip`                | `Borrower`          | `numeric`      | `int`           | `True`             |
| `grossapproval`          | `Borrower`          | `numeric`      | `int`           | `False`            |
| `approvaldate`           | `Borrower`          | `datetime`     | `datetime`      | `False`            |
| `approvalfy`             | `Borrower`          | `numeric`      | `int`           | `False`            |
| `firstdisbursementdate`  | `Borrower`          | `datetime`     | `datetime`      | `False`            |
| `processingmethod`       | `LoanProgram`       | `categorical`  | `str`           | `False`            |
| `nan`                    | `LoanProgram`       | `unknown`      | `unknown`       | `False`            |
| `subprogram`             | `Borrower`          | `categorical`  | `str`           | `False`            |
| `terminmonths`           | `LoanProgram`       | `numeric`      | `int`           | `False`            |
| `naicscode`              | `LenderInformation` | `numeric`      | `int`           | `False`            |
| `naicsdescription`       | `Borrower`          | `text`         | `str`           | `False`            |
| `franchisecode`          | `LenderInformation` | `numeric`      | `float`         | `False`            |
| `franchisename`          | `LenderInformation` | `categorical`  | `str`           | `False`            |
| `projectcounty`          | `LoanProgram`       | `text`         | `str`           | `True`             |
| `projectstate`           | `LoanProgram`       | `categorical`  | `str`           | `True`             |
| `sbadistrictoffice`      | `LoanProgram`       | `categorical`  | `str`           | `True`             |
| `congressionaldistrict`  | `LoanProgram`       | `numeric`      | `int`           | `True`             |
| `businesstype`           | `Borrower`          | `categorical`  | `str`           | `False`            |
| `businessage`            | `Borrower`          | `categorical`  | `str`           | `False`            |
| `loanstatus`             | `Borrower`          | `categorical`  | `str`           | `False`            |
| `paidinfulldate`         | `Borrower`          | `datetime`     | `datetime`      | `False`            |
| `chargeoffdate`          | `Borrower`          | `datetime`     | `datetime`      | `False`            |
| `grosschargeoffamount`   | `Borrower`          | `numeric`      | `float`         | `False`            |
| `jobssupported`          | `LenderInformation` | `numeric`      | `int`           | `False`            |
| `collateralind`          | `Borrower`          | `numeric`      | `float`         | `False`            |
| `cdc_name`               | `LenderInformation` | `categorical`  | `str`           | `False`            |
| `cdc_street`             | `Borrower`          | `categorical`  | `str`           | `True`             |
| `cdc_city`               | `LoanProgram`       | `categorical`  | `str`           | `True`             |
| `cdc_state`              | `LoanProgram`       | `categorical`  | `str`           | `True`             |
| `cdc_zip`                | `LenderInformation` | `numeric`      | `int`           | `True`             |
| `thirdpartylender_name`  | `LenderInformation` | `text`         | `str`           | `False`            |
| `thirdpartylender_city`  | `LenderInformation` | `text`         | `str`           | `True`             |
| `thirdpartylender_state` | `LenderInformation` | `categorical`  | `str`           | `True`             |
| `thirdpartydollars`      | `LenderInformation` | `numeric`      | `float`         | `False`            |

---
*Report generated via automated dd-parser post-processing.*