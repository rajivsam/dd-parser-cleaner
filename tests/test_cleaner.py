"""
Test suite for the Dataset Cleaner.
Aligned with the 'clean-dataset' CLI command and its various actions.
"""

import pytest
from pathlib import Path
import pandas as pd
from dd_cleaner.orchestrator import CleanerOrchestrator
from dd_common.path_coordinator import PathCoordinator

@pytest.fixture
def initialized_cleaner(managed_test_config):
    """Provides an orchestrator instance ready for testing."""
    coord = PathCoordinator(config_path=managed_test_config, working_dir="./tests")
    # Note: Ensure classify-entities (Parser) has run to satisfy the Handshake requirement
    return CleanerOrchestrator(coord), coord

def test_cleaner_discovery(initialized_cleaner):
    """Tests Phase 0: Domain Discovery (Policy Manifest generation)."""
    orch, coord = initialized_cleaner
    orch.run_pipeline(action="discovery")
    
    manifest_path = coord.cleaner_narrative_directory / "policy_manifest.json"
    assert manifest_path.exists(), "Discovery failed to generate policy_manifest.json"

def test_cleaner_profile(initialized_cleaner):
    """Tests the independent data quality profiling action."""
    orch, coord = initialized_cleaner
    orch.run_pipeline(action="profile")
    
    report_path = Path(coord.profiling_report_path)
    json_sidecar = report_path.with_suffix(".json")
    
    assert report_path.exists(), "Null profile markdown report missing"
    assert json_sidecar.exists(), "Null profile JSON sidecar missing"

def test_cleaner_assessment(initialized_cleaner):
    """Tests the Cleaning Assistant's recommendation and provisional report generation."""
    orch, coord = initialized_cleaner
    orch.run_pipeline(action="assessment")
    
    rec_path = coord.cleaner_narrative_directory / "cleaning_recommendations.md"
    prov_config = coord.cleaner_output_directory / "provisional_config.yaml"
    
    assert rec_path.exists(), "Cleaning recommendations report not found"
    assert prov_config.exists(), "Provisional config for HITL review not found"

def test_cleaner_full_pipeline(initialized_cleaner):
    """Tests the full transformation sequence from raw to clean."""
    orch, coord = initialized_cleaner
    
    # We run the full pipeline
    orch.run_pipeline(action="full")
    
    clean_path = Path(coord.clean_dataset_output_path)
    assert clean_path.exists(), "Full pipeline failed to produce cleaned dataset"
    
    # Basic data sanity check
    df_clean = pd.read_csv(clean_path)
    # Ensure Bucket A sync worked - there should be data
    assert not df_clean.empty, "Cleaned dataset is unexpectedly empty"
    assert "warn_" not in df_clean.columns or any(df_clean.columns.str.startswith("warn_")), "Validator flags missing"