# 🤖 Cleaning Assistant Report

This report provides automated recommendations based on data profile physics (nulls, cardinality) and semantic metadata.

## 🛡️ User Responsibilities
- **Domain Logic**: User must capture domain-specific row filters (exclusions/inclusions) in `config.yaml` or `domain_logic.py`.
- **Domain Deletions**: User must identify and tag columns requiring deletion based on business rules rather than physical stats.
- **Strategy Validation**: While we suggest mean/MISSING defaults, the user is responsible for determining the final imputation strategy per attribute.

## 📊 Summary of Actions
- **constant:MISSING**: 10 columns
- **drop-attribute**: 3 columns
- **custom:datetime_to_numeric**: 3 columns
- **mean-imputation**: 3 columns

## Deletion is recommended for the following attributes

| Attribute     | Type     | Entity      | What Needs Fixing                                         | Recommended Fix   |
|:--------------|:---------|:------------|:----------------------------------------------------------|:------------------|
| asofdate      | datetime | Borrower    | Constant value / Zero variance                            | drop-attribute    |
| program       | numeric  | LoanProgram | Constant value / Zero variance                            | drop-attribute    |
| chargeoffdate | datetime | Borrower    | Extreme sparsity (99.2%): Exceeds null threshold of 95.0% | drop-attribute    |

## Derived attribute definition or deletion is recommended for the following attributes

| Attribute             | Type     | Entity   | What Needs Fixing                                                                                                                                    | Recommended Fix            |
|:----------------------|:---------|:---------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------|
| approvaldate          | datetime | Borrower | This is a cross sectional dataset; if you want to use the datetime attributes, you need to derive numeric attributes from them and then delete them. | custom:datetime_to_numeric |
| firstdisbursementdate | datetime | Borrower | This is a cross sectional dataset; if you want to use the datetime attributes, you need to derive numeric attributes from them and then delete them. | custom:datetime_to_numeric |
| paidinfulldate        | datetime | Borrower | This is a cross sectional dataset; if you want to use the datetime attributes, you need to derive numeric attributes from them and then delete them. | custom:datetime_to_numeric |

## Missing value definition is recommended for the following attributes

### Numeric Attributes (Standard: Mean Imputation)

| Attribute             | Type    | Entity            | What Needs Fixing                                            | Recommended Fix   |
|:----------------------|:--------|:------------------|:-------------------------------------------------------------|:------------------|
| naicscode             | numeric | LenderInformation | Numeric with 0.4% nulls: Recommendation is mean imputation.  | mean-imputation   |
| franchisecode         | numeric | LenderInformation | Numeric with 90.2% nulls: Recommendation is mean imputation. | mean-imputation   |
| congressionaldistrict | numeric | LoanProgram       | Numeric with 0.0% nulls: Recommendation is mean imputation.  | mean-imputation   |

### Categorical Attributes (Standard: 'MISSING' Category)

| Attribute              | Type        | Entity            | What Needs Fixing                                                                   | Recommended Fix   |
|:-----------------------|:------------|:------------------|:------------------------------------------------------------------------------------|:------------------|
| thirdpartylender_name  | text        | LenderInformation | Categorical/Text with 0.3% nulls: Recommendation is creating a 'MISSING' category.  | constant:MISSING  |
| thirdpartylender_city  | text        | LenderInformation | Categorical/Text with 0.3% nulls: Recommendation is creating a 'MISSING' category.  | constant:MISSING  |
| thirdpartylender_state | categorical | LenderInformation | Categorical/Text with 0.3% nulls: Recommendation is creating a 'MISSING' category.  | constant:MISSING  |
| subprogram             | categorical | Borrower          | Categorical/Text with 6.8% nulls: Recommendation is creating a 'MISSING' category.  | constant:MISSING  |
| naicsdescription       | text        | Borrower          | Categorical/Text with 0.4% nulls: Recommendation is creating a 'MISSING' category.  | constant:MISSING  |
| franchisename          | categorical | LenderInformation | Categorical/Text with 90.2% nulls: Recommendation is creating a 'MISSING' category. | constant:MISSING  |
| sbadistrictoffice      | categorical | LoanProgram       | Categorical/Text with 0.0% nulls: Recommendation is creating a 'MISSING' category.  | constant:MISSING  |
| businesstype           | categorical | Borrower          | Categorical/Text with 0.0% nulls: Recommendation is creating a 'MISSING' category.  | constant:MISSING  |
| businessage            | categorical | Borrower          | Categorical/Text with 0.5% nulls: Recommendation is creating a 'MISSING' category.  | constant:MISSING  |
| loanstatus             | categorical | Borrower          | Categorical/Text with 0.2% nulls: Recommendation is creating a 'MISSING' category.  | constant:MISSING  |


---
*Generated by CleaningAssistant engine.*