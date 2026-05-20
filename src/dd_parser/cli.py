import argparse
import logging

def main():
    # Setup initial clean console output streaming
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    parser = argparse.ArgumentParser(description="Run the private local LLM Data Dictionary Parser.")
    parser.add_argument("--working-dir", required=True, help="Path to raw source files.")
    parser.add_argument("--config", required=True, help="Path to config.yaml file.")
    args = parser.parse_args()

    # Import inside main to let logging configure cleanly first
    from dd_parser.core import LocalEntityClassifier

    classifier = LocalEntityClassifier()
    classifier.set_working_config(working_dir=args.working_dir, config_path=args.config)
    classifier.process()

if __name__ == "__main__":
    main()
