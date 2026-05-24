"""Unit test suite verifying modular dataset cleaner execution matrix properties."""

import os
import pytest
import yaml
import pandas as pd
from pathlib import Path
# 🧬 ALIGNED ROUTING FIX: Import the newly decoupled modular pipeline orchestrator
from dd_cleaner.orchestrator import CleanerPipelineOrchestrator
from path_coordinator import PathCoordinator


def test_cleaner_orchestration_workflow(managed_test_config):
    """Validates end-to-end cleaning engine orchestration logic matching the workspace config.

    Directs the PathCoordinator to process and clean target datasets within the designated 
    "./tests" working directory context according to architectural rules.
    """
    # 1. Instantiate the authoritative path coordinator targeted to the test directory context
    coordinator = PathCoordinator(config_path=managed_test_config, working_dir="./tests")
    
    # 2. Initialize decoupled system modules via Constructor Dependency Injection
    cleaner = CleanerPipelineOrchestrator(path_coordinator=coordinator)
    
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
    cleaner.process_cleaning_pipeline()
    
    # Verify cleaning stage output file structures inside the sandbox
    cleaned_csv_path = Path(coordinator.clean_dataset_output_path)
    assert cleaned_csv_path.exists(), f"❌ Orchestration contract breach: Cleaner output missing at {cleaned_csv_path}"
    
        # Verify profiling stage output markdown layout structure inside the sandbox
    profile_md_path = Path(coordinator.profiling_report_path)
    assert profile_md_path.exists(), f"❌ Orchestration contract breach: Profiling report missing at {profile_md_path}"
    print(f"✅ Data profiling quality metric report successfully generated at: {profile_md_path}")

    # --- PHASE 3: Functional & Structural Compliance Handshake Verification ---
    print("🔍 Executing functional verification assertions...")
    df_clean_results = pd.read_csv(cleaned_csv_path)
    
    # Assert column case normalization matches the synchronized source dictionary parameters exactly
    for column_header in df_clean_results.columns:
        clean_header_token = str(column_header).lower().strip()
        if clean_header_token in case_insensitive_lookup:
            assert str(column_header) == case_insensitive_lookup[clean_header_token], (
                f"❌ Cleaner Data Defect: Casing mutated downstream for target header field '{column_header}' "
                f"(Expected reconciled format: '{case_insensitive_lookup[clean_header_token]}', Got: '{column_header}')"
            )
                
    print("✅ Dataset cleaner orchestration contract fully validated.")
