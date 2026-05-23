"""Command Line Interface entry point for the metadata parser framework."""

import argparse
import logging
import sys
from dd_parser.orchestrator import PipelineOrchestrator
from path_coordinator import PathCoordinator


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
        logger.info("Initializing Path Coordinator and Orchestration layers...")
        # 🎯 FIX: Explicitly instantiate the routing orchestration contract using CLI arguments
        coordinator = PathCoordinator(config_path=args.config, working_dir=args.workspace)
        
        # 🎯 FIX: Inject the coordinator instance into the required modular entry point
        orchestrator = PipelineOrchestrator(path_coordinator=coordinator)
        
        logger.info("Executing Data Dictionary Parser pipeline inference sequence...")
        orchestrator.process_pipeline()
        logger.info("Parser pipeline successfully concluded. View logs in output tracking dir.")
        
    except Exception as e:
        logger.error(f"Fatal Parser Pipeline Execution Failure: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
