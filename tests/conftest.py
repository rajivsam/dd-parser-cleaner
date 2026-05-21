import os
import pytest
import yaml

@pytest.fixture(scope="session", autouse=True)
def managed_test_config():
    """
    Programmatically maintains a dedicated test configuration file.
    Ensures that all modules safely execute within the isolated ./tests workspace.
    """
    test_config_path = "tests/config.yaml"
    
    # Establish default runtime parameter mappings for the test workspace
    config_payload = {
        "batch_size": 10,
        "model_name": "llama3.2",
        "temperature": 0.0,
        "system_prompt": "You are a precise data engineering assistant. Respond strictly in JSON.",
        "csv_target_column_index": 0,
        "documents_dir": "documents",
        "dd_parser_output_dir": "dd_analysis_results",
        "output_filename": "sba_analysis_results.csv",
        "raw_dataset_file": "sba_loans_raw.csv",
        "dd_cleaner_output_dir": "dd_cleaner_results",
        "clean_output_filename": "sba_loans_clean.csv"
    }
    
    # Write isolated runtime properties safely to disk
    with open(test_config_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config_payload, f)
        
    yield test_config_path
    
    # Optional cleanup step: Retain for audit, or remove if a pristine state is required
    # if os.path.exists(test_config_path):
    #     os.remove(test_config_path)
