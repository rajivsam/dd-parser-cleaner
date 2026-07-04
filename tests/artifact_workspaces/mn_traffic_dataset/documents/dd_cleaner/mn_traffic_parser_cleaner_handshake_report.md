# 📑 Data Dictionary: Provisional Entity Assignment Report
**Generation Timestamp:** `2026-07-04 11:54:12`
**Source Blueprint:** `MN_traffic_dd.csv`

### 🏗️ Structural Assessment
- **Dataset Type:** `panel`
> ⚠️ **Note:** This dataset type is provided by configuration and should match your workspace settings. Update `dataset_type` in `config.yaml` if the dataset is actually a panel or longitudinal dataset.

### 📊 Classification Summary
- **Environmental Conditions**: 6 fields
- **Regional Events**: 1 fields
- **Time and Date**: 1 fields
- **Traffic Volume**: 1 fields

---

### 📋 Detailed Assignments
| Attribute             | Assignment                 | Static/Dynamic   | Logical Type   | Physical Type   |
|-----------------------|----------------------------|------------------|----------------|-----------------|
| `holiday`             | `Regional Events`          | dynamic          | `categorical`  | `str`           |
| `temp`                | `Environmental Conditions` | static           | `numeric`      | `float`         |
| `rain_1h`             | `Environmental Conditions` | static           | `numeric`      | `float`         |
| `snow_1h`             | `Environmental Conditions` | static           | `numeric`      | `float`         |
| `clouds_all`          | `Environmental Conditions` | static           | `numeric`      | `int`           |
| `weather_main`        | `Environmental Conditions` | static           | `categorical`  | `str`           |
| `weather_description` | `Environmental Conditions` | static           | `categorical`  | `str`           |
| `date_time`           | `Time and Date`            | dynamic          | `datetime`     | `datetime`      |
| `traffic_volume`      | `Traffic Volume`           | static           | `numeric`      | `int`           |

---
*Report generated via automated dd-parser post-processing.*