# 📑 Project Stash: Data Dictionary Parser & Cleaner State

## 🏆 THE GOLDEN RULE
* **NO MOCKING**: All testing and development must be performed using the actual data files and configuration within the project. No temporary sandboxes, fakes, or `unittest.mock` objects for project resources.

## 🤖 Agent Operational Directives
* **Domain Agnosticism**: Strict requirement. Zero hardcoded domain-specific items, magic numbers, or regulatory assumptions. All domain logic must be injected via config or discovered via the "Domain Discovery" phase.
* **Config Management (STRICT)**: The `working_dir` variable in `config.yaml` is the single source of truth for the workspace. All paths resolved via `PathCoordinator` are relative to this root.
*   **Behavioral Change Awareness**: Before suggesting changes that modify existing logic in `domain_logic.py` or functional settings in `config.yaml`, the agent must explicitly notify the user of the expected change in behavior.
*   **Raw Data Verification**: The agent must strictly verify that every attribute name referenced in code or configuration changes matches an existing column in the raw dataset file to prevent schema drift and runtime errors.
* **KMDS Handshake Protocol**: The Cleaner enforces the existence of `parser_cleaner_handshake.md` (the "handshake file") in `documents/dd_cleaner/` before execution. This file serves as the fixed "Inbox" artifact produced by the Parser and contains semantic context for discovery.
* **Implementation Boundary**: The core package (CLI) provides diagnostics and recommendations. Implementation of cleaning logic happens in the "Migration" phase via the Agent writing to `scripts/domain_logic.py`.

## 🎭 User Experience (UX) Personas & Interaction Paths [LOCKED]
*   **Phase 1: Diagnostic Shell**: User sets `working_dir` in `config.yaml` and runs `classify-entities` followed by `clean-dataset --action full`.
*   **Phase 2: Migration Assistant**: User bootstraps the Agent with the produced recommendations and guides. The Agent then generates `domain_logic.py` and `config.yaml` overrides.
*   **Safety Gate**: The Cleaner enforces the presence of the Handshake file produced by the Parser.
 
## 🛠️ Active Project State (Last Updated: May 31, 2026 - Baseline v0.4.2)

### ✅ Baseline Complete: Feature Implementation & Testing Finished
* **Status**: **v0.4.2 Published to PyPI**. All core diagnostic, parsing, and cleaning orchestration features are implemented and validated.
* **Backlogs**: None. The project has moved out of active feature development.
* **Next Action**: Maintenance and bug fixes as required.
* **Workflow**: `pip install dd-parser-cleaner` -> Standard Diagnostic/Migration flow.

### 1. Core Architecture
* **Infrastructure**: `PathCoordinator` enforces zero-default path resolution via `config.yaml`.
* **Baseline Status**: v0.4.2 Production Baseline Locked. The tool provides semantic intelligence and data quality baselines.
* **Cleaner Orchestration**: Simplified 3-step Diagnostic Sequence:
    1. **Integrity Sync**: Reconcile Dictionary vs Raw (Intersection subsetting/Clean Bucket).
    2. **Null Profiling**: Generate MD and JSON quality baselines.
    3. **Assessment**: LLM-augmented cleaning recommendations and `provisional_config.yaml`.
    4. **Persistence**: Export synchronized "Clean Bucket" dataset for migration handover.
* **Data Quality & Grounding**: `DatasetDataProfiler` generates timestamped Markdown reports and JSON metadata sidecars including `logical_type` to ground LLM inference (Task 4.1).
* **Orchestrator**: Executes a two-phase LLM pipeline (Macro Discovery + Atomic Row Assignment) synchronized with physical headers. Handshake Safety Gate is active.
* **Classification**: Phase 1 establishes logical entities; Phase 2 executes atomic row assignment via Llama 3.2.
* **LLM Prompt Management**: All LLM interactions now follow an **Assembly -> Execution -> Processing** pattern, with prompts externalized to `config.yaml`.
* **Integrity Engine**: `IntegrityEngine` enforces a "Bucket Strategy" to validate the bridge between the Data Dictionary and Raw Data.
* **Reporting**: Unified `DS_type` inference; generates MD reports with "Critical Schema Mismatch" warnings and structured CSV matrices (stripped of orphans).
* **Performance**: Optimized CSV ingestion using C-engine with Python-engine fallback for delimiter sniffing.
* **Standardized CLI**: `classify-entities` and `clean-dataset --action [full|integrity|profile|assessment]` are the authoritative entry points.
* **Diagnostic Tools**: `check_integrity_bridge.py` established as a dataset-agnostic standalone tool for bridge validation.
* **Cleaning Assistant**: LOCKED heuristic framework producing segmented reports (`cleaning_recommendations.md`) and `provisional_config.yaml`.
* **Migration Handover**: The shell exports a synchronized data file representing the "Clean Bucket" for downstream migration processing.
---
*This stash ensures that the "Golden Rule" is maintained: any future updates must build upon the logic summarized here.*