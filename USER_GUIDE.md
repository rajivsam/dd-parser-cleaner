# USER GUIDE — dd-parser-cleaner

## Overview

**dd-parser-cleaner** is a discovery and validation library for enterprise datasets. It inspects incoming data, emits machine-readable manifests describing structure and modalities, runs deterministic integrity checks, and writes a handshake file that downstream featurizers must read before transforming data.

The package recognizes:

* `cross_sectional`
* `event_log`
* `panel`
* `graph_homogeneous`, `graph_bipartite`, and `graph_heterogeneous`

It also supports modality tags for non-tabular fields and explicit wide-short homogeneous dataset support.

## Quick start

### 1. Initialize the workspace

```bash
init-workspace .
```

This creates the KMDS workspace layout and provisions `documents/config/dataset_questions.json`.

### 2. Validate file placement

```bash
location-helper .
```

This confirms where `data/`, `data_dictionary/`, and `documents/` should live.

### 3. Bootstrap dataset metadata

```bash
dataset-bootstrap .
```

This writes `bootstrap_metadata.yaml` and captures dataset metadata such as `dataset_type`, `subject`, `subject_id_attribute`, and optional use-case answers.

* The utility supports tabular datasets and homogeneous graphs learnable from tabular data.
* For wide-short homogeneous datasets, it asks whether the dataset is wide-short and prompts for the representative column.
* If a graph is detected and it is not homogeneous/tabular-learnable, the bootstrapping flow stops and reports that bipartite/heterogeneous graphs are out of scope.

### 4. Generate runtime config

```bash
bootstrap-config --output config.yaml .
```

This consumes `bootstrap_metadata.yaml`, discovers the data and dictionary files, and writes `config.yaml` for parser and cleaner execution.

* For wide-short homogeneous datasets, `bootstrap-config` copies wide-short metadata into `config.yaml` and selects wide-short-specific parser prompts.

### 5. Run the parser

```bash
classify-entities --config config.yaml
```

This produces parser artifacts including:

* `documents/dd_analysis_results/<dataset_id>_analysis_results.csv`
* `documents/dd_analysis_results/<dataset_id>_dataset_manifest.json`
* `documents/dd_analysis_results/<dataset_id>_attribute_manifest.json`
* `documents/dd_cleaner/<dataset_id>_parser_cleaner_handshake.md`

For wide-short homogeneous datasets, parser classification uses a fast path: only the first schema field and the representative column are classified by the LLM, and the remaining repeated columns are treated as implied members of the same homogeneous group.

### 6. Run the cleaner

```bash
clean-dataset --config config.yaml --action full
```

This validates the manifests, produces diagnostics, and exports the synchronized clean dataset.

### 7. Featurizer contract

Featurizer **must** read the generated handshake file and proceed only if `status == "ready"`.

* If `status == "blocked"`, the featurizer must refuse to proceed.
* If `status == "warnings"`, the featurizer may proceed only after acknowledging and recording the warnings.

### 8. Regression coverage

The workflow is validated by `tests/test_sba_end_to_end.py` and by wide-short regressions in `tests/test_wide_short_end_to_end.py`.

## Canonical artifacts

### Dataset manifest (`manifests/<dataset_id>.json`)

A single JSON object describing dataset-level metadata. Minimum fields include:

* `dataset_id`
* `dataset_type` (`cross_sectional`, `event_log`, `panel`, `graph_homogeneous`, `graph_bipartite`, `graph_heterogeneous`)
* `primary_key_spec` (array of attribute names or generated key flag)
* `time_key_spec` (attribute name or `null`)
* `entity_files` (array; for graphs)
* `relation_files` (array; for graphs)
* `panel_variable_map` (object mapping `static` and `dynamic` attributes; for panel)
* `notes` (optional free text)
* `validation_errors` (array populated by cleaner)
* `use_case_answers` (optional object)

Example:

```json
{
  "dataset_id": "orders_2026",
  "dataset_type": "event_log",
  "primary_key_spec": ["order_id"],
  "time_key_spec": "event_time",
  "entity_files": [],
  "relation_files": [],
  "panel_variable_map": null,
  "notes": "Order events from e-commerce pipeline",
  "validation_errors": []
}
```

### Attribute manifest (`attributes/<dataset_id>_attributes.json`)

An array of attribute descriptors. Each entry includes:

* `attribute_name`
* `role` (`subject_key`, `time_key`, `feature`, `relation_key`, `node_id`, `edge_attr`)
* `time_dependency` (`static`, `dynamic`, `none`)
* `granularity` (`daily`, `monthly`, `irregular`, `event-level`, `null`)
* `modality` (`numeric`, `categorical`, `text_url`, `image_url`, `audio_url`, `geo_address`, `date`, `currency`, `other`)
* `suggested_checks` (array)
* `generated_key_flag` (boolean)

Example:

```json
{
  "attribute_name": "order_id",
  "role": "subject_key",
  "time_dependency": "none",
  "granularity": null,
  "modality": "categorical",
  "suggested_checks": ["null_profile"],
  "generated_key_flag": false
}
```

### Handshake (`manifests/handshake.json`)

A small JSON file indicating readiness for featurization.

* `status`: `ready`, `blocked`, or `warnings`
* `dataset_type`: bootstrapped dataset taxonomy
* `subject`: dataset subject, or `Not applicable` if not captured
* `subject_id_attribute`: subject key name, or `Not applicable` for cross-sectional datasets
* `wide_short_homogeneous`: boolean signal for wide-short grouping
* `wide_short_representative_column`: representative column name, or `Not applicable` when not applicable
* `manifest_path`: path to the dataset manifest
* `blocking_reasons`: array of strings

Example:

```json
{
  "status": "ready",
  "dataset_type": "event_log",
  "subject": "customer",
  "subject_id_attribute": "customer_id",
  "wide_short_homogeneous": false,
  "wide_short_representative_column": "Not applicable",
  "manifest_path": "manifests/orders_2026.json",
  "blocking_reasons": []
}
```

## Wide-short homogeneous datasets

Wide-short homogeneous datasets have one primary axis and many repeated homogeneous columns.

* `dataset-bootstrap` captures the wide-short signal and prompts for `wide_short_representative_column`.
* `bootstrap-config` preserves that metadata in `config.yaml`.
* `classify-entities` uses wide-short-specific prompts and a fast path that queries only the first schema field and the representative column.
* `manifest.notes.structure` is set to `wide_short_homogeneous` and `manifest.flags.skip_columnwise_intelligence` is enabled.

## Runtime workflow

1. `init-workspace .`
2. `location-helper .`
3. `dataset-bootstrap .`
4. `bootstrap-config --output config.yaml .`
5. `classify-entities --config config.yaml`
6. `clean-dataset --config config.yaml --action full`

## Configuration

`config.yaml` is the authoritative runtime configuration.

Example manifest flags:

```yaml
manifest:
  require_manifest_before_featurize: true
  use_case_questions_enabled: false
  graph_entity_limit: 5
  generate_surrogate_keys: true
  url_sample_size: 10
```

Other important flags:

* `parser.generate_surrogate_keys`
* `parser.wide_short_homogeneous`
* `parser.wide_short_representative_column`
* `cleaner.monotonicity_tolerance`
* `cleaner.url_sample_size`

LLM prompts are centralized in `dd_common/llm_prompts.py` and should be treated as configuration.

## Troubleshooting

* If `dataset-bootstrap` fails, confirm `data/` and `data_dictionary/` contain valid CSV files.
* If `bootstrap-config` fails, confirm `bootstrap_metadata.yaml` exists and includes the expected fields.
* If `classify-entities` is slow on wide-short datasets, confirm `config.yaml` has `parser.wide_short_homogeneous: true` and `parser.wide_short_representative_column`.
* If `clean-dataset` reports `blocked`, inspect the handshake file and `validation_errors`.

## Testing and validation

* `tests/test_sba_end_to_end.py` validates the full workspace workflow.
* `tests/test_wide_short_end_to_end.py` validates wide-short bootstrap/config coupling and parser behavior.
* Additional parser and cleaner unit tests cover manifest generation and validation logic.

## Programmatic discovery

Use `get_package_info()` to inspect supported CLI commands, schema paths, handshake contract, dataset types, and config flags.

## Notes

* The parser-cleaner preserves existing cross-sectional and graph flows while adding explicit wide-short homogeneous support.
* Bootstrapping now drives the wide-short signal instead of inferring it later.
* Prompt templates are selected based on `config.yaml` structure and wide-short metadata.

**End of user guide.**
