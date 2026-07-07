# Comprehensive Design Document: dd-parser-cleaner

## Purpose

The `dd-parser-cleaner` package provides a modular framework for dataset discovery, metadata bootstrapping, schema alignment, cleaning, and readiness signaling. It ensures that downstream featurization and modeling pipelines receive standardized, validated inputs.

---

## Design Principles

- **Raw data immutability**: Never overwrite source data.
- **Handshake contract**: Explicit readiness signaling between parser, cleaner, and featurizer.
- **Domain agnosticism**: Works across cross-sectional, event log, panel, and wide-short homogeneous datasets.
- **Config as law**: All behavior driven by manifest and config files.
- **Strict JSON-only LLM responses**: Deterministic, machine-readable outputs.

---

## Bootstrapping Phase

### Dataset Type Identification

1. **Graph vs Tabular**

   - Graph: Out of scope for v1.
   - Tabular: Proceed to subtype classification.
2. **Subtype Classification**

   - Cross-sectional
   - Event log
   - Panel (long form)
3. **Homogeneity Check (New)**

   - Ask: *“Is this a wide-and-short dataset with many homogeneous columns (e.g., sensor readings, survey matrices, embeddings)?”*
   - If **Yes**:
     - Set `manifest.notes.structure = "wide_short_homogeneous"`
     - Set `manifest.flags.skip_columnwise_intelligence = true`
     - Ask user to specify a **representative column**.
     - Parser generates intelligence for that column only.
     - Apply intelligence across all homogeneous columns.
   - If **No**:
     - Proceed with column-by-column intelligence gathering.

---

## Parsing & Schema Alignment

- Infer data types from representative column (if homogeneous) or each column (if heterogeneous).
- Generate dataset manifest with:
  - `dataset_type`
  - `notes.subject`
  - `notes.structure`
  - `attribute_manifest`
- Store representative column metadata for homogeneous datasets.

---

## Cleaning & Validation

- Apply validation rules:
  - **Cross-sectional**: static consistency checks.
  - **Event log**: monotonicity, lag consistency, gap detection.
  - **Panel**: static vs dynamic attribute validation.
  - **Wide-short homogeneous**: bulk validation rules applied across grouped columns.
- Cleaning recommendations remain identical, applied in bulk for homogeneous datasets.

---

## Handshake Contract

- Generate `handshake.json` with status:
  - `ready`: dataset validated and featurizer may proceed.
  - `blocked`: critical errors prevent downstream processing.
  - `warnings`: non-critical issues logged.

---

## Manifest Schema Example

```yaml
dataset_type: cross_sectional
notes:
  subject: customer
  structure: wide_short_homogeneous
flags:
  skip_columnwise_intelligence: true
attribute_manifest:
  - group_name: survey_responses
    representative_column: Q1_response
    data_type: integer
    validation_rules: [bounded_range, non_negative]
    count_columns: 800
```
