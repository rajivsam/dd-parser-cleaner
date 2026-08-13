# dd-parser-cleaner Agent Instructions

This file provides package-specific workflow guidance for dd-parser-cleaner.

## Hard rule: never fix tests by editing dataset fixtures

- Never modify raw source CSVs in `tests/data/` or any generated dataset artifact to make a test pass.
- Never change fixture values, row counts, or headers to satisfy a failing test.
- If a dataset file is synthetic, placeholder, or clearly clobbered, restore the original trusted source before changing code or validation expectations.
- Investigate root cause first: confirm schema, row count, and data realism before running or rewriting tests.
- A passing test on altered fixture data is not valid evidence that the data is correct.
- If the data is suspect, stop and restore the last known-good dataset version before continuing.

## Workflow

1. Confirm dataset and workspace location with the user.
2. Run `init-workspace .` if the KMDS workspace is not initialized.
3. Run `location-helper .` to verify `data/`, `data_dictionary/`, and `documents/`.
4. Run `dataset-bootstrap .` to capture dataset metadata.
5. Run `bootstrap-config --output config.yaml .` to generate the active runtime config.
   - This step is required to propagate bootstrap answers into `config.yaml` for parser, cleaner, and notebook metadata flows.
6. Run `classify-entities --config config.yaml` to produce parser artifacts and the handshake file.
7. Run `clean-dataset --config config.yaml --action full` to validate manifests and export the cleaned dataset.
8. Explain that downstream tools must read the handshake file and proceed only when `status == "ready"`.

## Data recovery and verification requirements

- Treat single-row placeholder files as a data-integrity problem, not as valid fixtures.
- Use schema and row-count checks before trusting parser or cleaner results.
- Prefer restoring a known-good dataset copy from an artifact workspace, a clean checkout, or git history over editing the corrupted file.
- After restoring the data, rerun the relevant tests to validate the actual fix.

## Notes

- `config.yaml` is the authoritative runtime configuration.
- `documents/` holds durable onboarding and prompt guidance.
- Use non-interactive shell flags for file operations: `cp -f`, `mv -f`, `rm -f`, `cp -rf`, `rm -rf`.
- Prefer `bd` issue tracking over markdown TODOs.
- Never treat a passing test on a mutated fixture as evidence that the source data is valid.
