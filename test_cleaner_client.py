import os
import shutil
import pandas as pd
import yaml
from dd_cleaner.engine import DatasetCleaner
from path_coordinator import PlatformPathResolver

def setup_cleaner_mock_environment():
    """Initializes metadata, signatures, and raw dataset fields via the resolver."""
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    resolver = PlatformPathResolver(working_dir=".", config=config)
    
    # Clean out target directory layouts
    for path in [resolver.data_dictionary_dir, resolver.data_cleaner_dir, resolver.documents_dir, os.path.dirname(resolver.raw_data_input_path)]:
        if os.path.exists(path):
            shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)

    os.makedirs(os.path.dirname(resolver.raw_data_input_path), exist_ok=True)

    # 1. Store case-preserved mock data dictionary results inside configured path
    dd_data = {
        "attribute_name": ["BorrCity", "cdc_zip", "ThirdPartyLender_City"],
        "is_geographical": [True, True, True]
    }
    pd.DataFrame(dd_data).to_csv(resolver.data_dictionary_csv_path, index=False)
    
    # 2. Write the independent verification signature file tracking line
    with open(f"{resolver.data_dictionary_csv_path}.signature", "w") as f:
        f.write("# DD-PARSER-SIGNATURE: PROCESSED-BY-LLAMA3.2\n")
        
    # 3. Write messy geographic strings to the data workspace directory
    dirty_payload = {
        "BorrCity": ["SAN JOSE", "boston"],
        "cdc_zip": ["95112.0", "2108"],
        "ThirdPartyLender_City": ["LOS ANGELES", "chicago"]
    }
    pd.DataFrame(dirty_payload).to_csv(resolver.raw_data_input_path, index=False)
    print(f"🧹 Cleaner Environment Initialized via Resolver. Messy inputs stored at: {resolver.raw_data_input_path}")

def run_cleaner_test():
    setup_cleaner_mock_environment()
    
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    resolver = PlatformPathResolver(working_dir=".", config=config)
    clean_filename = config.get("clean_output_filename", "sba_loans_clean.csv")

    cleaner = DatasetCleaner()
    cleaner.set_working_config(working_dir=".", config_path="config.yaml")
    
    print("🚀 Triggering integration verification via DatasetCleaner...")
    cleaner.process_cleaning_pipeline()
    
    expected_clean_csv = os.path.join(resolver.data_cleaner_dir, clean_filename)
    expected_report_md = os.path.join(resolver.documents_dir, "data_cleaning_summary.md")
    
    # Enforce platform layout checks
    assert os.path.exists(expected_clean_csv), f"❌ Failure: Clean dataset missing at: {expected_clean_csv}"
    assert os.path.exists(expected_report_md), f"❌ Failure: Summary markdown missing at: {expected_report_md}"
    
    # FIX: Force pandas to load zip codes as string objects to preserve the leading zero
    df_clean = pd.read_csv(expected_clean_csv, dtype={"cdc_zip": str})
    
    # Evaluate explicit data scrubbing constraints
    assert df_clean.loc[0, "BorrCity"] == "San Jose", "❌ Failure: City string Title Case transformation failed."
    assert df_clean.loc[1, "cdc_zip"] == "02108", "❌ Failure: Zero-padding constraints failed."
    assert df_clean.loc[1, "ThirdPartyLender_City"] == "Chicago", "❌ Failure: Complex prefix scrubbing failed."
    
    print("✅ Cleaner validation suite passed successfully via abstraction layer!")

if __name__ == "__main__":
    run_cleaner_test()
