# Copilot Session Bootstrap

This file is the session bootstrap guide for the `dd_parser_cleaner` workspace.
Use it together with the packaged agent instructions file `src/dd_common/AGENTS.md` and the files in `documents/` as the basis for the current session.

## Purpose

- Provide Copilot with a concise project overview and workspace entry points.
- Identify the main agent instruction file, the root documentation folder, and the current note files.
- Establish the starting context for feature work, debugging, or documentation updates.

## Hard rule: never fix tests by editing datasets

- Never edit raw fixture CSVs or generated dataset files to make a test pass.
- Never rewrite a dataset to hide a failing validation condition.
- If a dataset file looks synthetic, placeholder, or has been clobbered, stop and restore a trusted copy before changing code or test expectations.
- A passing test on mutated fixture data is not valid evidence of correctness.
- When the dataset or fixtures are suspect, restore the last trusted dataset version, validate schema and row counts, and then rerun tests.

## Key files

- `src/dd_common/AGENTS.md`
  - Packaged agent instructions and workflow guidance for dd-parser-cleaner.
- `copilot_init.md`
  - This session bootstrap document.
- `CLAUDE.md`
  - Project-specific agent policy and workflow guidance.
- `README.md`
  - High-level project overview and quick-start commands.
- `USER_GUIDE.md`
  - User-facing CLI and workflow instructions.
- `WORKSPACE_STRUCTURE.md`
  - Workspace layout and directory conventions.
- `documents/`
  - Detailed design and architecture documentation for the parser, cleaner, paths, configuration, testing, and migration workflows.

## Workspace notes

- The repository is organized around two main modules: `dd_parser` and `dd_cleaner`, with shared infrastructure in `dd_common`.
- `config.yaml` is the single authoritative source of path and model settings.
- The project uses `bd`/Beads for durable issue tracking and workflow metadata.
- Existing documentation is stored in `documents/` and is part of the session foundation.
- Current session updates wide-short homogeneous dataset support for the parser, including bootstrap-config coupling, wide-short-specific prompt selection, and a fast path in `classify-entities`.
- The wide-short flow now includes `graph_homogeneous` bootstrap metadata and a representative column signal that drives prompt and parser behavior rather than inferring it later.

## Recommended first actions

1. Read `src/dd_common/AGENTS.md` for agent behavior and task tracking rules.
2. Read `documents/README.md` if present, otherwise inspect the `documents/` directory.
3. Use `bd prime` to refresh Beads context before working on tracked issues.
4. Keep modifications to documentation and agent instructions self-contained and consistent with existing project conventions.
5. If fixture data looks suspicious or synthetic, restore the trusted dataset before running validation.
