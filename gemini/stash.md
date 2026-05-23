# 📌 Unified Contract & State Tracking Blueprint (Stash)

## 🛠️ Active Project State

* **Workspace:** `dd-parser-cleaner`
* **Architecture:** Modular system decoupled into `orchestrator.py`, `llm_client.py`, and `post_processor.py` with strict Constructor Dependency Injection via `PathCoordinator`.
* **State Checkpoint:** Successfully aligned the testing architecture to reference a single authoritative configuration file located at the VSCode workspace root. Resolved terminal blind spots by ensuring both `test_parser.py` and `test_cleaner.py` run in context-isolated `./tests` directory loops, completely eliminating duplicate/hardcoded configuration objects within the test workspace.

---

## ⚙️ Authoritative Contract Specifications

### 1. Unified Test Configuration Hook (`tests/conftest.py`)

Maintains zero-redundancy configuration management by directly serving the workspace root configuration path into the test matrix execution scope.

```python
"""Centralized test configuration layout managing shared fixtures."""

import os
from pathlib import Path
import pytest

@pytest.fixture(scope="session", autouse=True)
def managed_test_config():
    """
    Dynamically maps to the single authoritative config.yaml at the VSCode workspace root.
    Eliminates duplicated config payloads across production and testing states.
    """
    root_config = Path(__file__).parent.parent / "config.yaml"
  
    if not root_config.exists():
        raise FileNotFoundError(
            f"❌ Base configuration missing at workspace root: {root_config.resolve()}\n"
            f"Please ensure config.yaml exists at your project root boundary."
        )
      
    return str(root_config.resolve())
```

---

## 🧩 Modular System Snapshots (Testing Space)

### 🧬 Aligned Test Parser (`tests/test_parser.py`)

```python
"""Unit test suite verifying modular parsing matrix layout processing rules."""

import os
import pandas as pd
import pytest
from pathlib import Path
from dd_parser.orchestrator import PipelineOrchestrator
from path_coordinator import PathCoordinator

def test_parser_pipeline_execution(managed_test_config):
    """Validates end-to-end entity mapping logic matching the central workspace config."""
    coordinator = PathCoordinator(config_path=managed_test_config, working_dir="./tests")
    classifier = PipelineOrchestrator(path_coordinator=coordinator)
  
    print(f"\n🚀 Executing pipeline orchestration within sandbox boundary: ./tests")
    classifier.process_pipeline()
  
    csv_out = Path(coordinator.data_dictionary_csv_path)
    assert csv_out.exists(), f"❌ Expected pipeline output matrix missing at: {csv_out.resolve()}"
  
    df_meta = pd.read_csv(csv_out)
    assert "attribute_name" in df_meta.columns, "❌ Target field 'attribute_name' missing."
  
    raw_tags = classifier.parser_config.get("entity_tagging") or []
    explicit_targets = [str(t).strip().lower() for t in raw_tags if t]
  
    for target in explicit_targets:
        expected_col = f"is_{target}"
        assert expected_col in df_meta.columns, f"❌ Target concept column '{expected_col}' failed to bind."
```

### 🧼 Reconciled Test Cleaner (`tests/test_cleaner.py`)

```python
"""Unit test suite verifying modular dataset cleaner execution matrix properties."""

import os
import pytest
import pandas as pd
from pathlib import Path
from dd_parser.orchestrator import PipelineOrchestrator
from dd_cleaner.engine import DatasetCleaner
from path_coordinator import PathCoordinator

def test_cleaner_orchestration_workflow(managed_test_config):
    """Validates end-to-end cleaning engine orchestration logic matching the workspace config."""
    coordinator = PathCoordinator(config_path=managed_test_config, working_dir="./tests")
    classifier = PipelineOrchestrator(path_coordinator=coordinator)
    cleaner = DatasetCleaner(path_coordinator=coordinator)
  
    print("\n🚀 Starting dataset cleaner orchestration workflow execution...")
    classifier.process_pipeline()
  
    parsed_csv_path = Path(coordinator.data_dictionary_csv_path)
    assert parsed_csv_path.exists(), f"❌ Orchestration contract breach: Parser output missing."
  
    df_reconciled_metadata = pd.read_csv(parsed_csv_path)
    target_attr_col = "attribute_name" if "attribute_name" in df_reconciled_metadata.columns else df_reconciled_metadata.columns[0]
  
    raw_attributes = df_reconciled_metadata[target_attr_col].dropna().tolist()
    case_insensitive_lookup = {str(attr).lower().strip(): str(attr).strip() for attr in raw_attributes}
  
    cleaner.process_cleaning_pipeline()
    cleaned_csv_path = Path(coordinator.clean_dataset_output_path)
    assert cleaned_csv_path.exists(), f"❌ Orchestration contract breach: Cleaner output missing."
  
    df_clean_results = pd.read_csv(cleaned_csv_path)
    for column_header in df_clean_results.columns:
        clean_header_token = str(column_header).lower().strip()
        if clean_header_token in case_insensitive_lookup:
            assert str(column_header) == case_insensitive_lookup[clean_header_token], (
                f"❌ Cleaner Data Defect: Casing mutated downstream for target header field '{column_header}'"
            )
    print("✅ Dataset cleaner orchestration contract fully validated.")
```

---

## 🎯 Resumption Backlog (Next Steps)

1. **Rebuild Clobbered Cleaner Features:** Inspect `dd_cleaner/engine.py` to identify which parts of the casing/cleaning logic got clobbered, and refactor them to use the authoritative, synchronized outputs from `PipelineOrchestrator`.
2. **Verify Boolean Tag Propagation:** Ensure that `MetadataPostProcessor` inside the orchestrator is writing `True`/`False` flags into `is_geographic` based on configurations and overrides, matching the assertions now live in the test runner.
3. **CLI Interface Hook (`cli.py`):** Begin implementation of the human-in-the-loop low-confidence heuristic tagging terminal interface.
