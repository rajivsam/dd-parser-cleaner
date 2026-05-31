"""
Test suite for the Metadata Parser.
Aligned with the 'classify-entities' CLI command.
"""

import pytest
from pathlib import Path
from dd_parser.orchestrator import PipelineOrchestrator
from dd_common.path_coordinator import PathCoordinator

def test_parser_orchestration_flow(managed_test_config):
    """Validates the end-to-end parser pipeline as executed by classify-entities."""
    # 1. Initialize Path Coordinator targeting the test workspace (Contract setup)
    coordinator = PathCoordinator(config_path=managed_test_config, working_dir="./tests")
    
    # 2. Inject Coordinator into the Orchestrator (Dependency Injection)
    orchestrator = PipelineOrchestrator(path_coordinator=coordinator)
    
    # 3. Process the full metadata pipeline
    orchestrator.process_pipeline()
    
    # 4. Verify physical artifact generation
    assert coordinator.data_dictionary_csv_path.exists(), "Parser failed to generate Data Dictionary CSV"
    assert coordinator.parser_provisional_report_path.exists(), "Parser failed to generate analysis reports"

def test_integrity_diagnostic_script_execution(managed_test_config):
    """Verifies the standalone diagnostic script runs correctly on the test workspace."""
    from .check_integrity_bridge import run_diagnostic
    # Execution should finish without errors
    run_diagnostic(workspace="./tests", config_file=managed_test_config)