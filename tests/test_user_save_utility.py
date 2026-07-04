import pytest
import pandas as pd
from pathlib import Path
from dd_common.path_coordinator import PathCoordinator
from dd_cleaner.notebook_utils import save_user_cleaned_data, init_notebook_session

def test_user_cleaned_data_flow(managed_test_config):
    """
    Verifies the save utility persists data to the configured path.
    """
    coord = PathCoordinator(config_path=managed_test_config)
    
    # Cleanup
    if coord.user_cleaned_dataset_path.exists():
        coord.user_cleaned_dataset_path.unlink()

    # 1. Create a simple dummy DataFrame (the "user work")
    user_df = pd.DataFrame({"test_col": [1, 2, 3], "data": ["a", "b", "c"]})

    # 2. Call the save API
    save_user_cleaned_data(coord, user_df)
    
    # 3. Verify file exists and name matches config
    assert coord.user_cleaned_dataset_path.exists()
    assert coord.user_cleaned_dataset_path.name == "sba_loans_raw_user_cleaned.csv"

    # 4. Verify discovery
    _, artifacts = init_notebook_session(str(coord.working_dir), config_path=managed_test_config)
    exists = artifacts[artifacts["Artifact Name"] == "User Cleaned Data"]["Exists"].iloc[0]
    assert exists == True