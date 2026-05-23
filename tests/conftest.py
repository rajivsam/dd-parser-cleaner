import os
from pathlib import Path
import pytest
import yaml

@pytest.fixture(scope="session", autouse=True)
def managed_test_config():
    """
    Dynamically maps to the single authoritative config.yaml at the VSCode workspace root.
    Eliminates duplicated config payloads across production and testing states.
    """
    # Look for config.yaml relative to this file's position (walking up to workspace root)
    root_config = Path(__file__).parent.parent / "config.yaml"
    
    if not root_config.exists():
        raise FileNotFoundError(
            f"❌ Base configuration missing at workspace root: {root_config.resolve()}\n"
            f"Please ensure config.yaml exists at your project root boundary."
        )
        
    # Return the resolved string path to the single authoritative configuration file
    return str(root_config.resolve())
