# 📊 Data Quality Profile & Null Analysis
**Report Generated**: `2026-08-13 08:41:52`

**Total Attributes Profiled**: 35

## Attribute Completeness Matrix
| Attribute               | Logical Type   |   Null Count | Null %   |   Unique | Samples                                                                             |
|:------------------------|:---------------|-------------:|:---------|---------:|:------------------------------------------------------------------------------------|
| number                  | categorical    |            0 | 0.00%    |    24918 | INC0000045, INC0000047, INC0000057, INC0000060, INC0000062                          |
| incident_state          | categorical    |            0 | 0.00%    |        9 | New, Resolved, Closed, Active, Awaiting User Info                                   |
| active                  | numeric        |            0 | 0.00%    |        2 | True, False                                                                         |
| reassignment_count      | numeric        |            0 | 0.00%    |       28 | 0, 1, 2, 3, 4                                                                       |
| reopen_count            | numeric        |            0 | 0.00%    |        9 | 0, 1, 2, 3, 4                                                                       |
| sys_mod_count           | numeric        |            0 | 0.00%    |      115 | 0, 2, 3, 4, 1                                                                       |
| made_sla                | numeric        |            0 | 0.00%    |        2 | True, False                                                                         |
| caller_id               | categorical    |            0 | 0.00%    |     5245 | Caller 2403, Caller 4416, Caller 4491, Caller 3765, Caller 2146                     |
| opened_by               | categorical    |            0 | 0.00%    |      208 | Opened by  8, Opened by  397, Opened by  180, Opened by  131, Opened by  24         |
| opened_at               | datetime       |            0 | 0.00%    |    19849 | 29/2/2016 01:16, 29/2/2016 04:40, 29/2/2016 06:10, 29/2/2016 06:38, 29/2/2016 06:58 |
| sys_created_by          | categorical    |            0 | 0.00%    |      186 | Created by 6, Created by 171, ?, Created by 81, Created by 62                       |
| sys_created_at          | datetime       |            0 | 0.00%    |    11553 | 29/2/2016 01:23, 29/2/2016 04:57, ?, 29/2/2016 06:42, 29/2/2016 07:26               |
| sys_updated_by          | datetime       |            0 | 0.00%    |      846 | Updated by 21, Updated by 642, Updated by 804, Updated by 908, Updated by 746       |
| sys_updated_at          | datetime       |            0 | 0.00%    |    50664 | 29/2/2016 01:23, 29/2/2016 08:53, 29/2/2016 11:29, 5/3/2016 12:00, 29/2/2016 04:57  |
| contact_type            | categorical    |            0 | 0.00%    |        5 | Phone, Email, Self service, Direct opening, IVR                                     |
| location                | categorical    |            0 | 0.00%    |      225 | Location 143, Location 165, Location 204, Location 93, Location 108                 |
| category                | categorical    |            0 | 0.00%    |       59 | Category 55, Category 40, Category 20, Category 9, Category 53                      |
| subcategory             | categorical    |            0 | 0.00%    |      255 | Subcategory 170, Subcategory 215, Subcategory 125, Subcategory 97, Subcategory 168  |
| u_symptom               | categorical    |            0 | 0.00%    |      526 | Symptom 72, Symptom 471, Symptom 450, Symptom 232, Symptom 580                      |
| cmdb_ci                 | categorical    |            0 | 0.00%    |       51 | ?, cmdb_ci 31, cmdb_ci 23, cmdb_ci 22, cmdb_ci 6                                    |
| impact                  | categorical    |            0 | 0.00%    |        3 | 2 - Medium, 1 - High, 3 - Low                                                       |
| urgency                 | categorical    |            0 | 0.00%    |        3 | 2 - Medium, 3 - Low, 1 - High                                                       |
| priority                | categorical    |            0 | 0.00%    |        4 | 3 - Moderate, 2 - High, 4 - Low, 1 - Critical                                       |
| assignment_group        | categorical    |            0 | 0.00%    |       79 | Group 56, Group 70, Group 24, Group 25, Group 23                                    |
| assigned_to             | categorical    |            0 | 0.00%    |      235 | ?, Resolver 89, Resolver 31, Resolver 6, Resolver 125                               |
| knowledge               | numeric        |            0 | 0.00%    |        2 | True, False                                                                         |
| u_priority_confirmation | numeric        |            0 | 0.00%    |        2 | False, True                                                                         |
| notify                  | categorical    |            0 | 0.00%    |        2 | Do Not Notify, Send Email                                                           |
| problem_id              | categorical    |            0 | 0.00%    |      253 | ?, Problem ID  2, Problem ID  4, Problem ID  44, Problem ID  141                    |
| rfc                     | categorical    |            0 | 0.00%    |      182 | ?, CHG0000404, CHG0000647, CHG0000127, CHG0000646                                   |
| vendor                  | categorical    |            0 | 0.00%    |        5 | ?, code 8s, Vendor 3, Vendor 2, Vendor 1                                            |
| caused_by               | categorical    |            0 | 0.00%    |        4 | ?, CHG0000132, CHG0000097, CHG0001327                                               |
| resolved_by             | categorical    |            0 | 0.00%    |      217 | Resolved by 149, Resolved by 81, Resolved by 5, Resolved by 113, Resolved by 62     |
| resolved_at             | datetime       |            0 | 0.00%    |    18506 | 29/2/2016 11:29, 1/3/2016 09:52, 1/3/2016 02:55, 2/3/2016 12:06, 29/2/2016 15:51    |
| closed_at               | datetime       |            0 | 0.00%    |     2707 | 5/3/2016 12:00, 6/3/2016 10:00, 6/3/2016 03:00, 7/3/2016 13:00, 5/3/2016 16:00      |

---

*Generated by dd-parser-cleaner Integrity Engine.*