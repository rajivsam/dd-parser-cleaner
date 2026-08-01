# 📑 Data Dictionary: Provisional Entity Assignment Report
**Generation Timestamp:** `2026-08-01 14:27:05`
**Source Blueprint:** `itsm_dd.csv`

### 🏗️ Structural Assessment
- **Dataset Type:** `event_log`
> ⚠️ **Note:** This dataset type is provided by configuration and should match your workspace settings. Update `dataset_type` in `config.yaml` if the dataset is actually a panel or longitudinal dataset.

### 📊 Classification Summary
- **Incident Management**: 25 fields
- **User Interaction**: 10 fields
- **System Update**: 1 fields

---

### 📋 Detailed Assignments
| Attribute                 | Assignment            | Static/Dynamic   | Logical Type   | Physical Type   |
|---------------------------|-----------------------|------------------|----------------|-----------------|
| `number`                  | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `incident_state`          | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `active`                  | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `reassignment_count`      | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `reopen_count`            | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `sys_mod_count`           | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `made_sla`                | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `caller_id`               | `User Interaction`    | dynamic          | `numeric`      | `int`           |
| `opened_by`               | `User Interaction`    | dynamic          | `numeric`      | `int`           |
| `opened_at`               | `User Interaction`    | dynamic          | `datetime`     | `datetime`      |
| `sys_created_by`          | `User Interaction`    | dynamic          | `numeric`      | `int`           |
| `sys_created_at`          | `Incident Management` | dynamic          | `datetime`     | `datetime`      |
| `sys_updated_by`          | `User Interaction`    | dynamic          | `numeric`      | `int`           |
| `sys_updated_at`          | `System Update`       | dynamic          | `datetime`     | `datetime`      |
| `contact_type`            | `User Interaction`    | dynamic          | `numeric`      | `int`           |
| `location`                | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `category`                | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `subcategory`             | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `u_symptom`               | `User Interaction`    | dynamic          | `numeric`      | `int`           |
| `cmdb_ci`                 | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `impact`                  | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `urgency`                 | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `priority`                | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `assignment_group`        | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `assigned_to`             | `User Interaction`    | dynamic          | `numeric`      | `int`           |
| `knowledge`               | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `u_priority_confirmation` | `User Interaction`    | dynamic          | `numeric`      | `int`           |
| `notify`                  | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `problem_id`              | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `rfc`                     | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `vendor`                  | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `caused_by`               | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `close_code`              | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `resolved_by`             | `User Interaction`    | dynamic          | `numeric`      | `int`           |
| `resolved_at`             | `Incident Management` | dynamic          | `numeric`      | `int`           |
| `closed_at`               | `Incident Management` | dynamic          | `numeric`      | `int`           |

---
*Report generated via automated dd-parser post-processing.*