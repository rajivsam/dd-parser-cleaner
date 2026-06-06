import pytest
import pandas as pd
from pathlib import Path
from dd_common.path_coordinator import PathCoordinator
from dd_cleaner.orchestrator import CleanerOrchestrator
from dd_cleaner.notebook_utils import get_metadata_table, save_metadata_table

def test_metadata_authority_lifecycle(managed_test_config):
    """
    Tests the sequence: Run Cleaner -> Load Baseline -> Expert Override -> Save Authority.
    """
    coord = PathCoordinator(config_path=managed_test_config)
    
    # 1. Setup: Ensure we have a clean slate for the authority file
    if coord.metadata_table_path.exists():
        coord.metadata_table_path.unlink()

    # 2. Execution: Run the cleaner to establish the 'Clean Bucket'
    # This generates 'synchronized_dictionary.csv' and the clean dataset.
    orch = CleanerOrchestrator(coord)
    orch.run_pipeline(action="full")
    
    assert coord.synchronized_dictionary_path.exists(), "Cleaner failed to produce synchronized baseline"

    # 3. Discovery: Notebook loads the metadata (bootstraps from Synchronized Dictionary)
    df_metadata = get_metadata_table(coord)
    assert not df_metadata.empty
    
    # 4. Action: Expert overrides a logical type
    # Standardized header used by parser/cleaner output
    attr_col = "attribute_name" if "attribute_name" in df_metadata.columns else coord.data_dictionary_attribute_col_name
    target_attr = df_metadata.iloc[0][attr_col]
    df_metadata.loc[df_metadata[attr_col] == target_attr, "logical_type"] = "expert_override"
    
    # 5. Persistence: Save the expert authority
    save_metadata_table(coord, df_metadata)
    assert coord.metadata_table_path.exists()

    # 6. Verification: Reload and ensure it is authoritative
    df_reloaded = get_metadata_table(coord)
    val = df_reloaded[df_reloaded[attr_col] == target_attr]["logical_type"].values[0]
    assert val == "expert_override"

def test_metadata_fails_if_cleaner_not_run(managed_test_config):
    """
    Ensures we cannot get or bootstrap metadata if the cleaner hasn't established a baseline.
    """
    coord = PathCoordinator(config_path=managed_test_config)
    
    # Manually remove artifacts to simulate 'pre-cleaner' state
    if coord.metadata_table_path.exists(): coord.metadata_table_path.unlink()
    if coord.synchronized_dictionary_path.exists(): coord.synchronized_dictionary_path.unlink()
    
    # Attempting to get metadata should now fail
    with pytest.raises(FileNotFoundError, match="Cleaner has not established a baseline"):
        get_metadata_table(coord)