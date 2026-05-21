import os
import sys
import argparse
import logging
from dd_parser.core import LocalEntityClassifier

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    logger = logging.getLogger("dd_parser_cli")

    parser = argparse.ArgumentParser(
        description="Unified Project State: Private LLM Data Dictionary Parser CLI Engine."
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
        classifier = LocalEntityClassifier()
        classifier.set_working_config(args.workspace, args.config)
        
        logger.info("Executing Data Dictionary Parser pipeline inference sequence...")
        classifier.process_pipeline()
        logger.info("Parser pipeline successfully concluded. View logs in output tracking dir.")
        
    except Exception as e:
        logger.error(f"Fatal Parser Pipeline Execution Failure: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
