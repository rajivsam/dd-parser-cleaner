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
    # 🎯 DECOUPLED INITIALIZATION: Resolves workspace root from configuration metadata
    coord = PathCoordinator(config_path=managed_test_config)
    # Note: Ensure classify-entities (Parser) has run to satisfy the Handshake requirement
    return CleanerOrchestrator(coord), coord

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
    prov_config = coord.cleaner_narrative_directory / "provisional_config.yaml"
    
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
    try:
        df_dd = pd.read_csv(coord.data_dictionary_csv_path, engine='c', low_memory=False)
    except Exception:
        df_dd = pd.read_csv(coord.data_dictionary_csv_path, sep=None, engine='python')

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
    
    rec_path = coord.cleaner_narrative_directory / "cleaning_recommendations.md"
    report_path = coord.profiling_report_path
    
    assert rec_path.exists(), "Full pipeline failed to generate recommendations"
    assert report_path.exists(), "Full pipeline failed to generate profiling report"
    assert coord.clean_dataset_output_path.exists(), "Full pipeline failed to produce synchronized data file"