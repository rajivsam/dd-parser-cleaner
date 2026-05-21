import os
import sys
import argparse
import logging
from dd_cleaner.engine import DatasetCleaner

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    logger = logging.getLogger("dd_cleaner_cli")

    parser = argparse.ArgumentParser(
        description="Case-Insensitive Transformation and Geographic Scrubbing CLI Engine."
    )
    parser.add_argument(
        "--workspace", 
        default=".", 
        help="Path to the active directory workspace (default: current directory)"
    )
    parser.add_argument(
        "--config", 
        default="config.yaml", 
        help="Path to the runtime parameter configuration file (default: config.yaml)"
    )
    
    args = parser.parse_args()

    try:
        cleaner = DatasetCleaner()
        cleaner.set_working_config(args.workspace, args.config)
        
        logger.info("Executing downstream Geographic Data Cleaner pipeline...")
        cleaner.process_cleaning_pipeline()
        logger.info("Scrubbing workflow completed successfully.")
        
    except Exception as e:
        logger.error(f"Fatal Cleaner Pipeline Execution Failure: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
