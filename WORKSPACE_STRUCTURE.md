# 📐 Workspace Structure & Navigation Guide

This document maps the `dd-parser-cleaner` workspace layout, explains the purpose of each directory, and guides developers to the right place for common tasks.

---

## 🏗️ Directory Layout at a Glance

```
dd_parser_cleaner/
├── src/                          # Main application code
│   ├── dd_parser/               # Semantic classification & entity discovery
│   ├── dd_cleaner/              # Data quality profiling & cleaning
│   └── dd_common/               # Shared infrastructure & utilities
├── tests/                        # Test suite (real data, no mocking)
├── documents/                    # Documentation hub
│   ├── copilot_stash.md         # Session bootstrap and developer context
│   ├── stash.md                 # Authoritative v0.4.6 state
│   ├── transfer_to_migration.md # Agent-programmer handbook
│   ├── dataset_bootstrapping_guide.md # Dataset bootstrapping guide
│   ├── path_coordinator_design.md # Path routing architecture
│   ├── location_utility.md      # Onboarding guide
│   ├── testing_dd_parser.md     # Test infrastructure
│   └── archived/                # Obsolete and historical docs
├── config.yaml                   # Single source of truth for workspace config
├── pyproject.toml               # Python project metadata & CLI entry points
└── README.md                     # Project overview
```

---

## 🗂️ Module Breakdown & Documentation Map

### **src/dd_parser/** — Semantic Classification & Entity Discovery

**Purpose**: Classifies data dictionary attributes into logical entities and evaluates semantic tags via LLM.

**Key Files**:
- `orchestrator.py` — `PipelineOrchestrator` (entry point)
- `llm_client.py` — `LLMEntityClassifier` (Ollama integration)
- `rules.py` — `IntegrityEngine` (schema bridge validation)
- `post_processor.py` — `MetadataPostProcessor` (output assembly)
- `cli.py` — CLI entry point: `classify-entities`

**Relevant Documentation**:
- Start here: [documents/copilot_stash.md](documents/copilot_stash.md) (module overview + patterns)
- Detailed design: [documents/transfer_to_migration.md](documents/transfer_to_migration.md) (workflow + constraints)
- Architecture: [documents/path_coordinator_design.md](documents/path_coordinator_design.md) (routing + config)

**Common Tasks**:
- ❓ **Add a new entity tagging feature** → Modify `entity_tagging` in config.yaml, update `llm_prompts.py`, extend `LLMEntityClassifier`
- ❓ **Change LLM prompts** → Edit `src/dd_common/llm_prompts.py`; prompts are config-driven
- ❓ **Fix schema validation logic** → Modify `IntegrityEngine.evaluate_bridge()` in `rules.py`
- ❓ **Debug classifier output** → Check `MetadataPostProcessor.assemble_matrix()` logic

---

### **src/dd_cleaner/** — Data Quality Profiling & Cleaning

**Purpose**: Profiles dataset quality, generates diagnostics, and recommends cleaning actions via LLM.

**Key Files**:
- `orchestrator.py` — `CleanerOrchestrator` (pipeline orchestrator: integrity→profile→assessment)
- `null_profiler.py` — `DatasetDataProfiler` (quality metrics + Markdown/JSON reports)
- `assistant.py` — `CleaningAssistant` (LLM-driven recommendations)
- `reporter.py` — `CleaningReportManager` (output serialization)
- `cli.py` — CLI entry point: `clean-dataset --action [integrity|profile|assessment|full]`

**Relevant Documentation**:
- Start here: [documents/copilot_stash.md](documents/copilot_stash.md) (module overview + patterns)
- Pipeline design: [documents/transfer_to_migration.md](documents/transfer_to_migration.md) (workflow and constraints)
- Configuration: `config.yaml` and `README.md` (runtime configuration)
- Testing: [documents/testing_dd_parser.md](documents/testing_dd_parser.md) (test infrastructure)

**Common Tasks**:
- ❓ **Add a new quality metric** → Extend `DatasetDataProfiler.generate_null_quality_report()`
- ❓ **Add a new pipeline stage** → Add action to `CleanerOrchestrator.run_pipeline()`, update `config.yaml` `pipeline` list
- ❓ **Customize cleaning recommendations** → Modify `CleaningAssistant.generate_recommendations()`
- ❓ **Change output format** → Extend `CleaningReportManager` methods
- ❓ **Adjust null threshold for flagging** → Modify `config.yaml` `cleaner.structural_assessment.null_threshold`

---

### **src/dd_common/** — Shared Infrastructure

**Purpose**: Provides centralized routing, LLM prompt templates, and onboarding utilities.

**Key Files**:
- `path_coordinator.py` — `PathCoordinator` (zero-hardcoding path routing via config.yaml)
- `llm_prompts.py` — `PROMPT_TEMPLATES` (centralized LLM prompt definitions)
- `bootstrap_cli.py` — `bootstrap-config` command (auto-generate config from workspace)
- `location_cli.py` — `location-helper` command (onboarding file placement guide)
- `workspace_cli.py` — `init-workspace` command (KMDS directory initialization)

**Relevant Documentation**:
- Start here: [documents/copilot_stash.md](documents/copilot_stash.md) (infrastructure overview)
- Path routing: [documents/path_coordinator_design.md](documents/path_coordinator_design.md) (routing contract)
- Config reference: `config.yaml` and `README.md` (runtime configuration)
- Onboarding: [documents/location_utility.md](documents/location_utility.md) (setup workflow)

**Common Tasks**:
- ❓ **Add a new path routing endpoint** → Add property to `PathCoordinator` (e.g., `@property def new_path()`)
- ❓ **Add a new config section** → Define in `config.yaml`, access via `self.config.get("section")`
- ❓ **Update LLM prompts** → Edit `PROMPT_TEMPLATES` dict in `llm_prompts.py`
- ❓ **Add a new CLI command** → Create script in `dd_common/`, register in `pyproject.toml` entry_points

---

## 📚 Documentation Directory Hierarchy

### **documents/** — Current Documentation (Active & Reference)

**Read First**:
- [**copilot_stash.md**](documents/copilot_stash.md) — Session bootstrap and developer context.
- [**stash.md**](documents/stash.md) — Authoritative workflow and project state.

**Deep Dives** (Pick by topic):
- [transfer_to_migration.md](documents/transfer_to_migration.md) — Agent-programmer handbook and operational workflow.
- [dataset_bootstrapping_guide.md](documents/dataset_bootstrapping_guide.md) — Dataset type questionnaire and bootstrapping guidance.
- [path_coordinator_design.md](documents/path_coordinator_design.md) — Path routing architecture and coordinator contract.
- [location_utility.md](documents/location_utility.md) — Workspace file placement guidance.
- [testing_dd_parser.md](documents/testing_dd_parser.md) — Test infrastructure and suite overview.

### **documents/archived/** — Obsolete and historical documentation
- `documents/archived/` contains moved design notes, deprecated references, and future-planning artifacts.

Contains:
- `parser_methodology.md` (stub, 1 line)
- `datasheet_alignment.md` (future, not implemented)
- `features_from_Provost_Fawcett.md` (future, not implemented)
- `features_from_Pyles_text.md` (future, not implemented)
- `README.md` (archive explanation)

**Use case**: Understanding future roadmap, historical context, or completed-but-archived work.

---

## 🚀 Quick Navigation by Task

### **I'm starting a new feature development session**
1. Read [documents/copilot_stash.md](documents/copilot_stash.md) ← Start here
2. Clarify which module (dd_parser, dd_cleaner, or dd_common)
3. Review the relevant deep-dive doc (see "Documentation Directory Hierarchy" above)
4. Check [documents/upcoming_features/](documents/upcoming_features/) for design guidance
5. Update copilot_stash.md progress log at end of session

---

### **I'm implementing a parser feature (semantic classification)**
1. Read [documents/copilot_stash.md](documents/copilot_stash.md) — dd_parser section
2. Review [documents/transfer_to_migration.md](documents/transfer_to_migration.md) — workflow context
3. Check current code: `src/dd_parser/llm_client.py` (LLMEntityClassifier)
4. Modify as needed, follow LLM integration patterns (Assembly → Execution → Processing)
5. Test via `uv run pytest tests/test_parser.py`

---

### **I'm implementing a cleaner feature (profiling or recommendations)**
1. Read [documents/copilot_stash.md](documents/copilot_stash.md) — dd_cleaner section
2. Review [documents/transfer_to_migration.md](documents/transfer_to_migration.md) — workflow context
3. Check current code: `src/dd_cleaner/orchestrator.py` (pipeline stages)
4. Modify as needed, follow orchestrator patterns (Stage execution, error handling, reporting)
5. Test via `uv run pytest tests/test_cleaner.py`

---

### **I'm adding a new CLI command**
1. Read [documents/copilot_stash.md](documents/copilot_stash.md) — CLI commands section
2. Review an existing CLI: `src/dd_parser/cli.py` or `src/dd_cleaner/cli.py`
3. Create new script in `src/dd_common/` (e.g., `my_feature_cli.py`)
4. Import orchestrator, call `run_pipeline()` or equivalent
5. Register in `pyproject.toml` under `[project.scripts]`
6. Test via `uv run my-feature-command`

---

### **I'm modifying configuration**
1. Read [documents/transfer_to_migration.md](documents/transfer_to_migration.md) — workflow context
2. Review [documents/path_coordinator_design.md](documents/path_coordinator_design.md) — routing pattern
3. Edit `config.yaml` directly (single source of truth)
4. Access via `self.config.get("key")` or `self.paths.<property_name>`
5. Test via `uv run pytest` (conftest.py fixture validates config)

---

### **I'm understanding data flow**
1. Start: [documents/stash.md](documents/stash.md) — workflow overview (init → location → bootstrap → classify → clean)
2. Deep dive: [documents/path_coordinator_design.md](documents/path_coordinator_design.md) — routing contract
3. Check diagram in path_coordinator_design.md (shows module dependencies)
4. Trace code: `src/dd_common/path_coordinator.py` → entry points → orchestrators

---

### **I'm writing tests**
1. Read [documents/testing_dd_parser.md](documents/testing_dd_parser.md)
2. Review `tests/conftest.py` (single authoritative config.yaml fixture)
3. Check `tests/test_cleaner.py` or `tests/test_parser.py` for patterns
4. Use real data from `tests/data/` (NO mocking per Golden Rule)
5. Run: `uv run pytest` or `uv run pytest tests/test_cleaner.py -s`

---

## 🔑 Key Files Everyone Should Know

| File | Purpose | Who Needs It |
|------|---------|-------------|
| `config.yaml` | Single source of truth for all config | Everyone |
| `documents/copilot_stash.md` | Session bootstrap for developers | Feature devs |
| `documents/stash.md` | Authoritative v0.4.6 state | Everyone (read once) |
| `src/dd_common/path_coordinator.py` | All path resolution | Code reviewers, architects |
| `src/dd_common/llm_prompts.py` | LLM prompt definitions | Anyone tweaking LLM behavior |
| `pyproject.toml` | CLI entry points, dependencies | Package devs, CI/CD |
| `tests/conftest.py` | Test config fixture | Test writers |

---

## 🏆 Best Practices Enforced by Structure

1. **No Hardcoded Paths** — Use `PathCoordinator` properties everywhere
2. **No Mocking in Tests** — Real data only, simulated KMDS workspace isolation
3. **Domain Agnostic** — All domain logic in `config.yaml` or extracted via LLM
4. **Config-Driven** — Prompts, paths, timeouts, thresholds all in config.yaml
5. **Modular Imports** — Each module imports from `dd_common` for shared infrastructure
6. **Dependency Injection** — Orchestrators receive `PathCoordinator`, avoid global state

---

## 📊 Workspace Health Checklist

Use this to verify workspace cleanliness:

- [ ] All active docs in `documents/` (7 files + copilot_stash.md)
- [ ] Obsolete docs in `documents/archived/` with README
- [ ] Upcoming features in `documents/upcoming_features/` with prioritization table
- [ ] No `.py` files with hardcoded paths (search for `/path/`, `C:\`, `.csv` literals)
- [ ] All CLI commands registered in `pyproject.toml` entry_points
- [ ] Tests use `conftest.py` fixture, not independent config files
- [ ] LLM prompts in `llm_prompts.py`, not scattered across modules
- [ ] `config.yaml` is single source of truth (no .local, .dev, .prod variants)

---

**Last Updated**: June 5, 2026  
**Workspace Version**: Organized & documented for multi-session feature development  
**Next Recommended Read**: [documents/copilot_stash.md](documents/copilot_stash.md)
