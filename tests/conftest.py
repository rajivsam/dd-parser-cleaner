import os
import pytest
import yaml

@pytest.fixture(scope="session", autouse=True)
def managed_test_config():
    """
    Programmatically maintains a dedicated test configuration file.
    Ensures that all modules safely execute within the isolated ./tests workspace,
    preserving the structured sub-blocks for parser and cleaner engines.
    """
    test_config_path = "tests/config.yaml"
    
    # Establish structured sub-block parameters to prevent component clobbering
    config_payload = {
        "batch_size": 10,
        "model_name": "llama3.2",
        "temperature": 0.0,
        "system_prompt": "You are a precise data engineering assistant. Respond strictly in JSON.",
        "documents_dir": "documents",
        
        # 🔎 Parser Test Sub-Schema Block
        "parser": {
            "data_dictionary_file": "sba_dd.csv",
            "csv_target_column_index": 0,
            "dd_parser_output_dir": "dd_analysis_results",
            "output_filename": "sba_analysis_results.csv",
            "entity_tagging": ["geographic"],
            "overrides": {
                "LocationID": {
                    "provisional_entity_assignment": "Lender",
                    "is_geographic": False
                }
            }
        },

        
        # 🧼 Cleaner Test Sub-Schema Block
        "cleaner": {
            "raw_dataset_file": "sba_loans_raw.csv",
            "clean_output_filename": "sba_loans_clean.csv",
            "dd_cleaner_output_dir": "dd_cleaner_results"
        }
    }
    
    # Write isolated runtime properties safely to disk
    os.makedirs(os.path.dirname(test_config_path), exist_ok=True)
    with open(test_config_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config_payload, f)
        
    yield test_config_path
    
    # Optional cleanup step: Retain for audit, or remove if a pristine state is required
    # if os.path.exists(test_config_path):
    #     os.remove(test_config_path)
