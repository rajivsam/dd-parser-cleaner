import os
from dd_parser import LocalEntityClassifier

def run_local_test():
    # Folder containing your dictionary files
    target_data_dir = "/home/rajiv/programming/kmds_descriptive_analytics/kmds_sba_loans/data_dictionary"

    # Path to the config file sitting in your current workspace
    config_name = "config.yaml" 
    
    print("=== Starting dd_parser Integration Test ===")
    
    try:
        classifier = LocalEntityClassifier()
        
        # FIXED: Pass config_path as the second keyword argument matching our refactored core engine
        classifier.set_working_config(working_dir=target_data_dir, config_path=config_name)
        
        print("\n🚀 Dispatched extraction and Ollama micro-batching pipelines...")
        classifier.process()
        print("\n=== Test Finished Successfully ===")
        
    except Exception as e:
        print(f"\n❌ Pipeline execution failed with exception: {e}")

if __name__ == "__main__":
    run_local_test()
