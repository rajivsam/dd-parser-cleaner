# 📑 Data Dictionary: Provisional Entity Assignment Report
**Source Blueprint:** `sba_dd.csv`

### 📊 Classification Summary
- **Borrower Information**: 24 fields
- **Location Data**: 14 fields
- **unassigned**: 6 fields
- **Bank Information**: 5 fields
- **Loan Program Details**: 3 fields
- **Lender**: 1 fields

---

### 📋 Detailed Assignments
| Attribute                    | Provisional Entity Assignment   | Flag: Geographic   | Logical Type   |
|------------------------------|---------------------------------|--------------------|----------------|
| `asofdate`                   | `Borrower Information`          | `False`            | `categorical`  |
| `program`                    | `Loan Program Details`          | `False`            | `numeric`      |
| `locationid`                 | `Lender`                        | `False`            | `numeric`      |
| `borrname`                   | `Borrower Information`          | `False`            | `text`         |
| `borrstreet`                 | `Borrower Information`          | `True`             | `text`         |
| `borrcity`                   | `Location Data`                 | `True`             | `text`         |
| `borrstate`                  | `Borrower Information`          | `True`             | `text`         |
| `borrzip`                    | `Borrower Information`          | `True`             | `numeric`      |
| `BankName`                   | `Bank Information`              | `False`            | `text`         |
| `BankFDICNumber`             | `Bank Information`              | `False`            | `text`         |
| `BankNCUANumber`             | `Bank Information`              | `False`            | `text`         |
| `BankStreet`                 | `Location Data`                 | `True`             | `text`         |
| `BankCity`                   | `Location Data`                 | `True`             | `text`         |
| `BankState`                  | `Bank Information`              | `True`             | `text`         |
| `BankZip`                    | `Bank Information`              | `True`             | `text`         |
| `grossapproval`              | `Borrower Information`          | `False`            | `numeric`      |
| `SBAGuaranteedApproval`      | `Borrower Information`          | `False`            | `text`         |
| `approvaldate`               | `Borrower Information`          | `False`            | `categorical`  |
| `approvalfy`                 | `unassigned`                    | `False`            | `numeric`      |
| `firstdisbursementdate`      | `Borrower Information`          | `False`            | `categorical`  |
| `processingmethod`           | `Loan Program Details`          | `False`            | `categorical`  |
| `nan`                        | `Borrower Information`          | `False`            | `text`         |
| `subprogram`                 | `Loan Program Details`          | `False`            | `categorical`  |
| `InitialInterestRate`        | `Borrower Information`          | `False`            | `text`         |
| `FixedorVariableInterestInd` | `Borrower Information`          | `False`            | `text`         |
| `terminmonths`               | `Borrower Information`          | `False`            | `numeric`      |
| `naicscode`                  | `unassigned`                    | `False`            | `numeric`      |
| `naicsdescription`           | `unassigned`                    | `False`            | `text`         |
| `franchisecode`              | `Location Data`                 | `True`             | `numeric`      |
| `franchisename`              | `Location Data`                 | `True`             | `categorical`  |
| `projectcounty`              | `Location Data`                 | `True`             | `text`         |
| `projectstate`               | `unassigned`                    | `True`             | `text`         |
| `sbadistrictoffice`          | `Location Data`                 | `True`             | `text`         |
| `congressionaldistrict`      | `Location Data`                 | `True`             | `numeric`      |
| `businesstype`               | `Borrower Information`          | `False`            | `categorical`  |
| `businessage`                | `Borrower Information`          | `False`            | `categorical`  |
| `loanstatus`                 | `Borrower Information`          | `False`            | `categorical`  |
| `paidinfulldate`             | `Borrower Information`          | `False`            | `text`         |
| `chargeoffdate`              | `Borrower Information`          | `False`            | `categorical`  |
| `grosschargeoffamount`       | `Borrower Information`          | `False`            | `numeric`      |
| `RevolverStatus`             | `unassigned`                    | `False`            | `text`         |
| `jobssupported`              | `Borrower Information`          | `False`            | `numeric`      |
| `collateralind`              | `unassigned`                    | `True`             | `numeric`      |
| `SoldSecMrktInd`             | `Borrower Information`          | `False`            | `text`         |
| `cdc_name`                   | `Borrower Information`          | `False`            | `text`         |
| `cdc_street`                 | `Location Data`                 | `True`             | `text`         |
| `cdc_city`                   | `Location Data`                 | `True`             | `text`         |
| `cdc_state`                  | `Location Data`                 | `True`             | `text`         |
| `cdc_zip`                    | `Location Data`                 | `True`             | `numeric`      |
| `thirdpartylender_name`      | `Borrower Information`          | `False`            | `text`         |
| `thirdpartylender_city`      | `Location Data`                 | `True`             | `text`         |
| `thirdpartylender_state`     | `Location Data`                 | `True`             | `text`         |
| `thirdpartydollars`          | `Borrower Information`          | `False`            | `numeric`      |

---
*Report generated via automated dd-parser post-processing.*