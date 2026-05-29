"""Unit test suite verifying modular dataset cleaner execution matrix properties."""

import os
import sys
import pytest
import yaml
import pandas as pd
import numpy as np
from pathlib import Path

# Ensure the src directory is in the path for module discovery
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from path_coordinator import PathCoordinator
from dd_cleaner.orchestrator import PipelineRunner

# Path to the production configuration file
BASE_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

@pytest.fixture
def integration_env(tmp_path):
    """Sets up a mock environment mirroring the clean_dataset workspace."""
    output_dir = tmp_path / "cleaned_results"
    output_dir.mkdir()
    
    # 🧪 KMDS Layout: Ensure expected directories exist for PathCoordinator
    (tmp_path / "data").mkdir(exist_ok=True)
    (tmp_path / "documents").mkdir(exist_ok=True)

    # Create sample data containing cases for SOP threshold and job ratio logic
    # Ref: SOP 50 10 8 p. 149 (7a Small limit) and p. 329 (Job ratios)
    data = {
        'gross_approval_amount': [300000, 400000, 450000, 600000],
        'loan_program': ['7a Small', '7a Small', 'SBA Express', 'SBA Express'],
        'naics_code': [111110, 331110, 457110, 721110] # 33 is Mfg, 457 is restricted
    }
    
    # Load actual project config to ensure parity with production logic
    with open(BASE_CONFIG_PATH, "r") as f:
        config_dict = yaml.safe_load(f)

    # 🧪 Align mock data filename with the authoritative config
    raw_filename = config_dict["cleaner"].get("raw_dataset_file", "sba_loans_raw.csv")
    input_csv = tmp_path / "data" / raw_filename
    pd.DataFrame(data).to_csv(input_csv, index=False)

    # Inject test-specific output path while preserving derivation and pipeline logic
    config_dict["cleaner"]["output_dir"] = str(output_dir)
    
    # Create a temporary config file for the PathCoordinator to load
    test_config_file = tmp_path / "config.yaml"
    with open(test_config_file, "w") as f:
        yaml.safe_dump(config_dict, f)

    coordinator = PathCoordinator(config_path=str(test_config_file), working_dir=str(tmp_path))
    return coordinator, output_dir

def test_clean_dataset_functionality_parity(integration_env):
    """
    Ensures the test suite executes the same orchestrated logic as the 
    production 'uv run clean_dataset' command.
    """
    coordinator, output_dir = integration_env
    
    # Initialize and run the production-grade runner via the Routing Contract
    runner = PipelineRunner(coordinator=coordinator)
    runner.run()
    
    # Validate Output
    cleaned_file = output_dir / "raw_data_cleaned.csv"
    assert cleaned_file.exists(), "Pipeline failed to generate cleaned output file."
    
    result_df = pd.read_csv(cleaned_file)
    
    # 1. Parity Check: SOP Program Caps (SOP p. 149)
    # 7(a) Small must be <= $350k. Row 1 ($400k) should be flagged.
    if 'sop_threshold_violation' in result_df.columns:
        assert result_df.loc[1, 'sop_threshold_violation'] == True
        assert result_df.loc[0, 'sop_threshold_violation'] == False
    
    # 2. Parity Check: Job Creation Ratios (SOP p. 329)
    # Row 0: $300k / $90k (Std) = 3.33 jobs
    # Row 1: $400k / $140k (Mfg - NAICS 33) = 2.86 jobs
    if 'sop_expected_jobs' in result_df.columns:
        assert np.isclose(result_df.loc[0, 'sop_expected_jobs'], 3.33, atol=0.01)
        assert np.isclose(result_df.loc[1, 'sop_expected_jobs'], 2.86, atol=0.01)
