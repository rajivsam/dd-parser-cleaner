# 📑 Data Dictionary: Provisional Entity Assignment Report
**Generation Timestamp:** `2026-08-13 08:41:23`
**Source Blueprint:** `itsm_dd.csv`

### 🏗️ Structural Assessment
- **Dataset Type:** `event_log`
> ⚠️ **Note:** This dataset type is provided by configuration and should match your workspace settings. Update `dataset_type` in `config.yaml` if the dataset is actually a panel or longitudinal dataset.

### 📊 Classification Summary
- **Incident Management**: 21 fields
- **User Interaction**: 10 fields
- **unassigned**: 3 fields
- **System Update**: 1 fields

### ⚠️ Orphans in Data Dictionary
> These attributes exist in the dictionary but were **not found** in the raw data file. They have been excluded from the assignments below.

- `close_code`

### 👻 Orphans in Data (Ghosts)
> These headers exist in the raw data file but have **no corresponding entry** in the data dictionary.

- `closed_code`

---

### 📋 Detailed Assignments
| Attribute                 | Assignment            | Static/Dynamic   | Logical Type   | Physical Type   |
|---------------------------|-----------------------|------------------|----------------|-----------------|
| `number`                  | `Incident Management` | dynamic          | `categorical`  | `str`           |
| `incident_state`          | `Incident Management` | dynamic          | `categorical`  | `str`           |
| `active`                  | `unassigned`          | dynamic          | `numeric`      | `float`         |
| `reassignment_count`      | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `reopen_count`            | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `sys_mod_count`           | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `made_sla`                | `Incident Management` | dynamic          | `numeric`      | `float`         |
| `caller_id`               | `User Interaction`    | dynamic          | `categorical`  | `str`           |
| `opened_by`               | `User Interaction`    | dynamic          | `categorical`  | `str`           |
| `opened_at`               | `User Interaction`    | dynamic          | `datetime`     | `datetime`      |
| `sys_created_by`          | `User Interaction`    | dynamic          | `categorical`  | `str`           |
| `sys_created_at`          | `Incident Management` | dynamic          | `datetime`     | `datetime`      |
| `sys_updated_by`          | `User Interaction`    | dynamic          | `datetime`     | `datetime`      |
| `sys_updated_at`          | `System Update`       | dynamic          | `datetime`     | `datetime`      |
| `contact_type`            | `User Interaction`    | dynamic          | `categorical`  | `str`           |
| `location`                | `Incident Management` | dynamic          | `categorical`  | `str`           |
| `category`                | `User Interaction`    | dynamic          | `categorical`  | `str`           |
| `subcategory`             | `Incident Management` | dynamic          | `categorical`  | `str`           |
| `u_symptom`               | `User Interaction`    | dynamic          | `categorical`  | `str`           |
| `cmdb_ci`                 | `Incident Management` | dynamic          | `categorical`  | `str`           |
| `impact`                  | `Incident Management` | dynamic          | `categorical`  | `str`           |
| `urgency`                 | `Incident Management` | dynamic          | `categorical`  | `str`           |
| `priority`                | `Incident Management` | dynamic          | `categorical`  | `str`           |
| `assignment_group`        | `Incident Management` | dynamic          | `categorical`  | `str`           |
| `assigned_to`             | `User Interaction`    | dynamic          | `categorical`  | `str`           |
| `knowledge`               | `unassigned`          | static           | `numeric`      | `float`         |
| `u_priority_confirmation` | `unassigned`          | dynamic          | `numeric`      | `float`         |
| `notify`                  | `Incident Management` | dynamic          | `categorical`  | `str`           |
| `problem_id`              | `Incident Management` | dynamic          | `categorical`  | `str`           |
| `rfc`                     | `Incident Management` | dynamic          | `categorical`  | `str`           |
| `vendor`                  | `Incident Management` | dynamic          | `categorical`  | `str`           |
| `caused_by`               | `Incident Management` | dynamic          | `categorical`  | `str`           |
| `resolved_by`             | `User Interaction`    | dynamic          | `categorical`  | `str`           |
| `resolved_at`             | `Incident Management` | dynamic          | `datetime`     | `datetime`      |
| `closed_at`               | `Incident Management` | dynamic          | `datetime`     | `datetime`      |

---
*Report generated via automated dd-parser post-processing.*