```
# Dataset Type Bootstrapping Specification

## Purpose
Introduce a **bootstrapping phase**in `dd-parser-cleaner`to establish dataset type metadata before cleaning. This ensures the parser and cleaner apply the correct integrity rules and generate accurate manifests.

---

## Bootstrapping Flow

### Step 1: Top-Level Branch
-Ask: *Graph or Tabular analysis?*
-If **Graph**→ return: "Graph datasets are not supported in this version." (future scope)
-If **Tabular**→ proceed.

### Step 2: Tabular Branch
-Ask: *Is the dataset cross-sectional or panel?*
-If user knows → set `dataset_type`accordingly.
-If user is unsure → proceed with guided questions.

### Step 3: Guided Questions
1.**Subject identification**  
   -"What is the subject of the dataset? (e.g., customer, device, employee)"  
   -Store in `manifest.notes.subject`.

2.**Time dimension check**  
   -"Does each row represent the subject at a single point in time?"  
   -If **No**→ dataset is **event log**.  
   -If **Yes**→ continue.

3.**Synchronization check**  
   -"Are all subjects evaluated at the same point in time?"  
   -If **Yes**→ dataset is **cross-sectional**.  
   -If **No**→ dataset is **panel (long form)**.

---

## Manifest Integration
-Add `dataset_type`field to dataset manifest based on bootstrapping answers.
-Add `notes.subject`and `notes.use_case_answers`for transparency.
-Cleaner uses `dataset_type`to select appropriate validators:
  -**Cross-sectional**→ static consistency checks.
  -**Event log**→ monotonicity, lag consistency, gap detection.
  -**Panel**→ static vs dynamic attribute validation.

---

## Example Bootstrapping Dialogue
```

**System: Do you want to analyze a Graph or Tabular dataset?
User: Tabular
System: Is the dataset cross-sectional or panel?
User: Not sure
System: What is the subject of the dataset?
User: Customer
System: Does each row represent the subject at a single point in time?
User: No
System: → Dataset type set to event_log**

**Code**

```

---

## Acceptance Criteria
- Bootstrapping phase runs before any cleaning.
- Dataset manifest includes `dataset_type` and `notes.subject`.
- Handshake file reflects readiness only if bootstrapping metadata is complete.
- Cleaner applies validators based on dataset type.

---

## Value Added
- Provides **self-documenting metadata** for every dataset.
- Reduces ambiguity for agents and humans.
- Ensures cleaning rules are contextually correct.
- Significantly increases the trust and usability of KMDS across multiple dataset types.
```

**This Markdown version is clean, structured, and ready to replace fragmented notes. Would you like me to also add a ****table of contents** at the top for easier navigation, like we did for the consolidated featurization design doc?
