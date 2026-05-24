## 📑 Test Infrastructure & Execution Guide

The test architecture for `dd-parser-cleaner` relies on a fully isolated, automated test harness driven by `pytest`. It is designed to act as a production-grade safety net, validating file transformations, case preservation, and path tracking constraints across the system endpoints.

---

## 🏗️ KMDS Test Workspace Simulation

To ensure complete test isolation, the test suite programmatically simulates a KMDS Framework Workspace within the `tests/` subdirectory.

* Directory Isolation: The test runner maintains a sandboxed layout mimicking your production architecture. It establishes required subdirectories like `tests/data_dictionary/` (for schemas) and `tests/data/` (for operational tables) so code modules never contaminate active production files.
* Authoritative Config Mapping: The system utilizes a root-level `tests/conftest.py` script. The `managed_test_config` fixture dynamically resolves and uses the single authoritative `config.yaml` at the project root, ensuring tests always reflect the latest production configuration. It also initializes standardized logging to ensure `INFO` level diagnostics appear in the terminal during test runs.

---

## 🚀 How to Run the Tests

The workspace utilizes the optimized `uv` Python package manager environment toolchain to lock dependencies and run execution sweeps.

## 1. Run the Complete Test Suite

To fire off all structural pipeline suites together, execute the following command from your project root workspace directory:

```bash
uv run pytest
```

## 2. Run Individual Component Test Tracks

If you are modifying a single module and want to run focused, isolated validation loops:

* Validate the Parser Track: Checks case preservation, dynamic LLM entity categorization, prefix-stripping, and signature sidecar generation:
  ```bash
  uv run pytest -s tests/test_parser.py
  ```
* Validate the Cleaner Track: Checks end-to-end operational table data scrubbing, vectorized title-casing, zero-padding, and column case lookup restorations:
  ```bash
  uv run pytest tests/test_cleaner.py
  ```

---

## 🎯 Wrap-Up Project State

All foundational pieces are successfully locked down:

* The Parser Core extracts metadata using dynamic prefix-stripping and local Llama 3.2 APIs.
* The Cleaner Engine scrubs structural tables without mutating intended case definitions.
* The Test Harness perfectly isolates environment context side-effects.

When you return to the active project session, let me know whether we should prioritize building the Interactive HITL terminal interface loop to edit model classifications or code the Synthetic Payload scaling test script!
