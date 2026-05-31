"""Command Line Interface entry point for the dataset cleaning and profiling framework."""

import argparse
import logging
import sys
from pathlib import Path
from dd_parser.orchestrator import PipelineOrchestrator
from dd_common.path_coordinator import PathCoordinator


def main():
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True
    )
    logger = logging.getLogger("dd_parser_cli")

    parser = argparse.ArgumentParser(
        description="Unified Project State: LLM-Powered Data Dictionary Parser & Entity Classifier."
    )
    parser.add_argument(
        "--config", 
        default="config.yaml", 
        help="Path to the runtime parameter configuration file (default: config.yaml)"
    )
    
    args = parser.parse_args()

    try:
        logger.info("Initializing Path Coordinator and Parser Orchestration layers...")
        
        # 🎯 PATH RESOLUTION: Ensure config is resolved to absolute paths.
        # Workspace is now resolved via PathCoordinator from config.yaml.
        config_path = str(Path(args.config).resolve())

        # 🎯 CONSTRUCTOR DEPENDENCY INJECTION: Instantiate the authoritative routing contract
        coordinator = PathCoordinator(config_path=config_path)
        
        # 🎯 MODULAR ENTRY POINT: Inject the coordinator tracking boundary cleanly
        orchestrator = PipelineOrchestrator(path_coordinator=coordinator)
        
        logger.info("Starting metadata extraction and entity classification pipeline...")
        orchestrator.process_pipeline()
        
        logger.info("Parser pipeline successfully concluded. View results in documents/dd_analysis_results.")
        
    except Exception as e:
        logger.error(f"Fatal Parser Pipeline Execution Failure: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
