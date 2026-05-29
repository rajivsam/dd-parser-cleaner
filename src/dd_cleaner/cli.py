"""Command Line Interface entry point for the dataset cleaning and profiling framework."""

import argparse
import logging
import sys
from pathlib import Path
from dd_cleaner.orchestrator import CleanerOrchestrator
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
        default="./tests", 
        help="Path to the active directory workspace (default: current directory)"
    )
    parser.add_argument(
        "--config", 
        default="config.yaml", 
        help="Path to the runtime parameter configuration file (default: config.yaml)"
    )
    parser.add_argument(
        "--action",
        choices=["discovery", "full", "integrity", "profile", "assessment", "column_filter", "row_filter", "impute", "derive"],
        default="full",
        help="Specify a pipeline stage to run or 'full' for the entire sequence (default: full)."
    )
    
    args = parser.parse_args()

    try:
        logger.info("Initializing Path Coordinator and Cleaner Orchestrator...")
        
        # 🎯 PATH RESOLUTION: Ensure workspace and config are resolved to absolute paths 
        # to prevent relative path drift and align with test execution patterns.
        workspace_root = str(Path(args.workspace).resolve())
        config_path = str(Path(args.config).resolve())

        # 🎯 CONSTRUCTOR DEPENDENCY INJECTION: Instantiate the authoritative routing contract
        coordinator = PathCoordinator(config_path=config_path, working_dir=workspace_root)
        
        # 🧪 AUTHORITATIVE BINDING: Ensure the coordinator explicitly tracks its config source
        coordinator.config_path = config_path

        # 🎯 MODULAR ENTRY POINT: Inject the coordinator tracking boundary cleanly
        orchestrator = CleanerOrchestrator(path_coordinator=coordinator)
        
        logger.info(f"Starting cleaner pipeline [Action: {args.action}]...")
        orchestrator.run_pipeline(action=args.action)
        
        logger.info("Cleaner pipeline successfully concluded. View cleaned data and markdown profiles in output targets.")
        
    except Exception as e:
        logger.error(f"Fatal Cleaner Pipeline Execution Failure: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
