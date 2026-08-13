# Tabular Data Type Decision Tree

This is the simple decision path used by the project to classify tabular datasets.

The key idea is that there are two separate questions:

1. What kind of dataset is it in time/subject terms?
2. Is it also a wide-short dataset in shape terms?

These are related, but they are not the same thing.

---

## Start here

### 1. Is this a graph dataset or a tabular dataset?

- If it is a graph dataset, follow the graph workflow.
- If it is a tabular dataset, continue below.

---

### 2. Does one row represent one subject at one point in time?

- No -> treat it as an event log
- Yes -> continue

Why this matters:
- Event logs usually record actions, interactions, or transactions.
- A snapshot dataset usually records a subject at a single time point.

---

### 3. Are all subjects measured at the same point in time?

- Yes -> cross-sectional
- No -> panel

Examples:
- Cross-sectional: a single snapshot of customers, students, or devices
- Panel: the same people or entities are observed repeatedly over time

---

## Wide-short check

This part is separate from the dataset type.

### 4. Is the table wide and short?

Ask:
- Are there relatively few rows?
- Are there many columns?
- Is there one main representative field or anchor column?
- Do repeated groups of attributes cluster around that field?

If the answer is yes, classify it as wide-short.

If no, it is not wide-short.

Examples of wide-short shape:
- one row per subject
- many repeated columns around a central base field
- compact table with a large number of measured attributes

---

## Decision tree summary

```text
Start
│
├─ Is this a graph dataset?
│  ├─ Yes -> graph workflow
│  └─ No -> continue
│
├─ Does one row represent one subject at one point in time?
│  ├─ No -> event log
│  └─ Yes -> continue
│
├─ Are all subjects measured at the same point in time?
│  ├─ Yes -> cross-sectional
│  └─ No -> panel
│
└─ Is the table also wide-short?
   ├─ Yes -> wide-short + dataset type
   └─ No -> normal tabular dataset
```

---

## Simple rule of thumb

- Cross-sectional = snapshot
- Panel = repeated observations over time
- Event log = actions or transactions
- Wide-short = compact table with many repeated fields

A dataset can be both cross-sectional and wide-short, or panel and wide-short. The two labels answer different questions.

---

## Why this matters

The metadata is stored separately:

- dataset_type
- wide_short_homogeneous
- wide_short_representative_column

This lets the parser and cleaner apply the right logic for time-based datasets and for compact wide-short tables.

---

## Final takeaway

The project does not treat wide-short as a replacement for dataset type.

Instead, it resolves:

- dataset type = time/subject structure
- wide-short = table shape pattern

Then both are recorded and used downstream.
