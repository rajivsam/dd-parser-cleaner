import os
import sys
import logging
from pathlib import Path
import pytest
import yaml

# Ensure local src packages are importable during pytest collection and execution.
_repo_root = Path(__file__).resolve().parent.parent
_src_path = _repo_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

@pytest.fixture(scope="session", autouse=True)
def managed_test_config():
    """
    Dynamically maps to the single authoritative config.yaml at the VSCode workspace root.
    Eliminates duplicated config payloads across production and testing states.
    GOLDEN RULE: This points to the REAL file. No mocking or sandboxing.
    """
    # 🛠️ LOGGING INITIALIZATION: Ensure logs appear during test runs
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True
    )
    
    # Prefer the test workspace configuration when available.
    test_workspace_config = Path(__file__).parent / "config.yaml"
    if test_workspace_config.exists():
        return str(test_workspace_config.resolve())

    # Fallback to the repository root configuration if no test workspace config is present.
    root_config = Path(__file__).parent.parent / "config.yaml"
    if not root_config.exists():
        raise FileNotFoundError(
            f"❌ Base configuration missing at workspace root: {root_config.resolve()}\n"
            f"Please ensure config.yaml exists at your project root boundary."
        )

    # Return the resolved string path to the single authoritative configuration file
    return str(root_config.resolve())
