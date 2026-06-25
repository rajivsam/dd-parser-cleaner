# Google OKF Guide for dd-parser-cleaner

## Goal

Document how `dd-parser-cleaner` can be published or shared in a Google / Open Knowledge Foundation (OKF) compatible form, including open-data packaging, metadata requirements, and licensing.

## OKF Compatibility Checklist

- [ ] Data outputs are published under a permissive open license (e.g. MIT, CC0, or ODC-BY).
- [ ] Metadata files describe dataset contents, schema, provenance, and transformation steps.
- [ ] All documentation is available in machine-readable Markdown or JSON formats.
- [ ] Sensitive or private fields are identified and handled before publication.
- [ ] The dataset packaging follows OKF/Open Data standards for directories and manifest files.

## Recommended Artifacts

- `README.md` in the data package describing dataset purpose and contents.
- `LICENSE` or `COPYRIGHT` file for licensing clarity.
- `data_dictionary.csv` or JSON schema file describing each field.
- `parser_cleaner_handshake.md` documenting the parser-cleaner bridge.
- `cleaning_recommendations.md` or report outputs showing cleaning decisions.

## Publication Notes

1. Use `documents/google_okf/` as the staging area for publication notes and compliance checks.
2. Keep a separate `COPYING` or `LICENSE` file for OKF distribution if publication uses a different license than the repository.
3. Document the source dataset, processing steps, and cleaning assumptions clearly.
4. Include a link to `documents/stash.md` or `documents/copilot_stash.md` for design provenance.

## Next Steps

- Identify open datasets created by `dd-parser-cleaner` that are safe to publish.
- Assemble a minimal OKF package with dataset CSV, metadata, license, and README.
- Track publication status and required fixes in this directory.
