# Contributing to dd-parser-cleaner

## Contribution overview

Contributions should be small, focused, and test-backed. Follow the repository conventions and keep `config.yaml` as the authoritative runtime configuration source.

## Getting started

1. Create a Beads issue or claim an existing task with `bd ready` and `bd update <id> --claim`.
2. Run the current Python environment: `source .venv/bin/activate`.
3. Use the repository's scripts via `uv run`.

## Coding conventions

- Put implementation in `src/dd_parser`, `src/dd_cleaner`, or `src/dd_common`.
- Avoid adding top-level dependencies unless necessary.
- Keep CLI entry points consistent with `pyproject.toml`.
- Centralize prompt text in `src/dd_common/llm_prompts.py`.
- Preserve the handshake semantics for downstream consumers.

## Documentation

- Update `README.md` or `USER_GUIDE.md` when workflows change.
- Add or improve `documents/` design docs for architectural or behavioral changes.
- Use `ARCHITECTURE.md`, `PRODUCT.md`, and `CONTRIBUTING.md` for high-level project context.

## Testing

- Add regression coverage in `tests/`.
- Prefer integration-style tests that exercise actual data flows.
- Run tests using `uv run pytest`.

## Agent and context workflows

- Use `.github/copilot-instructions.md` for persistent agent context.
- Use `.github/agents/plan.agent.md` for planning and `.github/agents/implement.agent.md` for implementation.
- Use `plan-template.md` for structured implementation plans.

## Beads workflow

- Use `bd prime` to refresh Beads context.
- Use `bd ready`, `bd show`, `bd update`, `bd close` as your task lifecycle.
- Do not create ad hoc markdown TODOs in code; use Beads for durable issue tracking.

## Pull request guidance

- Summarize changes clearly.
- Reference tests added or updated.
- Highlight any docs or config changes.
- Keep PR scope focused on one feature or fix.
