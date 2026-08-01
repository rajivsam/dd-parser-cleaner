# 🤖 Copilot Initialization Stash: dd-parser-cleaner v0.4.6

**PURPOSE**: Quick context bootstrap for feature development sessions. Reference this at session start.

**PROJECT STATE**: Maintenance Mode. v0.4.6 baseline locked. Ready for feature additions without active refactoring.

---

## 🏗️ Core Architecture at a Glance

### Three Interconnected Modules

#### 1. **dd_parser** — Semantic Classification & Entity Discovery
- **Entry**: `src/dd_parser/cli.py` → CLI command: `classify-entities`
- **Orchestrator**: `PipelineOrchestrator` (orchestrator.py)
- **LLM Client**: `LLMEntityClassifier` (llm_client.py) — Ollama-based, JSON-only responses
- **Validation**: `IntegrityEngine` (rules.py) — Schema bridge validation (Operational/Orphans/Ghosts)
- **Output**: `MetadataPostProcessor` → CSV matrix + Markdown report + Handshake file
- **Prompts**: Externalized to `src/dd_common/llm_prompts.py`

#### 2. **dd_cleaner** — Data Quality & Profiling  
- **Entry**: `src/dd_cleaner/cli.py` → CLI commands: `clean-dataset --action [integrity|profile|assessment|full]`
- **Orchestrator**: `CleanerOrchestrator` (orchestrator.py) — Sequential 3-stage pipeline
- **Profiler**: `DatasetDataProfiler` (null_profiler.py) — JSON + Markdown quality reports
- **Assistant**: `CleaningAssistant` (assistant.py) — LLM + heuristics for recommendations
- **Reporter**: `CleaningReportManager` (reporter.py) — Clean CSV + Signature sidecars
- **Stages**: Integrity Sync → Null Profiling → LLM Assessment → Persistence

#### 3. **dd_common** — Shared Infrastructure
- **PathCoordinator** (path_coordinator.py): Single source of truth for all paths; anchored to `config.yaml`
- **LLM Prompts** (llm_prompts.py): Centralized prompt templates (JSON-only, temperature 0.0)
- **CLI Helpers**: bootstrap_cli.py, location_cli.py, workspace_cli.py, workspace_init.py
- **Utilities**: Common functions, path resolution, logging

---

## 🔑 Critical Constraints & Golden Rules

1. **NO MOCKING**: All testing uses real data files within the project. Test isolation via simulated KMDS layout in `tests/` subdirectory.
2. **Raw Data Sacrosanct**: Never modify the source `raw_dataset_file`. All transformations flow through orchestrators.
3. **Domain Agnosticism**: Zero hardcoded domain logic. All domain specifics injected via `config.yaml` or discovered in Domain Discovery phase.
4. **PathCoordinator Mandatory**: All file operations route through `PathCoordinator.config` + properties (e.g., `self.paths.raw_dataset_path`). NO hardcoded paths.
5. **Config as Law**: `config.yaml` is the single source of truth. Working directory, model name, timeouts, prompts, file names — all defined there.
6. **Handshake Protocol**: Cleaner enforces existence of `parser_cleaner_handshake.md` before execution (safety gate).
7. **LLM JSON-Only**: Prompts demand strict JSON responses. Temperature locked at 0.0 for determinism.

---

## 📁 Directory Structure & Entry Points

```
src/
├── dd_cleaner/          # Data cleaning & profiling
│   ├── cli.py          # Entry: clean-dataset CLI
│   ├── orchestrator.py  # CleanerOrchestrator (integrity→profile→assessment)
│   ├── assistant.py     # CleaningAssistant (LLM recommendations)
│   ├── null_profiler.py # DatasetDataProfiler (JSON+Markdown quality)
│   ├── reporter.py      # CleaningReportManager (CSV output + sidecar)
│   ├── pipeline.py      # Pipeline runner
│   ├── rules.py         # Validation rules
│   ├── validator.py     # Data validators
│   └── notebook_utils.py
├── dd_parser/           # Semantic classification
│   ├── cli.py          # Entry: classify-entities CLI
│   ├── orchestrator.py  # PipelineOrchestrator (domain→entity discovery)
│   ├── llm_client.py    # LLMEntityClassifier (Ollama API)
│   ├── rules.py         # IntegrityEngine (schema bridge validation)
│   ├── structural_assessor.py
│   ├── post_processor.py # MetadataPostProcessor
│   ├── document_processor.py
│   └── py.typed
└── dd_common/           # Shared infrastructure
    ├── path_coordinator.py  # PathCoordinator (path routing)
    ├── llm_prompts.py       # PROMPT_TEMPLATES (entity_classifier, document_processor)
    ├── bootstrap_cli.py
    ├── location_cli.py
    ├── workspace_cli.py
    ├── workspace_init.py
    └── utilities.py

tests/
├── conftest.py          # Fixture: managed_test_config (single authoritative config.yaml)
├── test_cleaner.py      # Cleaner validation tests
├── test_parser.py       # Parser validation tests
├── test_normalization.py
├── data/               # Test datasets
│   ├── data.csv
│   ├── dd.csv
│   └── quarantine/    # Mixed-type isolation
└── data_dictionary/    # Test metadata

documents/
├── stash.md                        # Authoritative v0.4.6 state (read first)
├── transfer_to_migration.md        # Agent-Programmer's Handbook
├── dataset_bootstrapping_guide.md  # Dataset type questionnaire and bootstrapping guide
├── path_coordinator_design.md      # Path routing architecture
├── location_utility.md             # Onboarding guide
├── testing_dd_parser.md            # Test infrastructure
├── copilot_stash.md               # THIS FILE (session bootstrap)
└── archived/                       # Obsolete and historical docs
    ├── consolidated_design_doc_dd-parser-cleaner.md
    ├── datasheet_alignment.md      # 5 planned features (not implemented)
    ├── features_from_Provost_Fawcett.md  # Featurization Tool (future)
    ├── features_from_Pyles_text.md       # Featurization Tool (future)
    ├── google_okf/
    ├── policy_manifest_schema.json
    ├── upcoming_features/
    └── wide_and_short_mod.md
```

---

## ⚙️ Configuration Structure

### Global Section
```yaml
working_dir: /path/to/workspace    # Single source of truth for base paths
model_name: llama3.2               # Ollama model identifier
temperature: 0.0                   # Deterministic (lock at 0.0)
llm_timeout: 60.0                  # Canary timeout; >60s = CPU fallback
documents_dir: documents           # Reports & artifacts
system_prompt: "..."               # LLM behavior instruction
```

### Parser Section
```yaml
parser:
  data_dictionary_file: name.csv   # Input: metadata schema
  data_dictionary_attribute_col_name: "Field Name"  # Column holding attribute names
  dd_parser_output_dir: dd_analysis_results        # Output directory name
  output_filename: results.csv     # Output CSV matrix
  entity_tagging: [geographic, ...]  # Feature flags to evaluate
  prompts:
    entity_classifier:
      macro_domain_template: "..."  # Prompt 1: coarse entity concepts
      entity_discovery_template: "..."  # Prompt 2: per-field classification
    document_processor:
      system: "..."
      discovery_template: "..."
  overrides: {}                   # Escape hatch: force-assign specific attributes
```

### Cleaner Section
```yaml
cleaner:
  raw_dataset_file: data.csv      # Input: operational table
  clean_output_filename: clean.csv # Output file name
  dd_cleaner_output_dir: dd_cleaner  # Output directory name
  handshake_file: parser_cleaner_handshake.md  # Safety gate file
  quarantine_dir: quarantine      # Mixed-type isolation dir
  pipeline: [integrity, profile, assessment]  # Execution sequence
  structural_assessment:
    null_threshold: 0.95            # Nullity threshold for flagging
    auto_drop_constant: false       # Auto-drop constant columns
  missing_values:
    prompts:
      cleaning_assistant:
        system: "..."
        recommendation_template: "..."
```

### Top-level dataset type
```yaml
dataset_type: cross-sectional   # User-controlled dataset type; set to 'panel' for longitudinal data
```

---

## 🧪 Testing Patterns

- **Framework**: pytest + real data (NO unittest.mock)
- **Config**: `conftest.py` fixture points to single authoritative `config.yaml` at workspace root
- **Isolation**: Simulated KMDS layout in `tests/` subdirectory (data/, data_dictionary/, documents/)
- **Data**: Real CSV files in tests/data/ (sba_loans_raw.csv, sba_dd.csv, etc.)
- **Run**: `uv run pytest` or `uv run pytest tests/test_cleaner.py`

---

## 🤖 LLM Integration Patterns

### Ollama Client (llm_client.py)
```python
# LLMEntityClassifier pattern:
1. Assembly Phase: Format prompt template with context
2. Execution Phase: httpx.post("http://localhost:11434/api/generate", ...)
3. Processing Phase: Parse JSON response, validate structure
```

### Prompts (llm_prompts.py)
```python
PROMPT_TEMPLATES = {
    "parser": {
        "prompts": {
            "entity_classifier": {
                "macro_domain_template": "...",
                "entity_discovery_template": "..."
            },
            "document_processor": {
                "system": "...",
                "discovery_template": "..."
            }
        }
    },
    "cleaner": {
        "missing_values": {
            "prompts": {
                "cleaning_assistant": {
                    "system": "...",
                    "recommendation_template": "..."
                }
            }
        }
    }
}
```

---

## ✅ Ready-to-Implement Feature Areas

These follow established patterns and don't require architectural changes:

### 1. New Diagnostic Checks
- Duplicate detection (IntegrityEngine)
- Cardinality anomalies (DatasetDataProfiler)
- Format violations (null_profiler)
- Add as new pipeline stages or post-processing steps

### 2. New LLM Classifiers
- Extend `entity_tagging` list in config
- Add new prompt templates to `llm_prompts.py`
- Update `LLMEntityClassifier.entity_discovery_template` logic

### 3. New Pipeline Actions
- Add stages to `cleaner.pipeline` config
- Implement action handlers in `CleanerOrchestrator.run_pipeline()`
- Example: `--action quality-gates` for advanced validation

### 4. New Reports & Outputs
- Extend `CleaningReportManager` methods
- Add new output formats (JSON, CSV matrices, etc.)
- Generate alongside existing Markdown + CSV

### 5. Config Extensions
- Add new sections to config.yaml (e.g., `validation_rules`)
- Access via `self.config.get("validation_rules")` throughout
- Validate in `PathCoordinator` or `_verify_*` methods

### 6. New CLI Commands
- Create new script in `src/dd_common/` (e.g., `quality_gates_cli.py`)
- Register in `pyproject.toml` entry_points
- Follow `cli.py` pattern: PathCoordinator → Orchestrator → Action

---

## 📋 Session Workflow Protocol

Each session follows this pattern:

1. **INITIALIZE**: Read this file (`copilot_stash.md`) at session start
2. **SELECT TASK**: Define specific feature or fix to implement
3. **IMPLEMENT**: Code changes, tests, updates following patterns above
4. **VALIDATE**: Run tests (`uv run pytest`), verify CLI execution
5. **UPDATE STASH**: Record progress, new patterns, completed features
6. **SIGN OFF**: Summarize what was done and what remains

---

## 📊 Session Progress Log

| Date | Task | Status | Notes |
|------|------|--------|-------|
| 2026-06-05 | Documentation audit & archival | ✅ Complete | Moved 5 obsolete docs to `archived/`. Created this copilot_stash.md. |

---

## 🔗 Key References

- **Authoritative State**: [stash.md](stash.md) — v0.4.6 baseline, constraints, design decisions
- **Implementation Guide**: [transfer_to_migration.md](transfer_to_migration.md) — Agent-Programmer's Handbook
- **Architecture**: [path_coordinator_design.md](path_coordinator_design.md), [cleaner_design.md](cleaner_design.md)
- **Testing**: [testing_dd_parser.md](testing_dd_parser.md)
- **Future Roadmap**: [archived/](archived/) — 5 planned features for v0.5+

---

**Last Updated**: June 5, 2026  
**Session**: Initial copilot context bootstrap
