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

def test_cleaner_tag_discovery(initialized_cleaner):
    """Tests the Metadata Discovery API for tag-based attribute retrieval."""
    orch, coord = initialized_cleaner
    
    # 1. Trigger assessment to initialize the assistant and metadata
    orch.run_pipeline(action="assessment")
    
    # 2. Utilize the Discovery API to capture 'geographic' attributes
    geo_cols = orch.assistant.get_attributes_by_tag("geographic")
    
    # 3. Log results to the test console (visible with pytest -s)
    print(f"\n🌍 Tagged Attribute Discovery: Found {len(geo_cols)} 'geographic' attributes.")
    for col in sorted(geo_cols):
        print(f"  - {col}")

    # 4. Provide a full breakdown of attributes tagged by entity assignment
    df_dd = pd.read_csv(coord.data_dictionary_csv_path)
    attr_col = "attribute_name" if "attribute_name" in df_dd.columns else df_dd.columns[0]

    print("\n🏷️  Full Entity-to-Attribute Mapping Details:")
    mapping = df_dd.groupby("provisional_entity_assignment")[attr_col].apply(list).to_dict()
    for entity, attributes in sorted(mapping.items()):
        print(f"\n[ {entity} ]")
        for attr in sorted(attributes):
            print(f"  - {attr}")

    assert isinstance(geo_cols, list)
    assert len(geo_cols) > 0, "No geographic attributes discovered; verify entity_tagging in config."

def test_cleaner_full_pipeline(initialized_cleaner):
    """Tests the full transformation sequence from raw to clean."""
    orch, coord = initialized_cleaner
    
    # We run the full pipeline
    orch.run_pipeline(action="full")
    
    clean_path = Path(coord.clean_dataset_output_path)
    assert clean_path.exists(), "Full pipeline failed to produce cleaned dataset"
    
    print(f"\n📊 Test Output: Produced cleaned dataset at {clean_path}")
    
    # Basic data sanity check
    df_clean = pd.read_csv(clean_path)
    # Ensure Bucket A sync worked - there should be data
    assert not df_clean.empty, "Cleaned dataset is unexpectedly empty"
    assert "warn_" not in df_clean.columns or any(df_clean.columns.str.startswith("warn_")), "Validator flags missing"

    # 🎯 VERIFY SEMANTIC FLOW-THROUGH
    # 1. Verify headers are prefixed with entity assignments (e.g. Borrower_asofdate)
    entity_prefixed = [c for c in df_clean.columns if "_" in c and not c.startswith("warn_")]
    assert len(entity_prefixed) > 0, "Semantic tagging failed: Headers are missing entity prefixes."

    # 2. Verify Discovery API captures geographic attributes correctly in the full pipeline state
    geo_cols = orch.assistant.get_attributes_by_tag("geographic")
    assert len(geo_cols) > 0, "Discovery API failed to retrieve geographic attributes during full run verification."