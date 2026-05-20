import argparse
import logging
import sys

def main():
    # 1. Initialize clean, standardized console log streaming
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    parser = argparse.ArgumentParser(
        description="Run the data cleaner pipeline driven by the verified dd-parser blueprint matrix map."
    )
    parser.add_argument("--working-dir", required=True, help="Path to raw data directories containing target payloads.")
    parser.add_argument("--config", required=True, help="Path to config.yaml file containing script targets.")
    args = parser.parse_args()

    # Import engine inside main to allow logging configs to bind cleanly first
    from dd_cleaner.engine import DataCleanerEngine

    try:
        # 2. Fire up the pipeline runner
        cleaner = DataCleanerEngine()
        cleaner.set_working_config(working_dir=args.working_dir, config_path=args.config)
        cleaner.clean_dataset()
        
    except Exception as e:
        logger = logging.getLogger("dd_cleaner_main")
        logger.error(f"🛑 Critical Pipeline Failure: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
