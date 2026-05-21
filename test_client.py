import os
import shutil
import pandas as pd
import yaml
from dd_parser.core import LocalEntityClassifier
from path_coordinator import PlatformPathResolver

def setup_mock_environment():
    """Initializes raw test files dynamically using the PlatformPathResolver."""
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    resolver = PlatformPathResolver(working_dir=".", config=config)
    
    # Clean old run residue using path resolver properties
    for path in [resolver.data_dictionary_dir, resolver.documents_dir, os.path.dirname(resolver.raw_data_input_path)]:
        if os.path.exists(path):
            shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)

    os.makedirs(os.path.dirname(resolver.raw_data_input_path), exist_ok=True)

    # Generate mock target keeping original casing structures perfectly intact
    df = pd.DataFrame(columns=["BorrCity", "BankStreet", "cdc_zip", "ThirdPartyLender_City"])
    df.to_csv(resolver.raw_data_input_path, index=False)
    print(f"📦 Environment Initialized via Resolver. Raw target stored at: {resolver.raw_data_input_path}")

def run_parser_test():
    setup_mock_environment()
    
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    resolver = PlatformPathResolver(working_dir=".", config=config)

    classifier = LocalEntityClassifier()
    classifier.set_working_config(working_dir=".", config_path="config.yaml")
    
    print("🚀 Triggering integration validation via LocalEntityClassifier...")
    classifier.process_pipeline()
    
    csv_out = resolver.data_dictionary_csv_path
    sig_out = f"{csv_out}.signature"
    md_out = os.path.join(resolver.documents_dir, "dd_parsing_summary.md")
    
    # Enforce platform layout checks
    assert os.path.exists(csv_out), f"❌ Failure: Metadata table missing at: {csv_out}"
    assert os.path.exists(sig_out), f"❌ Failure: Signature file missing at: {sig_out}"
    assert os.path.exists(md_out), f"❌ Failure: Markdown summary missing at: {md_out}"
    
    # Assert case preservation properties passed without alteration
    df_meta = pd.read_csv(csv_out)
    parsed_attrs = df_meta["attribute_name"].tolist()
    assert "BorrCity" in parsed_attrs, "❌ Failure: Case tracking altered PascalCase field names."
    assert "cdc_zip" in parsed_attrs, "❌ Failure: Case tracking altered snake_case field names."
    
    print("✅ Parser validation suite passed successfully via abstraction layer!")

if __name__ == "__main__":
    run_parser_test()
