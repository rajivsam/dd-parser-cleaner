"""Orchestration engine for the dataset cleaning pipeline."""

import sys
import logging
import yaml
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console
from rich.prompt import Confirm
from path_coordinator import PathCoordinator

from .pipeline import PipelineRunner
from dd_parser.rules import IntegrityEngine
from dd_parser.structural_assessor import StructuralAssessor

class CleanerOrchestrator:
    """
    Manages the idempotent execution of data cleaning transformations.
    Implements the Phase 3 pipeline: Integrity -> Assessment -> etc.
    """

    def __init__(self, path_coordinator: PathCoordinator) -> None:
        self.logger = logging.getLogger(__name__)
        self.paths = path_coordinator
        self.config = self.paths.config
        self.cleaner_cfg = self.config.get("cleaner", {})
        
        self.structural_assessor = StructuralAssessor(self.config)
        self.console = Console()

    def run_pipeline(self, action: str = "full") -> None:
        """Executes the sequence of cleaning gates and transformations."""
        self.logger.info("🚀 Starting Cleaner Pipeline...")
        
        # 1. Ingest Data
        raw_path = Path(self.paths.raw_dataset_path)
        if not raw_path.exists():
            self.logger.error(f"Raw dataset missing at: {raw_path}")
            return

        # Standard read (sep=None handles CSV/TSV)
        df = pd.read_csv(raw_path, sep=None, engine='python')
        
        # 1.5 Integrity Sync (Bucket Strategy): Reconcile Dictionary vs Raw
        dd_path = Path(self.paths.data_dictionary_csv_path)
        if dd_path.exists():
            df_dict = pd.read_csv(dd_path)
            # Reconciled dictionary attributes live in 'attribute_name' per post-processor rules
            dd_attributes = df_dict["attribute_name"].dropna().tolist()
            bridge = IntegrityEngine.evaluate_bridge(dd_attributes, list(df.columns))
            self.logger.info(f"🌉 Bridge Evaluation: {len(bridge['operational'])} Operational, {len(bridge['orphans'])} Orphans")
        
        if action == "integrity":
            return

        # 🛡️ GATEKEEPER: Fetch current exclusions to filter recommendations
        col_filters = self.cleaner_cfg.get("column_filters", {})
        manual_drops = col_filters.get("drop_attributes", [])
        ignored = col_filters.get("ignore_recommendations", [])
        all_exclusions = list(set(manual_drops) | set(ignored))
        
        report = self.structural_assessor.assess(df, exclude_cols=all_exclusions)

        # 🛡️ GATEKEEPER: Auto-persist inferred dataset type to config.yaml (Non-blocking)
        sa_cfg = self.cleaner_cfg.setdefault("structural_assessment", {})
        current_type = sa_cfg.get("dataset_type")
        inferred_type = report.get("dataset_type") or "cross-sectional"

        # Update if explicitly requested or if the value is missing/sentinel
        if not current_type or "not_yet_inferred" in str(current_type).lower():
            tagged_type = f"{inferred_type} (inferred)"
            self.logger.info(f"🔍 Structural Analysis: Updating dataset_type to [bold cyan]{tagged_type}[/bold cyan]")
            
            # Update both the local reference and the authoritative config object
            sa_cfg["dataset_type"] = tagged_type
            self.config.setdefault("cleaner", {})["structural_assessment"] = sa_cfg

            self._persist_config()
            self.console.print(f"\n[bold yellow]🛠️  CONFIG UPDATED:[/bold yellow] Dataset type set to '[cyan]{tagged_type}[/cyan]'. Review in config.yaml.")

        self._run_structural_wizard(report)

        if action == "assessment":
            return

        self.logger.info("✅ Pre-flight checks complete. Handing off to Pipeline Runner...")
        
        # 3. Hand off to the idempotent PipelineRunner for transformations
        runner = PipelineRunner(self.paths)
        runner.run(action=action)

    def _run_structural_wizard(self, report: Dict[str, Any]) -> None:
        """Interactive terminal wizard to review structural recommendations."""
        self.console.print("\n[bold cyan]📋 Cleaner: Structural Assessment Report[/bold cyan]")
        self.console.print(f"Structural Hash: [yellow]{report['structural_hash']}[/yellow]")

        # 📝 MANUAL OVERRIDE VISIBILITY: Display existing config-driven drops
        col_filters = self.cleaner_cfg.get("column_filters", {})
        manual_drops = col_filters.get("drop_attributes", [])
        ignored = col_filters.get("ignore_recommendations", [])
        
        if manual_drops:
            self.console.print(f"\n[bold blue]📝 Manual Drops (from config):[/bold blue] {manual_drops}")
        if ignored:
            self.console.print(f"[bold blue]🙈 Ignored Recommendations:[/bold blue] {ignored}")
        
        if report["recommendations"]:
            self.console.print("\n[bold yellow]⚠️  New Recommendations Found (Unhandled):[/bold yellow]")
            for rec in report["recommendations"]:
                self.console.print(f" - {rec}")
            
            self.console.print("\n[bold yellow]🛠️  ACTION REQUIRED:[/bold yellow] Update [cyan]config.yaml[/cyan] to address these findings.")
            self.console.print(" - Add columns to [bold]cleaner.column_filters.drop_attributes[/bold] to remove them.")
            self.console.print(" - Add columns to [bold]cleaner.column_filters.ignore_recommendations[/bold] to acknowledge and keep them.")
            
            self.console.print("\n[bold red]Pipeline stopped for structural safety. Re-run after updating config.[/bold red]")
            sys.exit(0)
        else:
            self.console.print("\n[green]✅ No unhandled structural issues detected.[/green]")

    def _persist_config(self) -> None:
        """
        Writes the current state of self.config back to the active config.yaml file.
        Uses the authoritative path from the coordinator to prevent relative path drift.
        """
        # 🎯 ZERO-DEFAULT RESOLUTION: Resolve the authoritative config path strictly from the coordinator
        # Priority: explicit config_path -> internal _config_path -> local default
        config_path = getattr(self.paths, "config_path", 
                      getattr(self.paths, "_config_path", 
                      getattr(self.paths, "config_file", None)))
            
        if not config_path:
            self.logger.error("❌ PathCoordinator failed to provide an authoritative config path. Persistence aborted.")
            return

        target = Path(config_path).resolve()
        
        try:
            with open(target, 'w') as f:
                yaml.safe_dump(self.config, f, sort_keys=False)
            self.logger.info(f"💾 Configuration persisted to: {target.resolve()}")
        except Exception as e:
            self.logger.error(f"❌ Failed to persist configuration: {e}")

    def _execute_column_filtering(self, df: pd.DataFrame, drop_cols: List[str]) -> pd.DataFrame:
        """Physically removes attributes specified in the configuration."""
        if not drop_cols:
            return df
            
        # Capture count for visual confirmation
        target_drops = [c for c in drop_cols if c in df.columns]
        self.logger.info(f"✂️  Column Filter: Removing {len(target_drops)} attributes from the dataset.")

        if target_drops:
            df = df.drop(columns=target_drops)
        return df

    def update_config(self, config: Dict[str, Any]) -> None:
        """Refreshes sub-component settings."""
        self.structural_assessor.update_config(config)