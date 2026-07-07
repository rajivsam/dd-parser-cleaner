### KMDS Primer Dataset Taxonomy

# KMDS Primer Dataset Taxonomy

## Purpose

This primer defines the **KMDS dataset taxonomy**and the characteristic features the **dd-parser-cleaner**must detect and emit. It is written for both human users and autonomous agents so parser outputs are consistent and the featurizer can consume them deterministically.

## Taxonomy Overview


| **DatasetType**        | **PrimaryStructure**                | **TimeRole**                        | **RelationalShape**                           | **TypicalModalities**                        |
| ------------------------ | ------------------------------------- | ------------------------------------- | ----------------------------------------------- | ---------------------------------------------- |
| **Crosssectional**     | Onerowpersubject                    | Notimedimension                     | Flattable                                     | Numeric;categorical;text;URLs                |
| **Eventlog**           | Onerowperevent;subjectrepeated      | Allattributesindexedbytimestamp     | Flatwithsubjectkeyandtimekey                  | Transactionalfields;timestamps;eventmetadata |
| **Panel**              | Onerowpersubjectpertimeperiod       | Mixofstaticandtimevaryingattributes | Flatwithsubjectkeyandtimekey                  | Staticdemographics;dynamicmetrics            |
| **Wide_short_homogeneous** | Onerowpermanycolumns               | Notimedimension or timeoptional    | Wide matrix with many repeated measures       | Sensor readings;survey items;embeddings       |
| **Graphhomogeneous**   | Nodeattributesplusedgetuples        | Timeoptional                        | Singleentitytype;edgesbetweensametype         | Nodefeatures;edgeattributes                  |
| **Graphbipartite**     | Twonodetypesplusrelationtuples      | Timeoptional                        | Twodistinctentitytypes;relationsacrosstypes   | Separateattributesetsperentity               |
| **Graphheterogeneous** | Multipleentitytypeswithtreetopology | Timeoptional                        | Multi-entitytree;nentitiesandn-1relationfiles | Entity-specificattributes;relationattributes |
| **Modalityrichfields** | Fieldspointingtoexternalcontent     | Timeorthogonal                      | Canappearinanydatasettype                     | image_url;text_url;audio_url;geo_address     |

## Characteristic Features dd-parser-cleaner Must Detect

### Identity and Keys

* **Primary subject key**or generated surrogate key.
* **Time key**when dataset is event log or panel.
* **Node id specs**for graph nodes and join keys for relation files.

### Time Semantics

* **Time dependency**per attribute: `<span>dynamic</span>`, `<span>static</span>`, or `<span>none</span>`.
* **Granularity** : `<span>daily</span>`, `<span>monthly</span>`, `<span>irregular</span>`, `<span>event-level</span>`.
* **Time semantics** : event time vs ingestion time vs aggregated period.

### Relational Topology

* **Graph type** : `<span>homogeneous</span>`, `<span>bipartite</span>`, `<span>heterogeneous</span>`.
* **Input form** : explicit tuples vs inferred relationships.
* **Constraints** : max entity types for heterogeneous; acyclic requirement for heterogeneous.

### Wide-Short Homogeneous Datasets

* **Structure** : one subject row with many homogeneous repeated-measure columns.
* **Processing strategy** : capture the dataset as wide-short at bootstrap time, ask for a `representative_column`, and infer validation intelligence once for the representative group.
* **Config coupling** : `dataset-bootstrap` writes `wide_short_homogeneous` and `wide_short_representative_column` into `bootstrap_metadata.yaml`; `bootstrap-config` copies those values into `parser` config and picks wide-short-specific prompts.
* **Parser fast path** : `classify-entities` uses only the first dictionary attribute and the representative column for LLM classification, then treats remaining columns as repeated members of the same homogeneous group.
* **Manifest signals** : `manifest.notes.structure = "wide_short_homogeneous"`, `manifest.flags.skip_columnwise_intelligence = true`, and a `representative_column` marker for the homogeneous group.
* **Use cases** : sensor arrays, survey matrices, embedding blocks, feature bundles where per-column semantic inference is redundant.
* **Validation focus** : bulk rules on grouped columns, consistent schema across repeated measures, and efficient summary diagnostics rather than individual column-level reports.

### Modality Tags

* **Input type** : `<span>numeric</span>`, `<span>categorical</span>`, `<span>text_url</span>`, `<span>image_url</span>`, `<span>audio_url</span>`, `<span>geo_address</span>`, `<span>date</span>`, `<span>currency</span>`.
* **Validation hints** : URL reachability, file extension checks, geo parsing.

### Quality and Integrity Hints

* **Suggested checks** : `<span>monotonicity</span>`, `<span>lag_consistency</span>`, `<span>irregular_gaps</span>`, `<span>relation_consistency</span>`, `<span>no_cycles</span>`, `<span>null_profile</span>`, `<span>url_validity</span>`.
* **Profiling metrics** : null rates by time slice, edge degree distribution, entity counts.

## Required Parser Outputs Before Featurization

### Dataset Manifest

A single JSON object containing at minimum:

* **dataset_id**
* **dataset_type**(one of the taxonomy)
* **primary_key_spec**list of attributes forming the subject key or generated key
* **time_key_spec**attribute name for timestamp or `<span>null</span>`
* **entity_files**and **relation_files**for graphs
* **notes**and **use_case_answers**optional

### Attribute Manifest

An array of JSON objects where each attribute entry includes:

* **attribute_name**
* **role**`<span>subject_key</span>`| `<span>time_key</span>`| `<span>feature</span>`| `<span>relation_key</span>`| `<span>node_id</span>`| `<span>edge_attr</span>`
* **time_dependency**`<span>static</span>`| `<span>dynamic</span>`| `<span>none</span>`
* **granularity**
* **modality**
* **suggested_checks**
* **generated_key_flag**boolean

### Graph Manifest Additions

* **graph_type**
* **node_attribute_schema**
* **edge_attribute_schema**
* **node_id_spec**or `<span>generated_node_id_flag</span>`
* **entity_file_map** ,  **entity_key_spec** , **relationship_map**
* **cycle_check_result** , **connectivity_check_result**

### Handshake Requirement

Parser must produce a validated manifest and a **handshake**file that the featurizer reads before any transformation.

## Minimal Use Case Questionnaire

Optional short prompts to improve dataset context and cleaning guidance. Record answers in `<span>manifest.notes.use_case_answers</span>`.

1. **Primary objective**prediction, cohort analysis, anomaly detection, or graph analytics
2. **Subject of analysis**customer, device, employee, transaction, etc.
3. **Time semantics**event time, ingestion time, or aggregated period
4. **Known relationships**files/entities that must be joined or preserved
5. **Privacy constraints**PII or restricted attributes requiring special handling

## Quick Checklist for Agents and Users

* Confirm parser produced dataset manifest and attribute manifest.
* Confirm keys and time specs are present and consistent.
* Confirm graph manifests include entity files and join keys.
* Confirm modality tags exist for non-tabular fields.
* Confirm suggested checks are present for time and graph integrity.
* Confirm handshake file exists and `<span>manifest.validation_errors</span>`is empty.

If manifest is incomplete, the cleaner should emit actionable diagnostics and a prioritized list of missing items. The featurizer must refuse to proceed until required manifest fields are present or surrogate keys are generated and recorded.

## Rationale

This taxonomy is exhaustive for tabular and relational enterprise data because every dataset either lacks time, is fully time indexed, mixes static and dynamic attributes, or represents relationships better expressed as graphs. Responsibilities remain separated and deterministic: dd-parser-cleaner declares structure and checks; featurizer performs transformations. Modality rich fields are tagged rather than converted early, enabling specialized downstream featurization.

## Next Steps

Provide this primer to users and agents as a quick reference. Optionally convert the manifests and checklist into a JSON Schema and a one-page capability map for documentation and automated validation.

### Comprehensive Design Document dd-parser-cleaner

# Comprehensive Design Document dd-parser-cleaner

## Objective

Define a unified, actionable design for **dd-parser-cleaner**that supports cross-sectional, longitudinal (event-log and panel), graph-based (homogeneous, bipartite, heterogeneous), and modality-aware datasets. Scope is strictly the parser-cleaner: tagging, diagnostics, validation, and emitting deterministic manifests and hints for downstream featurization.

## High-Level Architecture

### Responsibilities

* **Parser** : Analyze raw inputs, classify dataset type, produce dataset manifest and attribute manifest, tag modalities, detect graph intent, and generate keys when necessary.
* **Cleaner** : Run deterministic integrity checks, profile quality, validate manifest consistency, produce diagnostics and a handshake file.
* **Common** : Provide shared utilities (PathCoordinator, prompt templates, config schema) and enforce config-driven behavior.

### CLI Workflow and Metadata Bootstrapping

The canonical user interface now follows a deterministic bootstrapping flow:

1. `init-workspace .`
   - Create workspace directories and provision `documents/config/dataset_questions.json`.
2. `location-helper .`
   - Validate file placement guidance for `data/`, `data_dictionary/`, and `documents/`.
3. `dataset-bootstrap .`
   - Discover raw dataset and dictionary files and write `bootstrap_metadata.yaml`.
   - Capture `dataset_type`, `subject`, `subject_id_attribute`, and optional use-case answers.
4. `bootstrap-config --output config.yaml .`
   - Read `bootstrap_metadata.yaml` and generate a fully wired `config.yaml`.
   - Preserve `dataset_type`, `subject_id_attribute`, and wide-short metadata from bootstrapped metadata before prompting the user.
   - If the dataset is wide-short homogeneous, configure parser prompt templates for that structure.
5. `classify-entities --config config.yaml`
   - Produce parser artifacts, manifests, and the parser-cleaner handshake.
6. `clean-dataset --config config.yaml --action full`
   - Validate manifests, generate diagnostics, and export the synchronized clean dataset.

This workflow replaces earlier manual config generation with an explicit metadata bootstrapping phase.

#### Wide-Short Homogeneous Dataset Bootstrapping

* Detect whether the dataset is wide-and-short with many homogeneous columns during bootstrap or config generation.
* If yes, prompt for a `representative_column` and record `manifest.notes.structure = "wide_short_homogeneous"`.
* `bootstrap-config` now copies wide-short metadata into `config.yaml` and selects wide-short-specific LLM prompt templates for the parser.
* Use the representative column metadata to infer data type, modality, and validation rules once, then apply them across the repeated column group.
* `classify-entities` runs LLM classification only on the first schema field plus the representative column for wide-short datasets, keeping the rest of the group implied.
* Preserve a compact manifest representation rather than expanding every repeated column into a separate intelligence item unless downstream tooling requires it.

### SBA End-to-End Regression Coverage

A single consolidated regression test, `tests/test_sba_end_to_end.py`, now validates the full interface from workspace initialization through dataset bootstrap, config generation, parser execution, and cleaner execution. This test is the authoritative signal that the new interface is supported end to end.

### Design Principles

* **Declarative outputs** : Parser-cleaner emits structured manifests and hints; it does not perform heavy transformations.
* **Procedural featurizer** : Downstream featurizer consumes manifests to build transformation pipelines.
* **Config-driven** : All rules and thresholds live in `<span>config.yaml</span>`.
* **Non-destructive** : Raw data is never modified in place.
* **Deterministic LLM usage** : JSON-only responses, temperature locked at 0.0, prompts centralized.

## Required Manifests and Schemas

### Dataset Manifest Schema

* **dataset_id**string
* **dataset_type**enum: `<span>cross_sectional</span>`| `<span>event_log</span>`| `<span>panel</span>`| `<span>graph_homogeneous</span>`| `<span>graph_bipartite</span>`| `<span>graph_heterogeneous</span>`
* **primary_key_spec**array of attribute names or generated key flag
* **time_key_spec**attribute name or `<span>null</span>`
* **entity_files**array (for graphs)
* **relation_files**array (for graphs)
* **panel_variable_map**object mapping `<span>static</span>`and `<span>dynamic</span>`attributes (for panel)
* **graph_metadata**object (graph-specific details)
* **notes**free text
* **notes.structure**string (`wide_short_homogeneous` or other structure hints)
* **flags**object (e.g. `skip_columnwise_intelligence`)
* **use_case_answers**object (optional questionnaire responses)
* **validation_errors**array of strings (populated by cleaner)

### Attribute Manifest Schema (per attribute)

* **attribute_name**string
* **role**enum: `<span>subject_key</span>`| `<span>time_key</span>`| `<span>feature</span>`| `<span>relation_key</span>`| `<span>node_id</span>`| `<span>edge_attr</span>`
* **time_dependency**enum: `<span>static</span>`| `<span>dynamic</span>`| `<span>none</span>`
* **granularity**enum or `<span>null</span>`
* **modality**enum: `<span>numeric</span>`| `<span>categorical</span>`| `<span>text_url</span>`| `<span>image_url</span>`| `<span>audio_url</span>`| `<span>geo_address</span>`| `<span>date</span>`| `<span>currency</span>`| `<span>other</span>`
* **suggested_checks**array of strings
* **generated_key_flag**boolean

## Parser Enhancements

### Time-aware Detection

* Detect presence of timestamp fields and infer **dataset_type**as `<span>event_log</span>`or `<span>panel</span>`when appropriate.
* For `<span>event_log</span>`: mark all non-key attributes as `<span>time_dependency: </span><span>dynamic</span>`.
* For `<span>panel</span>`: classify each attribute as `<span>static</span>`or `<span>dynamic</span>`and populate `<span>panel_variable_map</span>`.

### Graph Recognition

* Detect graph intent via schema patterns or user hint.
* Classify graph type:
  * **Homogeneous** : single entity type; input may be explicit tuples or inferred.
  * **Bipartite** : two distinct entity types; tuples map attributes to each side.
  * **Heterogeneous** : up to 5 entity types; tree topology; requires n entity files and n-1 relation files.
* Emit graph metadata:
  * `<span>graph_type</span>`, `<span>entity_file_map</span>`, `<span>entity_key_spec</span>`, `<span>relationship_map</span>`, `<span>inferred_relationships</span>`flag.

### Modality Tagging

* Tag fields with `<span>modality</span>`(e.g., `<span>image_url</span>`, `<span>text_url</span>`, `<span>geo_address</span>`).
* Validate basic format and emit `<span>suggested_checks</span>`such as `<span>url_validity</span>`or `<span>geo_parse</span>`.

### Key Generation and Validation

* If primary keys or node ids are missing, generate surrogate keys and set `<span>generated_key_flag</span>`.
* Ensure join keys referenced in relation files match entity key specs.

### Manifest Emission

* Produce dataset manifest and attribute manifest as canonical handoff artifacts.
* Write a `<span>handshake</span>`file indicating manifest validity and readiness for featurization.

## Cleaner Enhancements

### Time-aware Integrity Checks

* **Monotonicity** : verify timestamps are monotonic per subject when required.
* **Lag consistency** : detect inconsistent lag patterns for dynamic attributes.
* **Irregular gaps** : profile gaps and suggest interpolation or aggregation strategies.

### Panel-specific Checks

* **Static consistency** : ensure static attributes do not change unexpectedly across time for the same subject.
* **Missingness by time** : compute missing rates per time slice and per subject.

### Graph-specific Checks

* **Relation consistency** : ensure relation files reference valid entity keys.
* **Cycle detection** : for heterogeneous graphs, assert acyclic topology and report `<span>cycle_check_result</span>`.
* **Connectivity** : report connected components and isolated nodes.

### Modality Checks

* **URL reachability** : optionally test a sample of URLs for reachability.
* **Geo parsing** : validate address parsing to lat-long for sample rows.
* **File type validation** : check extensions and basic MIME hints.

### Reporting

* Produce JSON and Markdown reports with:
  * Profiling metrics
  * Suggested cleaning actions
  * Manifest validation errors
  * Prioritized remediation list

## Config and Prompt Changes

### config.yaml Additions

* `<span>manifest</span>`section:
  * `<span>require_manifest_before_featurize</span>`boolean
  * `<span>use_case_questions_enabled</span>`boolean
  * `<span>graph_entity_limit</span>`integer (default 5)
  * `<span>time_granularity_rules</span>`mapping
  * `<span>modality_map</span>`definitions
* `<span>parser</span>`section:
  * `<span>generate_surrogate_keys</span>`boolean
  * `<span>graph_detection_thresholds</span>`
* `<span>cleaner</span>`section:
  * `<span>monotonicity_tolerance</span>`
  * `<span>url_sample_size</span>`
  * `<span>max_missing_rate_for_static</span>`

### Prompt Templates

* Extend LLM prompts to request structured JSON manifests and to ask the minimal questionnaire when enabled.
* Centralize prompts in `<span>dd_common/llm_prompts.py</span>` and enforce JSON-only responses.
* When `parser.wide_short_homogeneous` is true, select dedicated wide-short prompt templates from config and pass `wide_short_representative_column` into LLM prompt formatting.

## Featurizer Handshake Contract

Before featurization begins the parser-cleaner must provide:

* Validated **dataset manifest**and  **attribute manifest** .
* **Handshake file**indicating `<span>manifest.validation_errors</span>`is empty or contains only non-blocking warnings.
* For graphs: entity files, relation files, and consistent join keys.
* For longitudinal data: explicit `<span>time_key_spec</span>`and `<span>panel_variable_map</span>`for panel datasets.

Featurizer must refuse to proceed if required manifest fields are missing unless the cleaner has generated surrogate keys and recorded them in the manifest.

## Minimal Use Case Questionnaire

Include up to five short questions to improve dataset context and cleaning guidance. Store answers in `<span>manifest.notes.use_case_answers</span>`.

1. **Primary objective** : prediction, cohort analysis, anomaly detection, or graph analytics
2. **Subject of analysis** : customer, device, employee, transaction, etc.
3. **Time semantics** : event time, ingestion time, or aggregated period
4. **Known relationships** : files/entities that must be joined or preserved
5. **Privacy constraints** : PII or restricted attributes requiring special handling

## Testing Strategy

### Unit and Integration Tests

* Parser unit tests for manifest completeness across dataset types.
* Cleaner unit tests for each integrity check (time, panel, graph, modality).
* Integration tests that simulate KMDS workspace layouts and real CSVs.

### Datasets for Tests

* Cross-sectional: customer profiles.
* Event-log: transaction logs with irregular timestamps.
* Panel: HR payroll with static demographics and monthly salary.
* Graphs: homogeneous social edges, bipartite user-product interactions, heterogeneous supply chain tree.
* Modality: sample rows with image URLs, text URLs, and addresses.

### Validation Criteria

* Parser emits manifests matching JSON schema.
* Cleaner validation errors are actionable and precise.
* Handshake file correctly reflects readiness.
* Featurizer can deterministically consume manifests to build pipelines.

## Error Handling and Diagnostics

* **manifest.validation_errors**must list missing or inconsistent items with severity levels.
* Cleaner produces a prioritized remediation list with suggested fixes and sample code snippets (non-executable guidance).
* Handshake file includes `<span>status</span>`(`<span>ready</span>`| `<span>blocked</span>`| `<span>warnings</span>`) and `<span>blocking_reasons</span>`.

## Example Manifest Snippets

### Panel dataset snippet

**json**

```
{
  "dataset_id":"hr_panel_2026",
  "dataset_type":"panel",
  "primary_key_spec":["employee_id"],
  "time_key_spec":"pay_period",
  "panel_variable_map":{"static":["hire_date","department"],"dynamic":["salary","bonus"]},
  "attribute_manifest":[
    {"attribute_name":"employee_id","role":"subject_key","time_dependency":"none"},
    {"attribute_name":"salary","role":"feature","time_dependency":"dynamic","granularity":"monthly","suggested_checks":["lag_consistency"]},
    {"attribute_name":"hire_date","role":"feature","time_dependency":"static","modality":"date"}
  ],
  "validation_errors":[]
}
```

### Heterogeneous graph snippet

**json**

```
{
  "dataset_id":"supply_chain_graph",
  "dataset_type":"graph_heterogeneous",
  "entity_file_map":{"supplier":"suppliers.csv","part":"parts.csv","warehouse":"warehouses.csv"},
  "entity_key_spec":{"supplier":["supplier_id"],"part":["part_id"],"warehouse":["warehouse_id"]},
  "relationship_map":[
    {"from_entity":"supplier","to_entity":"part","relation_file":"supplies.csv","join_keys":{"supplier":"supplier_id","part":"part_id"}},
    {"from_entity":"part","to_entity":"warehouse","relation_file":"stored_in.csv","join_keys":{"part":"part_id","warehouse":"warehouse_id"}}
  ],
  "cycle_check_result":"acyclic",
  "validation_errors":[]
}
```

## Implementation Roadmap (High Level)

1. **Schema and config** : finalize manifest JSON schema and extend `<span>config.yaml</span>`.
2. **Parser updates** : implement time-awareness, modality tagging, graph detection, and manifest emission.
3. **Cleaner updates** : implement time-aware and graph-aware validators and profiling.
4. **Prompts** : update LLM prompt templates to request structured manifests and optional questionnaire.
5. **Testing** : add unit and integration tests with representative datasets.
6. **Documentation** : publish primer and manifest JSON schema for featurizer integration.

## Wide-Short Homogeneous Dataset Support Plan

### Implementation tasks

* Extend the dataset taxonomy and bootstrap questionnaire to recognize `wide_short_homogeneous` datasets.
* Add config/schema support for `manifest.notes.structure` and `flags.skip_columnwise_intelligence`.
* Implement representative-column detection and grouping in the parser so intelligence is inferred once and propagated across repeated homogeneous columns.* Couple bootstrap metadata into `config.yaml` so `bootstrap-config` writes `parser.wide_short_homogeneous`, `parser.wide_short_representative_column`, and selects wide-short prompt templates.
* Implement the wide-short parser fast path: classify only the first dictionary field and the representative column, then treat remaining columns as repeated members of the same homogeneous group.* Support a compact attribute manifest representation for grouped homogeneous columns, including `group_name`, `representative_column`, `data_type`, `validation_rules`, and `count_columns`.
* Update the cleaner to validate grouped columns in bulk and report summary diagnostics for wide-short datasets instead of per-column verbosity.
* Keep existing tall-and-skinny heterogeneous processing unchanged by gating the new flow on the wide-short structure signal.

### Testing tasks

* Add unit tests for bootstrap/config recognition of wide-short datasets and metadata recording.
* Add parser tests verifying the representative-column inference and grouped manifest emission.
* Add parser tests verifying the wide-short fast path uses only the first and representative columns for LLM classification.
* Add cleaner tests validating bulk rule application and handshake status generation for wide-short inputs.
* Create a wide-short fixture dataset with homogeneous repeated columns and a schema that matches typical sensor/survey use cases.
* Add an end-to-end integration test that covers bootstrap -> config generation -> parser -> cleaner -> handshake for a wide-short dataset.
* Add regression asserts ensuring traditional tall-and-skinny datasets continue to emit standard `dataset_type` and non-wide-short manifests.

### Validation criteria

* `manifest.notes.structure` is populated only for wide-short homogeneous datasets.
* `flags.skip_columnwise_intelligence` is used to avoid redundant per-column inference.
* The parser emits a compact grouped manifest for the representative homogeneous column and still includes enough detail for downstream featurization.
* The cleaner produces `handshake.status == "ready"` for valid wide-short inputs and `blocked` for missing critical metadata.
* Existing dataset flows remain unchanged when `wide_short_homogeneous` is not detected.

## Summary

This comprehensive dd-parser-cleaner design makes the parser responsible for **complete, validated manifests** describing keys, time semantics, modality tags, and graph structure. The cleaner enforces integrity and produces actionable diagnostics. The featurizer becomes a deterministic consumer of these manifests. The design preserves modularity, is config-driven, and supports enterprise dataset types including cross-sectional, longitudinal, graph-based, and modality-rich inputs.

### Implementation Hints

A single, copy‑ready section for developers and Copilot in VS Code. Paste this into the repo under `docs/implementation_hints.md` or into the Implementation Hints section of the design doc. It assumes the parser‑cleaner will emit canonical manifests and a handshake file that the featurizer reads before any transformation.

---

### Parser Priorities
- **Emit canonical manifests**: produce a **dataset manifest** and an **attribute manifest** for every dataset run. These are the single source of truth for featurization.
- **Detect dataset type**: set `dataset_type` to one of `cross_sectional`, `event_log`, `panel`, `graph_homogeneous`, `graph_bipartite`, `graph_heterogeneous`.
- **Attribute tagging**: include `role`, `time_dependency`, `granularity`, `modality`, `suggested_checks`, `generated_key_flag` for each attribute.
- **Graph detection and metadata**:
  - Detect explicit tuples vs inferred relationships.
  - Emit `graph_type`, `entity_file_map`, `entity_key_spec`, `relationship_map`, `inferred_relationships`.
  - For heterogeneous graphs enforce `graph_entity_limit` (default 5) and tree topology constraints.
- **Key policy**:
  - If keys missing, generate deterministic surrogate keys and set `generated_key_flag`.
  - Use naming convention: **`__gen_key_<dataset_id>_<seq>`**.
- **Minimal questionnaire**: optionally capture up to five use‑case answers and store in `manifest.notes.use_case_answers`.
- **Backward compatibility**: add new manifest fields as non‑breaking optional keys; preserve existing cross‑sectional outputs.

---

### Cleaner Priorities
- **Manifest validation engine**: deterministic validators that populate `manifest.validation_errors` and set handshake `status`.
- **Time checks**: monotonicity, lag consistency, irregular gap detection, missingness by time slice.
- **Panel checks**: static consistency across time for static attributes; drift detection for dynamic attributes.
- **Graph checks**: relation consistency, cycle detection for heterogeneous graphs, connectivity summary, degree distribution.
- **Modality checks**: URL format validation, optional sampled reachability, geo parse sanity checks, file type hints.
- **Actionable diagnostics**: prioritized remediation list with severity, remediation steps, and sample rows for each issue.
- **Non‑destructive behavior**: do not modify source files; record any generated keys in manifests.

---

### Manifests Handshake and Schema
- **Handshake contract**: write `handshake.json` with:
  ```json
  {
    "status": "ready",
    "manifest_path": "manifests/<dataset_id>.json",
    "blocking_reasons": []
  }
  ```
  - `status` values: `ready` | `blocked` | `warnings`.
  - Featurizer must read handshake and refuse to proceed if `status == blocked`.
- **Dataset manifest required fields**: `dataset_id`, `dataset_type`, `primary_key_spec`, `time_key_spec`, `entity_files`, `relation_files`, `panel_variable_map`, `validation_errors`, `notes`.
- **Attribute manifest required fields**: `attribute_name`, `role`, `time_dependency`, `granularity`, `modality`, `suggested_checks`, `generated_key_flag`.
- **Graph additions**: `graph_type`, `entity_file_map`, `entity_key_spec`, `relationship_map`, `cycle_check_result`.
- **Provide JSON Schema**: add machine‑readable JSON Schema files for dataset manifest, attribute manifest, and handshake in `schemas/`.
- **Questionnaire schema location**: `init-workspace` should provision `documents/config/dataset_questions.json` and `bootstrap-config` should write `questionnaire_schema_path` to this workspace-local file.

---

### Config Flags and Defaults
Add these to `config.yaml` under a `manifest` section and parser/cleaner sections.

| **Flag** | **Purpose** | **Default** |
|---|---:|---:|
| `require_manifest_before_featurize` | Enforce handshake read by featurizer | `true` |
| `use_case_questions_enabled` | Prompt for minimal questionnaire | `false` |
| `graph_entity_limit` | Max entity types for heterogeneous graphs | `5` |
| `generate_surrogate_keys` | Allow parser to create keys when missing | `true` |
| `url_sample_size` | Sample size for optional URL checks | `10` |

- Centralize LLM prompts in `dd_common/llm_prompts.py` and enforce JSON‑only responses; validate LLM output against JSON Schema before accepting.

---

### Testing CI and Rollout
- **Unit tests**: parser emits full manifests for fixtures covering cross‑sectional, event‑log, panel, homogeneous, bipartite, heterogeneous, and modality‑rich datasets.
- **Integration tests**: run parser → cleaner → handshake writer; featurizer stub reads handshake and refuses on `blocked`.
- **Property tests**: deterministic surrogate key generation and idempotent manifest emission.
- **Fixtures**: include canonical CSVs under `tests/fixtures/` for each dataset type.
- **CI gating**: fail pipeline if any sample run produces `handshake.status == blocked`.
- **Phased rollout**:
  1. Emit manifests and handshake while preserving legacy outputs.
  2. Enable cleaner validators and handshake enforcement behind config flag.
  3. Deprecate legacy outputs after one release cycle.

---

### Observability Developer Ergonomics and Extension Points
- **Structured logs**: log manifest generation, validation errors, handshake events with structured fields for metrics.
- **Metrics**: track manifests emitted, blocked featurizations, common validation failures.
- **Validation error format**: include `severity`, `remediation`, and `sample_rows`.
- **Performance guardrails**: sample‑based expensive checks (URL reachability, full graph connectivity) with configurable sample sizes.
- **Extension hooks**: plugin points for custom validators and modality handlers.
- **Docs and examples**: add `docs/manifest.md`, `docs/graph-guidelines.md`, and example manifests for each dataset type.
- **Acceptance criteria**:
  - Parser emits manifests matching JSON Schema for all fixtures.
  - Cleaner writes handshake with correct `status`.
  - Featurizer stub refuses on `blocked`.
  - Unit and integration tests pass in CI.

---

Paste this consolidated section verbatim into your Implementation Hints. Include the JSON Schema files and sample manifests in the repo so Copilot can validate outputs against them.
