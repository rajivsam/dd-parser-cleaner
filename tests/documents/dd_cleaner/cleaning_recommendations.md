# 🤖 Cleaning Assistant Report

This report provides automated recommendations based on data profile physics and semantic metadata.

## 🛡️ User Responsibilities
- **Domain Logic**: User should capture domain-specific row filters in `config.yaml` or via an optional external custom logic module referenced explicitly in configuration.
- **Domain Deletions**: User must identify columns requiring deletion based on business rules.
- **Strategy Validation**: While we suggest mean/MISSING defaults, the user determines the final strategy.

## 📊 Summary of Actions
- **drop-attribute**: 43 columns

## Deletion is recommended for the following attributes

| Attribute                  | Type     | Entity             | What Needs Fixing              | Recommended Fix   |
|:---------------------------|:---------|:-------------------|:-------------------------------|:------------------|
| AsOfDate                   | datetime | Logical Category   | Constant value / Zero variance | drop-attribute    |
| Program                    | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| LocationID                 | numeric  | Logical Category   | Constant value / Zero variance | drop-attribute    |
| BorrName                   | numeric  | Person             | Constant value / Zero variance | drop-attribute    |
| BorrStreet                 | numeric  | geographic         | Constant value / Zero variance | drop-attribute    |
| BorrCity                   | numeric  | Geographic         | Constant value / Zero variance | drop-attribute    |
| BorrState                  | numeric  | Logical Category   | Constant value / Zero variance | drop-attribute    |
| BorrZip                    | numeric  | geographic         | Constant value / Zero variance | drop-attribute    |
| BankName                   | numeric  | Logical Category   | Constant value / Zero variance | drop-attribute    |
| BankFDICNumber             | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| BankNCUANumber             | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| BankStreet                 | numeric  | geographic         | Constant value / Zero variance | drop-attribute    |
| BankCity                   | numeric  | Geographic         | Constant value / Zero variance | drop-attribute    |
| BankState                  | numeric  | Logical Category   | Constant value / Zero variance | drop-attribute    |
| BankZip                    | numeric  | Geographic         | Constant value / Zero variance | drop-attribute    |
| GrossApproval              | numeric  | Logical Category   | Constant value / Zero variance | drop-attribute    |
| SBAGuaranteedApproval      | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| ApprovalDate               | datetime | Logical Category   | Constant value / Zero variance | drop-attribute    |
| ApprovalFY                 | numeric  | Logical Category   | Constant value / Zero variance | drop-attribute    |
| FirstDisbursementDate      | numeric  | date               | Constant value / Zero variance | drop-attribute    |
| ProcessingMethod           | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| Subprogram                 | numeric  | Logical Category   | Constant value / Zero variance | drop-attribute    |
| InitialInterestRate        | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| FixedorVariableInterestInd | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| TermInMonths               | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| NaicsCode                  | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| NaicsDescription           | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| FranchiseCode              | numeric  | Logical Category   | Constant value / Zero variance | drop-attribute    |
| FranchiseName              | numeric  | Conceptual Entity  | Constant value / Zero variance | drop-attribute    |
| ProjectCounty              | numeric  | Logical Category   | Constant value / Zero variance | drop-attribute    |
| ProjectState               | numeric  | Logical Category   | Constant value / Zero variance | drop-attribute    |
| SBADistrictOffice          | numeric  | Logical Category   | Constant value / Zero variance | drop-attribute    |
| CongressionalDistrict      | numeric  | Geographic         | Constant value / Zero variance | drop-attribute    |
| BusinessType               | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| BusinessAge                | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| LoanStatus                 | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| PaidInFullDate             | numeric  | Logical Category   | Constant value / Zero variance | drop-attribute    |
| ChargeOffDate              | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| GrossChargeOffAmount       | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| RevolverStatus             | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| JobsSupported              | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| CollateralInd              | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |
| SoldSecMrktInd             | numeric  | Logical Categories | Constant value / Zero variance | drop-attribute    |


---
*Generated by CleaningAssistant engine.*