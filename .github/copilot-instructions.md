# dd-parser-cleaner AI Context Instructions

These instructions provide persistent project context for VS Code AI agents and Copilot.
They are included automatically in all chat interactions.

## Project overview

`dd-parser-cleaner` is a local dataset discovery and validation toolkit.
It ingests tabular datasets, emits validated dataset and attribute manifests, runs deterministic cleaning checks, and writes a handshake file for downstream featurizers.

Key modules:
- `src/dd_parser`: semantic classification, entity discovery, dataset taxonomy, and manifest emission
- `src/dd_cleaner`: data quality profiling, diagnostics, validation, and clean dataset export
- `src/dd_common`: path coordination, workspace bootstrap, configuration, shared utilities, and LLM prompt templates

Important docs:
- [README.md](../README.md)
- [USER_GUIDE.md](../USER_GUIDE.md)
- [WORKSPACE_STRUCTURE.md](../WORKSPACE_STRUCTURE.md)
- [documents/copilot_stash.md](../documents/copilot_stash.md)
- [documents/path_coordinator_design.md](../documents/path_coordinator_design.md)
- [documents/dataset_bootstrapping_guide.md](../documents/dataset_bootstrapping_guide.md)
- [documents/testing_dd_parser.md](../documents/testing_dd_parser.md)
- [ARCHITECTURE.md](../ARCHITECTURE.md)
- [PRODUCT.md](../PRODUCT.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)

## Coding and behavior guidelines

- Prefer small, incremental edits. Validate each behavior with tests when possible.
- Maintain existing CLI commands and runtime config semantics.
- Use `config.yaml` as the authoritative runtime configuration source.
- Preserve the handshake contract: downstream featurizers must read `handshake.json` and obey `status` values.
- Avoid introducing new top-level dependencies unless necessary.
- Keep documentation and agent guidance consistent with existing project conventions.

## Workspace conventions

- Use `bd prime`, `bd ready`, `bd show`, `bd update`, and `bd close` for task tracking.
- Do not create markdown TODO lists in code; use Beads for durable issues.
- Respect the repository layout: source code in `src/`, docs in `documents/`, tests in `tests/`.
- Use the current Python environment from `.venv` and run tests with `uv run pytest`.

## Agent workflows

- Planning requests should be answered using the project's docs and codebase.
- Implementation requests should be done with focused, test-backed changes.
- For complex refactors, create or update supporting docs in `documents/`.
- If you see missing or incomplete documentation, improve the docs before implementing features that depend on them.
