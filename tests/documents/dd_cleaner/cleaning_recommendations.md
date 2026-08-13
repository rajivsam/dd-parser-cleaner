# 🤖 Cleaning Assistant Report

This report provides automated recommendations based on data profile physics and semantic metadata.

## 🛡️ User Responsibilities
- **Domain Logic**: User should capture domain-specific row filters in `config.yaml` or via an optional external custom logic module referenced explicitly in configuration.
- **Domain Deletions**: User must identify columns requiring deletion based on business rules.
- **Strategy Validation**: While we suggest mean/MISSING defaults, the user determines the final strategy.

## 📊 Summary of Actions
- **constant:MISSING**: 7 columns
- **drop-attribute**: 3 columns
- **custom:datetime_to_numeric**: 3 columns
- **mean-imputation**: 3 columns

## Deletion is recommended for the following attributes

| Attribute     | Type     | Entity             | What Needs Fixing                                         | Recommended Fix   |
|:--------------|:---------|:-------------------|:----------------------------------------------------------|:------------------|
| asofdate      | datetime | Logical Categories | Constant value / Zero variance                            | drop-attribute    |
| program       | numeric  | Logical Categories | Constant value / Zero variance                            | drop-attribute    |
| chargeoffdate | datetime | Logical Categories | Extreme sparsity (99.2%): Exceeds null threshold of 95.0% | drop-attribute    |

## Derived attribute definition or deletion is recommended

| Attribute             | Type     | Entity             | What Needs Fixing                                                                                                                                    | Recommended Fix            |
|:----------------------|:---------|:-------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------|
| approvaldate          | datetime | Logical Categories | This is a cross sectional dataset; if you want to use the datetime attributes, you need to derive numeric attributes from them and then delete them. | custom:datetime_to_numeric |
| firstdisbursementdate | datetime | Person             | This is a cross sectional dataset; if you want to use the datetime attributes, you need to derive numeric attributes from them and then delete them. | custom:datetime_to_numeric |
| paidinfulldate        | datetime | Logical Category   | This is a cross sectional dataset; if you want to use the datetime attributes, you need to derive numeric attributes from them and then delete them. | custom:datetime_to_numeric |

## Missing value definition is recommended for the following attributes

### Numeric Attributes (Standard: Mean Imputation)

| Attribute             | Type    | Entity             | What Needs Fixing                                            | Recommended Fix   |
|:----------------------|:--------|:-------------------|:-------------------------------------------------------------|:------------------|
| naicscode             | numeric | Logical Categories | Numeric with 0.4% nulls: Recommendation is mean imputation.  | mean-imputation   |
| franchisecode         | numeric | Logical Categories | Numeric with 90.2% nulls: Recommendation is mean imputation. | mean-imputation   |
| congressionaldistrict | numeric | geographic         | Numeric with 0.0% nulls: Recommendation is mean imputation.  | mean-imputation   |

### Categorical Attributes (Standard: 'MISSING' Category)

| Attribute         | Type        | Entity             | What Needs Fixing                                                                   | Recommended Fix   |
|:------------------|:------------|:-------------------|:------------------------------------------------------------------------------------|:------------------|
| subprogram        | categorical | Logical Categories | Categorical/Text with 6.8% nulls: Recommendation is creating a 'MISSING' category.  | constant:MISSING  |
| naicsdescription  | text        | Logical Categories | Categorical/Text with 0.4% nulls: Recommendation is creating a 'MISSING' category.  | constant:MISSING  |
| franchisename     | categorical | Organization       | Categorical/Text with 90.2% nulls: Recommendation is creating a 'MISSING' category. | constant:MISSING  |
| sbadistrictoffice | categorical | Conceptual Entity  | Categorical/Text with 0.0% nulls: Recommendation is creating a 'MISSING' category.  | constant:MISSING  |
| businesstype      | categorical | Logical Categories | Categorical/Text with 0.0% nulls: Recommendation is creating a 'MISSING' category.  | constant:MISSING  |
| businessage       | categorical | Logical Categories | Categorical/Text with 0.5% nulls: Recommendation is creating a 'MISSING' category.  | constant:MISSING  |
| loanstatus        | categorical | Logical Categories | Categorical/Text with 0.2% nulls: Recommendation is creating a 'MISSING' category.  | constant:MISSING  |


---
*Generated by CleaningAssistant engine.*