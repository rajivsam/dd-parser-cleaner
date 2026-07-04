# 📑 Data Dictionary: Provisional Entity Assignment Report
**Generation Timestamp:** `2026-05-30 10:15:48`
**Source Blueprint:** `sba_dd.csv`

### 🏗️ Structural Assessment
- **Dataset Type:** `cross-sectional`
> ⚠️ **Note:** This dataset type is defined in configuration. Update `cleaner.structural_assessment.dataset_type` in `config.yaml` if the dataset is actually a panel.

### 📊 Classification Summary
- **BorrowerInformation**: 1 fields
- **LocationMetadata**: 1 fields
- **LoanApplication**: 1 fields
- **ProgramIndicator**: 1 fields

### ⚠️ CRITICAL SCHEMA MISMATCH (Orphaned Attributes)
> The following attributes were found in your Data Dictionary but are missing from the raw data file. They have been **excluded** from the operational cleaning matrix.

- `AsOfDate`
- `Program`
- `LocationID`
- `BorrName`
- `BorrStreet`
- `BorrCity`
- `BorrState`
- `BorrZip`
- `BankName`
- `BankFDICNumber`
- `BankNCUANumber`
- `BankStreet`
- `BankCity`
- `BankState`
- `BankZip`
- `GrossApproval`
- `SBAGuaranteedApproval`
- `ApprovalDate`
- `ApprovalFY`
- `FirstDisbursementDate`
- `ProcessingMethod`
- `Subprogram`
- `InitialInterestRate`
- `FixedorVariableInterestInd`
- `TermInMonths`
- `NaicsDescription`
- `FranchiseCode`
- `FranchiseName`
- `ProjectCounty`
- `ProjectState`
- `SBADistrictOffice`
- `CongressionalDistrict`
- `BusinessType`
- `BusinessAge`
- `LoanStatus`
- `PaidInFullDate`
- `ChargeOffDate`
- `GrossChargeOffAmount`
- `RevolverStatus`
- `JobsSupported`
- `CollateralInd`
- `SoldSecMrktInd`


---

### 📋 Detailed Assignments
| Attribute               | Assignment            | Logical Type   | Physical Type   | Flag: Geographic   |
|-------------------------|-----------------------|----------------|-----------------|--------------------|
| `nan`                   | `BorrowerInformation` | `unknown`      | `unknown`       | `False`            |
| `naics_code`            | `LocationMetadata`    | `numeric`      | `int`           | `True`             |
| `gross_approval_amount` | `LoanApplication`     | `numeric`      | `int`           | `False`            |
| `loan_program`          | `ProgramIndicator`    | `text`         | `str`           | `False`            |

---
*Report generated via automated dd-parser post-processing.*