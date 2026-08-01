## 📑 Test Infrastructure & Execution Guide

The test architecture for `dd-parser-cleaner` relies on a fully isolated, automated test harness driven by `pytest`. It is designed to act as a production-grade safety net, validating file transformations, case preservation, and path tracking constraints across the system endpoints.

---

## 🏗️ KMDS Test Workspace Simulation

To ensure complete test isolation, the test suite programmatically simulates a KMDS Framework Workspace within the `tests/` subdirectory.

* Directory Isolation: The test runner maintains a sandboxed layout mimicking your production architecture. It establishes required subdirectories like `tests/data_dictionary/` (for schemas) and `tests/data/` (for operational tables) so code modules never contaminate active production files.
* Authoritative Config Mapping: The system utilizes a root-level `tests/conftest.py` script. The `managed_test_config` fixture dynamically resolves and uses the single authoritative `config.yaml` at the project root, ensuring tests always reflect the latest production configuration. It also initializes standardized logging to ensure `INFO` level diagnostics appear in the terminal during test runs.

---

## 🚀 How to Run the Tests

The workspace uses `pytest` for validation with all test files under `tests/`.

## 1. Run the Complete Test Suite

From the project root, execute:

```bash
uv run pytest
```

## 2. Run Individual Test Files

If you are modifying a specific workflow or module, run the relevant test file directly:

* `tests/test_bootstrap_config.py` — config generation and bootstrap metadata behavior.
* `tests/test_sba_end_to_end.py` — SBA end-to-end parser and cleaner workflow.
* `tests/test_mn_traffic_end_to_end.py` — MN traffic end-to-end workflow.
* `tests/test_itsm_end_to_end.py` — ITSM panel workflow with questionnaire behavior.
* `tests/test_wide_short_end_to_end.py` — wide-short homogeneous dataset workflow.
* `tests/test_metadata_authority.py` — metadata authority lifecycle and cleaner baseline enforcement.
* `tests/test_normalization.py` — normalization utilities and value canonicalization.
* `tests/test_package_info.py` — package metadata and CLI discovery.
* `tests/test_post_processor.py` — parser post-processing and manifest emission behavior.
* `tests/test_user_save_utility.py` — post-cleaning user save utilities.
* `tests/test_workspace_init.py` — workspace initialization and directory provisioning.

---

## 🛠️ Diagnostic Tools

### Notebook Examples
The project includes example notebooks in `tests/notebooks/` that show how to use the notebook utilities and metadata APIs.

- `tests/notebooks/imperative_migration_example.ipynb`
- `tests/notebooks/verify_notebook_utils.ipynb`
- `tests/notebooks/metadata_bootstrap_example.ipynb`

### Integrity Bridge Check
To debug mismatches between your Data Dictionary and Raw Data headers without running a full pipeline pass, use the standalone diagnostic tool. This tool is dataset-agnostic and resolves paths dynamically via the `PathCoordinator`.

```bash
uv run python tests/check_integrity_bridge.py --workspace . --config config.yaml
```

**Output Summary:**
- **Operational Fields**: Attributes successfully mapped between both sources.
- **Orphans**: Fields defined in the dictionary but missing from the raw data.
- **Ghosts**: Headers found in the raw data with no corresponding dictionary definition.

---

## 🎯 Wrap-Up Project State

All foundational pieces are successfully locked down:

* The Parser Core extracts metadata using dynamic prefix-stripping and local Llama 3.2 APIs.
* The Cleaner Engine scrubs structural tables without mutating intended case definitions.
* The Test Harness perfectly isolates environment context side-effects.

When you return to the active project session, let me know whether we should prioritize building the Interactive HITL terminal interface loop to edit model classifications or code the Synthetic Payload scaling test script!
