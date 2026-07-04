# USER GUIDE — dd-parser-cleaner

## Overview

**dd-parser-cleaner** is a discovery and validation library for enterprise datasets. It inspects incoming data, emits machine‑readable manifests describing structure and modalities, runs deterministic integrity checks, and writes a handshake file that downstream featurizers must read before transforming data. The package recognizes  **cross‑sectional** **, ** **event‑log** **, ** **panel** **, and ****graph** datasets (homogeneous, bipartite, heterogeneous) and supports modality tags for non‑tabular fields.

**This guide explains how to use the package, the canonical artifacts it produces, the programmatic discovery API (**`get_package_info()`), configuration flags, testing and rollout guidance, and developer implementation hints for refactors.

## Quick start

### 1. Initialize the workspace

```bash
init-workspace .
```

This creates the required KMDS directory layout and provisions `documents/config/dataset_questions.json`.

### 2. Validate file placement

```bash
location-helper .
```

This confirms where raw data, the data dictionary, and narrative documents should live.

### 3. Bootstrap dataset metadata

```bash
dataset-bootstrap .
```

This writes `bootstrap_metadata.yaml` and captures dataset metadata such as `dataset_type`, `subject`, `subject_id_attribute`, and optional use-case answers.

### 4. Generate runtime config

```bash
bootstrap-config --output config.yaml .
```

This consumes `bootstrap_metadata.yaml`, discovers the data and dictionary files, and writes `config.yaml` for parser and cleaner execution.

### 5. Run the parser

```bash
classify-entities --config config.yaml
```

This produces parser artifacts including:

* `documents/dd_analysis_results/<dataset_id>_analysis_results.csv`
* `documents/dd_analysis_results/<dataset_id>_dataset_manifest.json`
* `documents/dd_analysis_results/<dataset_id>_attribute_manifest.json`
* `documents/dd_cleaner/<dataset_id>_parser_cleaner_handshake.md`

### 6. Run the cleaner

```bash
clean-dataset --config config.yaml --action full
```

This validates the manifests, produces diagnostics, and exports the synchronized clean dataset.

### 7. Featurizer contract

Featurizer **must** read the generated handshake file and proceed only if `status == "ready"`.

* If `status == "blocked"`, the featurizer must refuse to proceed.
* If `status == "warnings"`, the featurizer may proceed only after acknowledging and recording the warnings.

### 8. SBA regression coverage

The consolidated SBA workflow is validated by `tests/test_sba_end_to_end.py`, which exercises the full interface from workspace initialization through metadata bootstrapping, config generation, parsing, and cleaning.

## Canonical artifacts

### Dataset manifest (`manifests/<dataset_id>.json`)

**A single JSON object describing dataset-level metadata. ** **Minimum fields** **:**

* **dataset_id** (string)
* **dataset_type** (enum): `cross_sectional` | `event_log` | `panel` | `graph_homogeneous` | `graph_bipartite` | `graph_heterogeneous`
* **primary_key_spec** (array of attribute names or generated key flag)
* **time_key_spec** (attribute name or `null`)
* **entity_files** (array; for graphs)
* **relation_files** (array; for graphs)
* **panel_variable_map** (object mapping `static` and `dynamic` attributes; for panel)
* **notes** (optional free text)
* **validation_errors** (array populated by cleaner)
* **use_case_answers** (optional object with minimal questionnaire answers)

**Example**

**json**

```
{
  "dataset_id":"orders_2026",
  "dataset_type":"event_log",
  "primary_key_spec":["order_id"],
  "time_key_spec":"event_time",
  "entity_files":[],
  "relation_files":[],
  "panel_variable_map":null,
  "notes":"Order events from e-commerce pipeline",
  "validation_errors":[]
}
```

### Attribute manifest (`attributes/<dataset_id>_attributes.json`)

**An array of attribute descriptors. Each entry includes:**

* **attribute_name** (string)
* **role** **: **`subject_key` | `time_key` | `feature` | `relation_key` | `node_id` | `edge_attr`
* **time_dependency** **: **`static` | `dynamic` | `none`
* **granularity** **: **`daily` | `monthly` | `irregular` | `event-level` | `null`
* **modality** **: **`numeric` | `categorical` | `text_url` | `image_url` | `audio_url` | `geo_address` | `date` | `currency` | `other`
* **suggested_checks** (array of strings)
* **generated_key_flag** (boolean)

**Example**

**json**

```
{
  "attribute_name":"order_id",
  "role":"subject_key",
  "time_dependency":"none",
  "granularity":null,
  "modality":"categorical",
  "suggested_checks":["null_profile"],
  "generated_key_flag":false
}
```

### Handshake (`manifests/handshake.json`)

**A small JSON file indicating readiness for featurization. Fields:**

* **status** **: **`ready` | `blocked` | `warnings`
* **manifest_path** **: path to dataset manifest**
* **blocking_reasons** **: array of strings**

**Example**

**json**

```
{
  "status":"ready",
  "manifest_path":"manifests/orders_2026.json",
  "blocking_reasons":[]
}
```

## KMDS taxonomy primer (for users and agents)

### Dataset types and characteristic features


| **Dataset Type**         | **Primary Structure**                    | **Time Role**                             | **Relational Shape**                                 | **Typical Modalities**                           |
| -------------------------- | ------------------------------------------ | ------------------------------------------- | ------------------------------------------------------ | -------------------------------------------------- |
| **Cross sectional**      | One row per subject                      | No time dimension                         | Flat table                                           | Numeric; categorical; text; URLs                 |
| **Event log**            | One row per event; subject repeated      | All attributes indexed by timestamp       | Flat with subject key + time key                     | Transactional fields; timestamps; event metadata |
| **Panel**                | One row per subject per time period      | Mix of static and time-varying attributes | Flat with subject key + time key                     | Static demographics; dynamic metrics             |
| **Graph homogeneous**    | Node attributes + edge tuples            | Time optional                             | Single entity type; edges between same type          | Node features; edge attributes                   |
| **Graph bipartite**      | Two node types + relation tuples         | Time optional                             | Two distinct entity types; relations across types    | Separate attribute sets per entity               |
| **Graph heterogeneous**  | Multiple entity types with tree topology | Time optional                             | Multi-entity tree; n entities and n-1 relation files | Entity-specific attributes; relation attributes  |
| **Modality rich fields** | Fields pointing to external content      | Time orthogonal                           | Can appear in any dataset type                       | `image_url`;`text_url`;`audio_url`;`geo_address` |

### Characteristic features dd-parser-cleaner must detect

* **Identity and keys** **: primary subject key or generated surrogate key; time key for longitudinal data; node id specs and join keys for graphs.**
* **Time semantics** **: per-attribute **`time_dependency` (`dynamic`/`static`/`none`), `granularity`, and time semantics (event vs ingestion vs aggregated).
* **Relational topology** **: graph type, input form (explicit vs inferred), constraints (max entity types, acyclic requirement for heterogeneous).**
* **Modality tags** **: **`numeric`, `categorical`, `text_url`, `image_url`, `audio_url`, `geo_address`, `date`, `currency`.
* **Quality hints** **: suggested checks like **`monotonicity`, `lag_consistency`, `irregular_gaps`, `relation_consistency`, `no_cycles`, `null_profile`, `url_validity`.

## Minimal use-case questionnaire

**The parser-cleaner can optionally prompt the user (or accept answers via API) to capture up to five short use-case questions. Answers are stored in **`manifest.notes.use_case_answers` and improve cleaning suggestions and documentation.

1. **Primary objective** **: prediction, cohort analysis, anomaly detection, or graph analytics**
2. **Subject of analysis** **: customer, device, employee, transaction, etc.**
3. **Time semantics** **: event time, ingestion time, or aggregated period**
4. **Key relationships** **: known relationships between files/entities that must be preserved**
5. **Privacy constraints** **: PII or restricted attributes requiring special handling**

**These answers are optional but recommended.**

## Configuration

**Add or review these flags in **`config.yaml` under a `manifest` section.

**yaml**

```
manifest:
  require_manifest_before_featurize:true
  use_case_questions_enabled:false
  graph_entity_limit:5
  generate_surrogate_keys:true
  url_sample_size:10
```

**Other parser/cleaner flags:**

* `parser.generate_surrogate_keys` (boolean)
* `cleaner.monotonicity_tolerance` (numeric)
* `cleaner.url_sample_size` (integer)

**Centralize LLM prompts in **`dd_common/llm_prompts.py` and enforce JSON-only responses when using LLMs for manifest generation.

## Implementation hints (developer-facing)

**Paste this section into **`docs/implementation_hints.md` or include in the repo for Copilot to use when refactoring.

### Parser priorities

* **Emit canonical manifests (dataset manifest and attribute manifest) for every run.**
* **Detect dataset type and set **`dataset_type` accordingly.
* **Tag attributes with **`role`, `time_dependency`, `granularity`, `modality`, `suggested_checks`, `generated_key_flag`.
* **Detect graph intent and emit **`graph_type`, `entity_file_map`, `entity_key_spec`, `relationship_map`, `inferred_relationships`.
* **Generate deterministic surrogate keys when keys are missing; use naming convention **`__gen_key_<dataset_id>_<seq>` and set `generated_key_flag`.
* **Capture minimal questionnaire answers in **`manifest.notes.use_case_answers` when enabled.
* **Maintain backward compatibility by adding new fields as optional keys.**

### Cleaner priorities

* **Implement a manifest validation engine that populates **`manifest.validation_errors` and writes `handshake.json` with `status`.
* **Time checks: monotonicity, lag consistency, irregular gaps, missingness by time slice.**
* **Panel checks: static consistency and drift detection.**
* **Graph checks: relation consistency, cycle detection for heterogeneous graphs, connectivity summary.**
* **Modality checks: URL format validation, optional sampled reachability, geo parse sanity checks.**
* **Provide actionable diagnostics with **`severity`, `remediation`, and `sample_rows`.
* **Do not modify source files; record generated keys in manifests.**

### Handshake and schema

* **Handshake file example:**

**json**

```
{
  "status":"ready",
  "manifest_path":"manifests/<dataset_id>.json",
  "blocking_reasons":[]
}
```

* **Provide JSON Schema files in **`schemas/` for `dataset_manifest.json`, `attribute_manifest.json`, and `handshake.json`.
* **The user questionnaire schema is now located at** `documents/config/dataset_questions.json`.
* **Featurizer must read handshake and refuse to proceed if **`status == blocked`.

### Testing and CI

* **Unit tests for manifest emission across dataset types.**
* **Integration tests: parser → cleaner → handshake; featurizer stub refuses on **`blocked`.
* **Property tests for deterministic surrogate key generation.**
* **Include fixtures under **`tests/fixtures/` for each dataset type.
* **CI should fail if any sample run produces **`handshake.status == blocked`.

### Rollout plan

1. **Emit manifests and handshake while preserving legacy outputs.**
2. **Enable cleaner validators and handshake enforcement behind config flags.**
3. **Deprecate legacy outputs after one release cycle.**

### Observability and ergonomics

* **Structured logs for manifest generation and validation errors.**
* **Metrics: manifests emitted, blocked featurizations, common validation failures.**
* **Extension hooks for custom validators and modality handlers.**

## Examples and recipes

### Parser → Cleaner → Featurizer flow (conceptual)

**py**

```
fromdd_parser_cleaner importget_package_info
# 1. Discover
info = get_package_info()
# 2. Run parser (conceptual API)
# parser.run(input_path='data/orders.csv', output_manifest='manifests/orders.json')
# 3. Run cleaner (conceptual API)
# cleaner.run(manifest_path='manifests/orders.json', output_handshake='manifests/handshake.json')
# 4. Featurizer reads handshake
# with open('manifests/handshake.json') as f:
#     handshake = json.load(f)
# if handshake['status'] != 'ready':
#     raise RuntimeError('Featurization blocked: ' + str(handshake['blocking_reasons']))
```

**Place sample manifests in **`tests/fixtures/manifests/` for developer reference.

## Troubleshooting

**Each cleaner validation error includes **`severity`, `remediation`, and `sample_rows`.

**Common issues and fixes:**

* **Missing primary key** **: provide explicit key or allow parser to generate surrogate key; prefer explicit keys.**
* **Time key absent for longitudinal data** **: set **`time_key_spec` or mark dataset as `cross_sectional`.
* **Relation file join mismatch** **: ensure **`entity_key_spec` matches keys referenced in relation files.
* **Heterogeneous graph cycle detected** **: correct relationship files to form a tree or remove cycles.**
* **Invalid URLs or geo addresses** **: inspect sample rows flagged by cleaner and correct modality fields.**

## Programmatic discovery: `get_package_info()`

`get_package_info()` returns a dictionary with both legacy and new discovery fields. Use it to find CLI commands, schema paths, handshake spec, supported dataset types, and config flags.

**Important keys returned**

* `package_name`, `version`, `entry_points`, `cli_commands`, `provided_packages`, `documentation_note`
* `manifest_schema_paths` (paths to JSON Schema files)
* `handshake_spec` (handshake file path and allowed status values)
* `supported_dataset_types`
* `config_flags` (important flags and defaults)
* `sample_manifests_location`, `cli_help_map`, `compatibility_notes`, `support_contact`

**Agent guidance**

* **Validate manifests against the schemas referenced in **`manifest_schema_paths` before proceeding.
* **Use **`handshake_spec` to enforce featurizer contract.

## Contribution and support

* **Add issues to the repository issue tracker (see **`get_package_info()` for link).
* **Follow **`CONTRIBUTING.md` for tests, fixtures, and schema updates.
* **Keep new manifest fields additive and optional to preserve backward compatibility.**

## Appendix: acceptance criteria for refactor

* **Parser emits dataset manifest and attribute manifest matching JSON Schema for all fixtures.**
* **Cleaner writes **`handshake.json` with correct `status`.
* **Featurizer stub refuses to proceed when **`handshake.status == blocked`.
* **Unit and integration tests pass in CI.**
* **Backward compatibility preserved during phased rollout.**

## Where to find files and examples

* **JSON Schema files** **: **`schemas/dataset_manifest.json`, `schemas/attribute_manifest.json`, `schemas/handshake.json`
* **Sample manifests and fixtures** **: **`tests/fixtures/manifests/` and `tests/fixtures/csvs/`
* **Docs and design** **: **`USER_GUIDE.md`, `documents/`, `docs/manifest.md`, `docs/implementation_hints.md`

**End of user guide.**
