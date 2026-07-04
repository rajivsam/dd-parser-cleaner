# 📑 Data Dictionary: Provisional Entity Assignment Report
**Generation Timestamp:** `2026-07-04 11:54:43`
**Source Blueprint:** `itsm_dd.csv`

### 🏗️ Structural Assessment
- **Dataset Type:** `panel`
> ⚠️ **Note:** This dataset type is provided by configuration and should match your workspace settings. Update `dataset_type` in `config.yaml` if the dataset is actually a panel or longitudinal dataset.

### 📊 Classification Summary
- **Incident Management**: 4 fields
- **Support Group**: 1 fields
- **unassigned**: 1 fields

### ⚠️ Orphans in Data Dictionary
> These attributes exist in the dictionary but were **not found** in the raw data file. They have been excluded from the assignments below.

- `active`
- `reassignment_count`
- `reopen_count`
- `sys_mod_count`
- `made_sla`
- `caller_id`
- `opened_by`
- `sys_created_by`
- `sys_created_at`
- `sys_updated_by`
- `sys_updated_at`
- `contact_type`
- `location`
- `category`
- `subcategory`
- `u_symptom`
- `cmdb_ci`
- `impact`
- `urgency`
- `priority`
- `assigned_to`
- `knowledge`
- `u_priority_confirmation`
- `notify`
- `problem_id`
- `rfc`
- `vendor`
- `caused_by`
- `close_code`
- `resolved_by`

---

### 📋 Detailed Assignments
| Attribute          | Assignment            | Static/Dynamic   | Logical Type   | Physical Type   |
|--------------------|-----------------------|------------------|----------------|-----------------|
| `number`           | `Incident Management` | static           | `categorical`  | `str`           |
| `incident_state`   | `Incident Management` | dynamic          | `categorical`  | `str`           |
| `opened_at`        | `Incident Management` | dynamic          | `datetime`     | `datetime`      |
| `assignment_group` | `Support Group`       | static           | `categorical`  | `str`           |
| `resolved_at`      | `Incident Management` | dynamic          | `datetime`     | `datetime`      |
| `closed_at`        | `unassigned`          | dynamic          | `datetime`     | `datetime`      |

---
*Report generated via automated dd-parser post-processing.*