"""Command Line Interface entry point for the dataset cleaning and profiling framework."""

import argparse
import logging
import sys
from dd_cleaner.pipeline import PipelineRunner
from path_coordinator import PathCoordinator


def main():
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True
    )
    logger = logging.getLogger("dd_cleaner_cli")

    parser = argparse.ArgumentParser(
        description="Unified Project State: Downstream Cleaner, Profiler, & Normalization CLI Engine."
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
    parser.add_argument(
        "--action",
        choices=["full", "integrity", "profile"],
        default="full",
        help="Specify an atomic cleaning action or 'full' for the entire pipeline (default: full)."
    )
    
    args = parser.parse_args()

    try:
        logger.info("Initializing Path Coordinator and Pipeline Runner...")
        # 🎯 CONSTRUCTOR DEPENDENCY INJECTION: Instantiate the authoritative routing contract
        coordinator = PathCoordinator(config_path=args.config, working_dir=args.workspace)
        
        # 🎯 MODULAR ENTRY POINT: Inject the coordinator tracking boundary cleanly
        runner = PipelineRunner(coordinator=coordinator)
        
        logger.info(f"Starting cleaner pipeline [Action: {args.action}]...")
        runner.run()
        
        logger.info("Cleaner pipeline successfully concluded. View cleaned data and markdown profiles in output targets.")
        
    except Exception as e:
        logger.error(f"Fatal Cleaner Pipeline Execution Failure: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
