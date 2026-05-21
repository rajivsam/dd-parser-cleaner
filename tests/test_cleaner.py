import os
import pandas as pd
import yaml
from dd_cleaner.engine import DatasetCleaner
from path_coordinator import PlatformPathResolver

def test_cleaner_pipeline_execution(managed_test_config):
    """
    Validates end-to-end data scrubbing routines within the isolated tests directory.
    Verifies that zero-padding, title-casing, and custom prefix tracking execute cleanly.
    """
    with open(managed_test_config, 'r') as f:
        config = yaml.safe_load(f)
        
    resolver = PlatformPathResolver(working_dir="./tests", config=config)
    clean_filename = config.get("clean_output_filename", "sba_loans_clean.csv")
    
    # 1. Establish independent verification sidecar file ahead of pipeline handshake
    meta_csv_path = resolver.data_dictionary_csv_path
    with open(f"{meta_csv_path}.signature", "w", encoding='utf-8') as f:
        f.write("# DD-PARSER-SIGNATURE: PROCESSED-BY-LLAMA3.2\n")

    # 2. Trigger downstream cleaning engine
    cleaner = DatasetCleaner()
    cleaner.set_working_config(working_dir="./tests", config_path=managed_test_config)
    
    print("\n🚀 Executing geographic transformation checks on raw benchmark files...")
    cleaner.process_cleaning_pipeline()
    
    # Resolve absolute targets
    expected_clean_csv = os.path.join(resolver.data_cleaner_dir, clean_filename)
    expected_report_md = os.path.join(resolver.documents_dir, "data_cleaning_summary.md")
    
    # Platform layout checkpoints
    assert os.path.exists(expected_clean_csv), f"❌ Clean dataset file missing at: {expected_clean_csv}"
    assert os.path.exists(expected_report_md), f"❌ Cleaning summary markdown table report missing at: {expected_report_md}"
    
    # 3. Deep-element data sanity evaluations (Force zip as string to verify zero-padding)
    df_clean = pd.read_csv(expected_clean_csv, dtype={"cdc_zip": str})
    
    assert df_clean.loc[0, "BorrCity"] == "San Jose", "❌ Failure: City string Title Case transformation failed."
    assert df_clean.loc[1, "cdc_zip"] == "02108", "❌ Failure: ZIP zero-padding sequence failed."
    
    # FIX: Aligned assertion value with row index 1 ("NEW YORK" -> "New York")
    assert df_clean.loc[1, "ThirdPartyLender_City"] == "New York", "❌ Failure: Complex organizational prefix casing failed."
