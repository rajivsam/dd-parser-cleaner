import os
import pytest
import pandas as pd
from pathlib import Path
from dd_parser.core import LocalEntityClassifier
from dd_cleaner.engine import DatasetCleaner
from path_coordinator import PathCoordinator

def test_client_orchestration_workflow(managed_test_config):
    """
    Validates end-to-end client integration workflow using the mandatory 
    centralized PathCoordinator instance contract interface.
    """
    # 🎯 STEP 1: Instantiate the single authoritative path coordinator tracking boundary
    coordinator = PathCoordinator(config_path=managed_test_config, working_dir="./tests")
    
    # 🎯 STEP 2: Initialize components via explicit constructor dependency injection
    classifier = LocalEntityClassifier(path_coordinator=coordinator)
    cleaner = DatasetCleaner(path_coordinator=coordinator)
    
    print("\n🚀 Starting client end-to-end orchestration workflow execution...")
    
    # --- PHASE 1: Parse Data Dictionary Payload ---
    print("📋 Triggering local Llama metadata parser matrix generation...")
    classifier.process_pipeline()
    
    # Verify parsing stage output file structures
    parsed_csv_path = Path(coordinator.data_dictionary_csv_path)
    sidecar_sig_path = parsed_csv_path.with_suffix(".signature")
    
    assert parsed_csv_path.exists(), f"❌ Client contract breach: Parser output missing at {parsed_csv_path}"
    assert sidecar_sig_path.exists(), f"❌ Client contract breach: Cryptographic signature asset missing at {sidecar_sig_path}"
    
    # Extract structural casing dictionary maps directly from pipeline context
    raw_attributes = classifier.extract_inventory_attributes()
    case_insensitive_lookup = {attr.lower().strip(): attr.strip() for attr in raw_attributes}
    
    # --- PHASE 2: Clean Operational Datasets ---
    print("🧼 Triggering downstream cleaning engine matrix scrub transformations...")
    cleaner.process_cleaning_pipeline()
    
    # Verify cleaning stage output file structures
    cleaned_csv_path = Path(coordinator.clean_dataset_output_path)
    assert cleaned_csv_path.exists(), f"❌ Client contract breach: Cleaner output missing at {cleaned_csv_path}"
    
    # --- PHASE 3: Functional & Structural Compliance Handshake Verification ---
    print("🔍 Executing functional verification assertions...")
    df_clean_results = pd.read_csv(cleaned_csv_path)
    
    # Assert column case normalization matches the source dictionary parameters
    for column_header in df_clean_results.columns:
        clean_header_token = str(column_header).lower().strip()
        if clean_header_token in case_insensitive_lookup:
            assert str(column_header) == case_insensitive_lookup[clean_header_token], \
                f"❌ Client Data Defect: Casing mutated downstream for target header field '{column_header}'"
                
    print("✅ Client orchestration contract fully validated.")
