## 📑 Data Dictionary Parser Architecture (High-Level Brief)

This parser is a Human-in-the-Loop (HITL) automation asset designed to eliminate 90% of spreadsheet busywork when onboarding raw datasets. It processes unstructured column metadata definitions into structured schema mapping matrices and feature-routing blueprints.

---

## 🔎 The 3 Core Processing Passes

The parser evaluates a data dictionary via three sequential execution layers:

```text
  [Input File] 
       │
       ▼
 ┌───────────┐
 │  Pass 1   │ ──► Heuristic File Structure Extraction & Cell Cleansing
 └─────┬─────┘
       │
       ▼
 ┌───────────┐
 │  Pass 2   │ ──► Coarse Domain Entity Identification via Local Llama 3.2
 └─────┬─────┘
       │
       ▼
 ┌───────────┐
 │  Pass 3   │ ──► Prefix-Stripping Feature Pipeline Capability Routing
 └─────┬─────┘
       │
       ▼
  [Output Matrix]
```

## 📦 Pass 1: Structural Extraction & Cleansing

* What it does: Scans the input file (supporting CSV format or fragmented text/PDF extraction arrays) without hardcoded header name assumptions.
* Outcome: Heuristically isolates the raw attribute identifiers and automatically measures description text density to pinpoint the context cells. All unpopulated fields are typed securely to prevent downstream processing crashes.

## 🧠 Pass 2: Coarse Domain Entity Graph Classification

* What it does: Contextualizes variables holistically into high-level business entity buckets (e.g., `Borrower`, `Lender`, `Loan`) by running the extracted text payloads against local zero-shot semantic models.
* Outcome: Populates the `provisional_entity_assignment` label column. This allows developers to construct provisional graph database topologies from raw files immediately.

## 🧼 Pass 3: Prefix-Stripping Feature Capability Routing

* What it does: Strips known structural abbreviation prefixes (e.g., mapping `BorrZip` to `Zip` or `BankStreet` to `Street`) before running rule validations.
* Outcome: Populates individual boolean capability flags (e.g., `is_geographic`) to cleanly route extracted columns to their respective downstream featurization pipelines.

---

## 🎯 The Authoritative Override Layer

Before executing the inference steps (Pass 2 and Pass 3), the parser checks a user-managed dictionary inside `config.yaml`.

```yaml
parser:
  overrides:
    LocationID:
      provisional_entity_assignment: "Lender"
      is_geographic: false
```

* If an attribute name matches an explicit override key, the inference pipeline is bypassed completely for that row.
* The parser directly injects the user's hardcoded definitions into the final matrix, serving as an absolute safety valve for complex edge cases.

---

## 🚀 Tomorrow's Workspace Context

Both the data dictionary parser and table data cleaner components are fully stabilized, isolated from hardcoded paths, and verified PASSED inside your test suite runner.

When you log back on tomorrow, we can immediately pick up our active project checklist by choosing one of these directions:

1. Build the Interactive User Interface Loop to manage low-confidence coordinate mappings inside the terminal using `rich`.
2. Draft the Synthetic Payload Generation Script to verify performance optimization thresholds over thousands of production column matrices.

Let me know what you would like to proceed with first!
