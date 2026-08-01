# dd-parser-cleaner Architecture

## Overview

`dd-parser-cleaner` is an end-to-end dataset discovery and validation toolkit.
It is designed to ingest tabular datasets and output deterministic manifests, diagnostics, and a handshake file that downstream featurizers can use to safely proceed.

## Core modules

- `src/dd_parser`
  - Purpose: classify dataset attributes, infer dataset taxonomy, and emit dataset/attribute manifests.
  - Key responsibilities: schema discovery, semantic tagging, entity detection, time-key inference, and graph/homogeneous dataset handling.
  - Entry point: `classify-entities` CLI command.

- `src/dd_cleaner`
  - Purpose: validate manifests, profile data quality, and export cleaned synchronized datasets.
  - Key responsibilities: integrity checks, null profiling, diagnostics, warning/blocking status generation, and handshake readiness.
  - Entry point: `clean-dataset` CLI command.

- `src/dd_common`
  - Purpose: shared infrastructure for configuration, path coordination, workspace bootstrap, and prompt management.
  - Key responsibilities: `config.yaml` handling, workspace initialization, location utilities, dataset bootstrap, and LLM prompt templates.

## Data flow

1. `init-workspace .`
   - Creates the KMDS workspace layout and supporting document structure.
2. `location-helper .`
   - Validates dataset, dictionary, and document placement.
3. `dataset-bootstrap .`
   - Captures metadata such as dataset type, subject, and representative column information for wide-short homogeneous datasets.
4. `bootstrap-config --output config.yaml .`
   - Reads bootstrap metadata and workspace contents, then writes the authoritative runtime configuration.
5. `classify-entities --config config.yaml`
   - Runs the parser to emit `dataset_manifest.json`, `attribute_manifest.json`, and parser artifacts.
6. `clean-dataset --config config.yaml --action full`
   - Validates manifests, profiles quality, and writes a cleaned dataset along with `handshake.json`.

## Design principles

- `config.yaml` is the single source of truth for runtime behavior.
- Handshake semantics are explicit: downstream consumers must read `handshake.json` and obey `status` values.
- LLM prompts are centralized in `src/dd_common/llm_prompts.py` and kept configuration-driven.
- The system supports tabular dataset taxonomy, homogeneous graphs, and wide-short homogeneous dataset fast-paths.
- Changes are intended to be additive and backward-compatible, especially for manifest outputs.

## Validation contract

- The parser emits canonical manifests describing dataset structure and attribute roles.
- The cleaner performs deterministic validation and produces a readiness signal in `handshake.json`.
- `status` values are:
  - `ready`
  - `blocked`
  - `warnings`

## Developer touchpoints

- `README.md` for product overview and quick start.
- `USER_GUIDE.md` for workflow and CLI usage.
- `documents/path_coordinator_design.md` for routing and path management.
- `tests/` for regression and integration coverage.
