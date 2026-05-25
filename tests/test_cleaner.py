"""Unit test suite verifying modular dataset cleaner execution matrix properties."""

import os
import pytest
import yaml
import pandas as pd
from pathlib import Path
# 🧬 ALIGNED ROUTING FIX: Import the newly decoupled modular pipeline orchestrator
from dd_cleaner.pipeline import PipelineRunner
from path_coordinator import PathCoordinator


def test_cleaner_orchestration_workflow(managed_test_config):
    """Validates end-to-end cleaning engine orchestration logic matching the workspace config.

    Directs the PathCoordinator to process and clean target datasets within the designated 
    "./tests" working directory context according to architectural rules.
    """
    # 1. Instantiate the authoritative path coordinator targeted to the test directory context
    coordinator = PathCoordinator(config_path=managed_test_config, working_dir="./tests")
    
    # 2. Initialize decoupled system modules via Constructor Dependency Injection
    runner = PipelineRunner(coordinator=coordinator)
    
    print("\n🚀 Starting decoupled dataset cleaner orchestration workflow execution...")
    
    # --- PHASE 1: Verify & Load Parser Artifacts ---
    parsed_csv_path = Path(coordinator.data_dictionary_csv_path)
    
    # 3. COMPLIANCE CHECK: Look directly at the generated/reconciled output matrix file layout
    assert parsed_csv_path.exists(), f"❌ Prerequisite Missing: Cleaner requires parser output at {parsed_csv_path}"
    df_reconciled_metadata = pd.read_csv(parsed_csv_path)
    
    # Isolate parsed target attribute name column string safely matching post-processor conventions
    target_attr_col = "attribute_name" if "attribute_name" in df_reconciled_metadata.columns else df_reconciled_metadata.columns[0]
    
    raw_attributes = df_reconciled_metadata[target_attr_col].dropna().tolist()
    case_insensitive_lookup = {str(attr).lower().strip(): str(attr).strip() for attr in raw_attributes}
    
    # --- PHASE 2: Clean Operational Datasets ---
    print("🧼 Triggering downstream modular cleaning engine matrix scrub transformations...")
    runner.run()
    
    # ⚖️ INTEGRITY CHECK: Verify synchronized dictionary (Bucket Strategy output)
    sync_dict_path = coordinator.cleaner_output_directory / "synchronized_dictionary.csv"
    assert sync_dict_path.exists(), f"❌ Integrity Sync Failed: Synchronized dictionary missing at {sync_dict_path}"
    
    # 📊 PROFILING CHECK: Verify markdown report AND Grounded Inference JSON sidecar
    profile_md_path = Path(coordinator.profiling_report_path)
    profile_json_path = profile_md_path.with_suffix(".json")
    
    assert profile_md_path.exists(), f"❌ Orchestration contract breach: Profiling report missing at {profile_md_path}"
    assert profile_json_path.exists(), f"❌ Task 4.1 Breach: Grounded Inference JSON sidecar missing at {profile_json_path}"
    
    print(f"✅ Data profiling quality metric report successfully generated at: {profile_md_path}")

    # --- PHASE 3: Functional & Structural Compliance Handshake Verification ---
    print("🔍 Executing functional verification assertions...")
    df_sync_dict = pd.read_csv(sync_dict_path)
    
    # ⚖️ BUCKET A VALIDATION: Ensure synchronized dictionary contains only physical headers
    # 1. Load physical headers directly from the raw data source for the ground truth
    raw_data_path = coordinator.raw_dataset_path
    df_raw_headers = pd.read_csv(raw_data_path, nrows=0)
    physical_headers = set(df_raw_headers.columns)

    # 2. Check that every attribute in the operational matrix matches a physical column
    for attr in df_sync_dict[target_attr_col]:
        assert attr in physical_headers, (
            f"❌ Integrity Breach: Attribute '{attr}' in synchronized dictionary is an orphan. "
            "It does not exist in the physical raw data file headers."
        )
        
        # 3. Verify character-for-character casing alignment with the Data Dictionary
        attr_clean = str(attr).lower().strip()
        assert attr_clean in case_insensitive_lookup, (
            f"❌ Alignment Breach: Attribute '{attr}' was not found in the source Data Dictionary."
        )
                
    print("✅ Dataset cleaner orchestration contract fully validated.")
