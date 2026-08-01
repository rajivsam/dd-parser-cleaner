# dd-parser-cleaner Agent Instructions

This file provides package-specific workflow guidance for dd-parser-cleaner.

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

## Notes

- `config.yaml` is the authoritative runtime configuration.
- `documents/` holds durable onboarding and prompt guidance.
- Use non-interactive shell flags for file operations: `cp -f`, `mv -f`, `rm -f`, `cp -rf`, `rm -rf`.
- Prefer `bd` issue tracking over markdown TODOs.
