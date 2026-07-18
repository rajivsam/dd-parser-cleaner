# dd-parser-cleaner Product

## What it does

`dd-parser-cleaner` helps teams ingest and validate enterprise tabular datasets by automatically discovering data semantics, generating deterministic manifests, and enforcing a handshake contract before featurization.

## Why it matters

- Reduces manual dataset onboarding effort.
- Ensures structural consistency and semantic correctness before downstream modeling.
- Provides explicit readiness signals so featurizers do not proceed on invalid data.

## Key functionality

- Detects dataset taxonomy such as `cross_sectional`, `event_log`, `panel`, and graph variants.
- Tags attributes with roles, modalities, and time semantics.
- Emits canonical dataset and attribute manifests.
- Validates manifests through deterministic cleaner diagnostics.
- Produces a `handshake.json` readiness contract for downstream consumers.

## Primary users

- Data engineers onboarding new datasets.
- ML engineers building feature pipelines.
- Analysts validating dataset structure and quality.

## Typical workflow

1. Initialize the workspace.
2. Confirm file placement.
3. Bootstrap dataset metadata.
4. Generate runtime config.
5. Run parser classification.
6. Run cleaner validation and export clean output.
7. Downstream featurizers read `handshake.json` and proceed only if `status == "ready"`.

## Output artifacts

- `documents/dd_analysis_results/<dataset_id>_dataset_manifest.json`
- `documents/dd_analysis_results/<dataset_id>_attribute_manifest.json`
- `documents/dd_cleaner/<dataset_id>_parser_cleaner_handshake.md`
- `data/dd_cleaner/<dataset_id>_clean.csv`
- `schemas/` for manifest validation

## Differentiators

- Combines metadata discovery and deterministic cleaning in one workflow.
- Supports wide-short homogeneous dataset fast paths.
- Writes explicit downstream handshake contracts.
- Keeps runtime behavior config-driven and reproducible.
