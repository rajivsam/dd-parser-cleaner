# 📑 Data Dictionary: Provisional Entity Assignment Report
**Source Blueprint:** `insurance_dd.csv`

### 📊 Classification Summary
- **BeneficiaryDemographics**: 4 fields
- **HealthStatusAssessment**: 1 fields
- **ResidentialArea**: 1 fields
- **MedicalCosts**: 1 fields

---

### 📋 Detailed Assignments
| Attribute   | Provisional Entity Assignment   | Native Type   |
|-------------|---------------------------------|---------------|
| `age`       | `BeneficiaryDemographics`       | `int`         |
| `sex`       | `BeneficiaryDemographics`       | `str`         |
| `bmi`       | `HealthStatusAssessment`        | `float`       |
| `children`  | `BeneficiaryDemographics`       | `int`         |
| `smoker`    | `BeneficiaryDemographics`       | `str`         |
| `region`    | `ResidentialArea`               | `str`         |
| `charges`   | `MedicalCosts`                  | `float`       |

---
*Report generated via automated dd-parser post-processing.*