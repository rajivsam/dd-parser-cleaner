"""Integration test to verify the interactive Structural Assessment Wizard."""

import pytest
from path_coordinator import PathCoordinator
from dd_cleaner.orchestrator import CleanerOrchestrator

def test_structural_assessment_interaction(managed_test_config):
    """
    Triggers the interactive structural assessment wizard using the test workspace.
    
    Run this with the -s flag to allow terminal input/output:
    uv run pytest -s tests/test_structural_assessment.py
    """
    # 1. Initialize coordinator targeting the 'tests' sandbox workspace
    # This ensures it finds data in tests/data/ and writing to tests/dd_cleaner_results/
    coordinator = PathCoordinator(config_path=managed_test_config, working_dir="./tests")
    
    # 2. Initialize the Orchestrator (which contains the wizard logic)
    orchestrator = CleanerOrchestrator(path_coordinator=coordinator)
    
    # 3. Execute the pipeline (pre-flight checks trigger the wizard)
    with pytest.raises(SystemExit):
        orchestrator.run_pipeline()