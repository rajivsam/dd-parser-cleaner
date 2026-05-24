# 📑 Data Dictionary: Provisional Entity Assignment Report
**Source Blueprint:** `sba_dd.csv`

### 📊 Classification Summary
- **Borrower Information**: 18 fields
- **Location Data**: 13 fields
- **Loan Details**: 11 fields
- **Bank Information**: 5 fields
- **unassigned**: 5 fields
- **Lender**: 1 fields

---

### 📋 Detailed Assignments
| Attribute                    | Provisional Entity Assignment   | Flag: Geographic   | Logical Type   |
|------------------------------|---------------------------------|--------------------|----------------|
| `asofdate`                   | `Borrower Information`          | `False`            | `datetime`     |
| `program`                    | `Loan Details`                  | `False`            | `numeric`      |
| `locationid`                 | `Lender`                        | `False`            | `numeric`      |
| `borrname`                   | `Borrower Information`          | `False`            | `text`         |
| `borrstreet`                 | `Borrower Information`          | `False`            | `text`         |
| `borrcity`                   | `Location Data`                 | `True`             | `text`         |
| `borrstate`                  | `Borrower Information`          | `True`             | `text`         |
| `borrzip`                    | `Borrower Information`          | `True`             | `numeric`      |
| `BankName`                   | `Bank Information`              | `False`            | `text`         |
| `BankFDICNumber`             | `Bank Information`              | `False`            | `text`         |
| `BankNCUANumber`             | `Bank Information`              | `False`            | `text`         |
| `BankStreet`                 | `Location Data`                 | `True`             | `text`         |
| `BankCity`                   | `Location Data`                 | `True`             | `text`         |
| `BankState`                  | `Bank Information`              | `True`             | `text`         |
| `BankZip`                    | `Bank Information`              | `False`            | `text`         |
| `grossapproval`              | `Loan Details`                  | `False`            | `numeric`      |
| `SBAGuaranteedApproval`      | `Borrower Information`          | `False`            | `text`         |
| `approvaldate`               | `Loan Details`                  | `False`            | `datetime`     |
| `approvalfy`                 | `unassigned`                    | `False`            | `numeric`      |
| `firstdisbursementdate`      | `Loan Details`                  | `False`            | `datetime`     |
| `processingmethod`           | `Loan Details`                  | `False`            | `categorical`  |
| `nan`                        | `Borrower Information`          | `False`            | `text`         |
| `subprogram`                 | `Borrower Information`          | `False`            | `categorical`  |
| `InitialInterestRate`        | `Loan Details`                  | `False`            | `text`         |
| `FixedorVariableInterestInd` | `Borrower Information`          | `False`            | `text`         |
| `terminmonths`               | `Loan Details`                  | `False`            | `numeric`      |
| `naicscode`                  | `unassigned`                    | `False`            | `numeric`      |
| `naicsdescription`           | `unassigned`                    | `False`            | `text`         |
| `franchisecode`              | `Location Data`                 | `True`             | `numeric`      |
| `franchisename`              | `Location Data`                 | `True`             | `categorical`  |
| `projectcounty`              | `Location Data`                 | `True`             | `text`         |
| `projectstate`               | `unassigned`                    | `False`            | `text`         |
| `sbadistrictoffice`          | `Location Data`                 | `True`             | `text`         |
| `congressionaldistrict`      | `Location Data`                 | `True`             | `numeric`      |
| `businesstype`               | `Borrower Information`          | `False`            | `categorical`  |
| `businessage`                | `Borrower Information`          | `False`            | `categorical`  |
| `loanstatus`                 | `Loan Details`                  | `False`            | `categorical`  |
| `paidinfulldate`             | `Borrower Information`          | `False`            | `datetime`     |
| `chargeoffdate`              | `Borrower Information`          | `False`            | `datetime`     |
| `grosschargeoffamount`       | `Loan Details`                  | `False`            | `numeric`      |
| `RevolverStatus`             | `Loan Details`                  | `False`            | `text`         |
| `jobssupported`              | `Borrower Information`          | `False`            | `numeric`      |
| `collateralind`              | `unassigned`                    | `False`            | `numeric`      |
| `SoldSecMrktInd`             | `Loan Details`                  | `False`            | `text`         |
| `cdc_name`                   | `Borrower Information`          | `False`            | `text`         |
| `cdc_street`                 | `Location Data`                 | `True`             | `text`         |
| `cdc_city`                   | `Location Data`                 | `True`             | `text`         |
| `cdc_state`                  | `Location Data`                 | `True`             | `text`         |
| `cdc_zip`                    | `Location Data`                 | `True`             | `numeric`      |
| `thirdpartylender_name`      | `Borrower Information`          | `False`            | `text`         |
| `thirdpartylender_city`      | `Location Data`                 | `True`             | `text`         |
| `thirdpartylender_state`     | `Borrower Information`          | `False`            | `text`         |
| `thirdpartydollars`          | `Borrower Information`          | `False`            | `numeric`      |

---
*Report generated via automated dd-parser post-processing.*