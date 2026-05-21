import os
import pandas as pd
import yaml
from dd_parser.core import LocalEntityClassifier
from path_coordinator import PlatformPathResolver

def test_parser_pipeline_execution(managed_test_config):
    """
    Validates end-to-end entity mapping logic within the isolated tests directory.
    Asserts case preservation and signature tracking separation.
    """
    # Initialize engine targeting our custom execution parameters
    classifier = LocalEntityClassifier()
    classifier.set_working_config(working_dir="./tests", config_path=managed_test_config)
    
    print("\n🚀 Executing entity classification sweeps on benchmark assets...")
    classifier.process_pipeline()
    
    # Instantiate coordinator to resolve accurate target path properties
    with open(managed_test_config, 'r') as f:
        config = yaml.safe_load(f)
    resolver = PlatformPathResolver(working_dir="./tests", config=config)
    
    csv_out = resolver.data_dictionary_csv_path
    sig_out = f"{csv_out}.signature"
    md_out = os.path.join(resolver.documents_dir, "dd_parsing_summary.md")
    
    # Platform compliance checks
    assert os.path.exists(csv_out), f"❌ Metadata matrix missing at: {csv_out}"
    assert os.path.exists(sig_out), f"❌ Sidecar control signature asset missing at: {sig_out}"
    assert os.path.exists(md_out), f"❌ Report analytics summary layout missing at: {md_out}"
    
    # Structural integrity: pandas must parse it smoothly without header contamination
    df_meta = pd.read_csv(csv_out)
    assert "attribute_name" in df_meta.columns, "❌ Structural crash: Tabular data framing misaligned."
    
    # Assert case tracking matches input file specs
    parsed_attrs = df_meta["attribute_name"].tolist()
    assert "BorrCity" in parsed_attrs, "❌ Failure: Case tracking contaminated PascalCase naming parameters."
    assert "cdc_zip" in parsed_attrs, "❌ Failure: Case tracking contaminated snake_case naming parameters."
