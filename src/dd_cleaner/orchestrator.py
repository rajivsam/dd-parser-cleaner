"""Orchestration engine for the dataset cleaning pipeline."""

import sys
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console
from rich.prompt import Confirm
from path_coordinator import PathCoordinator

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
        
        # 🛡️ GATEKEEPER: Check if dataset_type is still present in config as a requirement.
        # Since we are dropping the feature, we assume the user just wants to filter.
        dataset_type = self.cleaner_cfg.get("structural_assessment", {}).get("dataset_type", "not_yet_inferred")
        if dataset_type == "not_yet_inferred":
             self.logger.debug("Dataset type not specified; proceeding with heuristic filtering only.")

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

        # 2. Structural Assessment (Gate 1 & 2)
        pk_list = self.cleaner_cfg.get("structural_assessment", {}).get("primary_keys", [])
        
        # 🛡️ GATEKEEPER: Fetch current exclusions to filter recommendations
        filters = self.cleaner_cfg.get("filters", {})
        manual_drops = filters.get("drop_attributes", [])
        ignored = filters.get("ignore_recommendations", [])
        all_exclusions = list(set(manual_drops) | set(ignored))
        
        report = self.structural_assessor.assess(df, exclude_cols=all_exclusions)
        
        self._run_structural_wizard(report)

        if action == "assessment":
            return

        # 3. Filtering Stage: Physically drop attributes marked in config.yaml
        df = self._execute_filtering(df, manual_drops)
        
        if action == "filter":
            return

        self.logger.info("✅ Cleaner Pre-flight checks complete.")

    def _run_structural_wizard(self, report: Dict[str, Any]) -> None:
        """Interactive terminal wizard to review structural recommendations."""
        self.console.print("\n[bold cyan]📋 Cleaner: Structural Assessment Report[/bold cyan]")
        self.console.print(f"Structural Hash: [yellow]{report['structural_hash']}[/yellow]")

        # 📝 MANUAL OVERRIDE VISIBILITY: Display existing config-driven drops
        filters = self.cleaner_cfg.get("filters", {})
        manual_drops = filters.get("drop_attributes", [])
        ignored = filters.get("ignore_recommendations", [])
        
        if manual_drops:
            self.console.print(f"\n[bold blue]📝 Manual Drops (from config):[/bold blue] {manual_drops}")
        if ignored:
            self.console.print(f"[bold blue]🙈 Ignored Recommendations:[/bold blue] {ignored}")
        
        if report["recommendations"]:
            self.console.print("\n[bold yellow]⚠️  New Recommendations Found (Unhandled):[/bold yellow]")
            for rec in report["recommendations"]:
                self.console.print(f" - {rec}")
            
            self.console.print("\n[bold yellow]🛠️  ACTION REQUIRED:[/bold yellow] Update [cyan]config.yaml[/cyan] to address these findings.")
            self.console.print(" - Add columns to [bold]cleaner.filters.drop_attributes[/bold] to remove them.")
            self.console.print(" - Add columns to [bold]cleaner.filters.ignore_recommendations[/bold] to acknowledge and keep them.")
            
            self.console.print("\n[bold red]Pipeline stopped for structural safety. Re-run after updating config.[/bold red]")
            sys.exit(0)
        else:
            self.console.print("\n[green]✅ No unhandled structural issues detected.[/green]")

    def _execute_filtering(self, df: pd.DataFrame, drop_cols: List[str]) -> pd.DataFrame:
        """Physically removes attributes specified in the configuration."""
        if not drop_cols:
            return df
            
        existing_drops = [c for c in drop_cols if c in df.columns]
        if existing_drops:
            self.logger.info(f"✂️  Filtering: Dropping {len(existing_drops)} attributes defined in config...")
            df = df.drop(columns=existing_drops)
        return df

    def update_config(self, config: Dict[str, Any]) -> None:
        """Refreshes sub-component settings."""
        self.structural_assessor.update_config(config)