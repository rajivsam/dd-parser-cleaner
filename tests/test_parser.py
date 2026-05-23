"""Unit test suite verifying modular parsing matrix layout processing rules."""

import os
import pandas as pd
import pytest
from pathlib import Path
from dd_parser.orchestrator import PipelineOrchestrator
from path_coordinator import PathCoordinator


def test_parser_pipeline_execution(managed_test_config):
    """Validates end-to-end entity mapping logic matching the central workspace config.

    Directs the PathCoordinator to evaluate the pre-provisioned data files within 
    the designated "./tests" working directory context.
    """
    # 1. Instantiate the authoritative path coordinator targeted to the test directory context
    coordinator = PathCoordinator(config_path=managed_test_config, working_dir="./tests")
    
    # 2. Inject the coordinator into the operational orchestration engine
    classifier = PipelineOrchestrator(path_coordinator=coordinator)
    
    print(f"\n🚀 Executing pipeline orchestration within sandbox boundary: ./tests")
    classifier.process_pipeline()
    
    # 3. Verify that the output file was successfully written or updated inside the test directory
    csv_out = Path(coordinator.data_dictionary_csv_path)
    assert csv_out.exists(), f"❌ Expected pipeline output matrix missing at: {csv_out.resolve()}"
    
    print(f"✅ Verified updated sandbox output file generated at: {csv_out}")
    print(f"🕒 Output File Last Modified Timestamp: {os.path.getmtime(csv_out)}")
    
    # 4. Enforce schema compliance on the generated metadata output matrix
    df_meta = pd.read_csv(csv_out)
    
    # Extract the configured concepts directly from the orchestrator setup
    raw_tags = classifier.parser_config.get("entity_tagging") or []
    explicit_targets = [str(t).strip().lower() for t in raw_tags if t]
    
    # Ensure every single configured tag maps directly to an active boolean flag column
    for target in explicit_targets:
        expected_col = f"is_{target}"
        assert expected_col in df_meta.columns, f"❌ Target concept column '{expected_col}' failed to bind to dataframe."
