# Google OKF Project Setup Notes

## Purpose

Capture the project-specific setup and decisions needed to prepare `dd-parser-cleaner` outputs for Google / OKF publication.

## Project Setup

- **Project Name:** dd-parser-cleaner
- **Target Publication Format:** Open Knowledge Foundation (OKF) / Google Open Data compatible package
- **License:** MIT for code, open license for published data outputs (consider CC0 or ODC-BY)

## Required OKF Components

- `README.md` describing the dataset and its intended use
- `LICENSE` or `COPYRIGHT` statement for the published package
- `data_dictionary.csv` or equivalent field-level schema metadata
- `parser_cleaner_handshake.md` describing the parser-cleaner safety gate
- `cleaning_recommendations.md` or quality report summary

## Publishing Decisions

- **Use the repository `config.yaml` for inference, but do not publish internal config values unless they are part of the open dataset package.**
- **Keep sensitive or private fields out of published datasets.** Document all excluded fields in the package README.
- **If the dataset is synthetic or anonymized, include a data quality statement in the package metadata.**

## Staging and Validation

1. Stage publication artifacts in `documents/google_okf/` before final packaging.
2. Validate metadata completeness: title, description, author, license, provenance.
3. Verify that the package directory structure is consistent with OKF/Open Data guidelines.
4. Keep a brief changelog in this file for publication-ready document versions.

## Notes

- This directory is intended for publication preparation and should not replace the core design docs in `documents/`.
- Keep all OKF-specific notes here so they can be reviewed independently from engineering documentation.
