"""Pipeline orchestration engine for the metadata classification framework."""

import sys
import logging
import pandas as pd
from pathlib import Path
from typing import List
from rich.console import Console
from rich.prompt import Confirm
from path_coordinator import PathCoordinator

from .llm_client import LLMEntityClassifier
from .post_processor import MetadataPostProcessor
from .rules import IntegrityEngine
from .structural_assessor import StructuralAssessor


class PipelineOrchestrator:
    """Entry point architecture that choreographs the domain discovery workflow."""

    def __init__(self, path_coordinator: PathCoordinator) -> None:
        """Injects dependencies and hydrates framework configuration boundaries."""
        if path_coordinator is None:
            raise TypeError("PipelineOrchestrator requires a valid PathCoordinator instance.")
            
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self.paths = path_coordinator
        self.global_config = self.paths.config
        self.parser_config = self.global_config.get("parser", self.global_config)
        
        # 📊 DIAGNOSTIC: Evaluate configuration state immediately after hydration
        self.logger.info("=== CONFIGURATION TAG EVALUATION ===")
        raw_tags = self.parser_config.get("entity_tagging") or []
        self.logger.info(f"1. Raw 'entity_tagging' from YAML: {raw_tags}")
        explicit_targets = [str(t).strip().lower() for t in raw_tags if t]
        self.logger.info(f"2. Sanitized target concepts to tag: {explicit_targets}")
        overrides = self.parser_config.get("overrides") or {}
        self.logger.info(f"3. Active structural overrides found: {list(overrides.keys())}")
        self.logger.info("=====================================")

        # Inject modular specialized sub-components safely via relative module references
        self.llm_classifier = LLMEntityClassifier(self.global_config, self.parser_config)
        self.post_processor = MetadataPostProcessor(self.paths, self.parser_config)
        self.structural_assessor = StructuralAssessor(self.global_config)
        self.console = Console()

        # 🧠 DEPENDENCY CHECKPOINT: Validate background processing infrastructure availability
        self._verify_infrastructure_availability()

    def _verify_infrastructure_availability(self) -> None:
        """Verifies that the core inference model client infrastructure is reachable before execution."""
        if not hasattr(self.llm_classifier, "is_ready") or not self.llm_classifier.is_ready():
            self.logger.critical("❌ Background inference model (Ollama) is offline. Please start your local service engine instance and re-run this tool.")
            sys.exit(1)

    def set_working_config(self, working_dir: str, config_path: str) -> None:
        """Resets the internal environment boundaries with runtime parameters."""
        self.paths = self.paths.__class__(config_path=config_path, working_dir=working_dir)
        self.global_config = self.paths.config
        self.parser_config = self.global_config.get("parser", self.global_config)
        
        # Refresh configurations across downstream dependencies
        self.llm_classifier.update_config(self.global_config, self.parser_config)
        self.post_processor.update_config(self.paths, self.parser_config)
        self.structural_assessor.update_config(self.global_config)
        
        # Re-verify infrastructure capabilities following environmental layout adjustments
        self._verify_infrastructure_availability()

    def extract_inventory_attributes(self) -> List[str]:
        """Safely extracts native attribute strings from the configured source."""
        target_path = Path(self.paths.data_dictionary_path)
        if not target_path.exists():
            return []
            
        df_dict = pd.read_csv(target_path, sep=None, engine='python', skipinitialspace=True)
        attr_series, _ = self.post_processor.infer_schema_columns(df_dict)
        clean_series = attr_series.dropna().astype(str).str.strip()
        return clean_series[clean_series != ""].tolist()

    def process_pipeline(self) -> pd.DataFrame:
        """Executes LLM domain discovery and passes artifacts to post-processing."""
        target_path = Path(self.paths.data_dictionary_path)
        if not target_path.exists():
            raise FileNotFoundError(f"Data Dictionary blueprint missing at: {target_path}")
            
        df_dict = pd.read_csv(target_path, sep=None, engine='python', skipinitialspace=True)

        # 📊 GROUNDED INFERENCE: Synchronize schema and generate data profile
        grounding_profile = {}
        df_raw_sample = None
        raw_dataset_path = Path(self.paths.raw_dataset_path)
        if raw_dataset_path.exists():
            cleaner_cfg = self.global_config.get("cleaner", {})
            filters = cleaner_cfg.get("filters", {})
            manual_drops = filters.get("drop_attributes", [])
            ignored = filters.get("ignore_recommendations", [])
            all_exclusions = list(set(manual_drops) | set(ignored))

            self.logger.info(f"📊 Generating grounding profile from sample of: {raw_dataset_path.name}")
            # Read a 500-row sample and immediately filter out manual drops
            df_raw_sample = pd.read_csv(raw_dataset_path, sep=None, engine='python', nrows=500)
            df_raw_sample = self._execute_filtering(df_raw_sample, manual_drops)
            
            # Task 4.1: Request the LLM client to generate the metadata bundle
            grounding_profile = self.llm_classifier.generate_grounding_profile(df_raw_sample)

            # 📊 HEADER SYNCHRONIZATION: Align dictionary attributes with authoritative raw headers
            df_dict = self.post_processor.synchronize_with_raw_headers(df_dict, df_raw_sample)

            # 🛡️ INTEGRITY SYNC: Reconcile Dictionary vs Raw (Bucket Strategy)
            attr_series, _ = self.post_processor.infer_schema_columns(df_dict)
            bridge = IntegrityEngine.evaluate_bridge(attr_series.tolist(), list(df_raw_sample.columns))
            self.logger.info(f"🌉 Bridge Evaluation: {len(bridge['operational'])} Operational, {len(bridge['orphans'])} Orphans, {len(bridge['ghosts'])} Ghosts")

            # 📋 STRUCTURAL ASSESSMENT: Physical Integrity (Gate 1 & 2)
            assessment = self.structural_assessor.assess(df_raw_sample, exclude_cols=all_exclusions)
            self._run_structural_wizard(assessment)
            
            # Synchronize the dictionary to exclude manual drops before LLM classification
            if manual_drops:
                attr_series, _ = self.post_processor.infer_schema_columns(df_dict)
                attr_col_name = attr_series.name if attr_series.name in df_dict.columns else df_dict.columns[0]
                df_dict = df_dict[~df_dict[attr_col_name].isin(manual_drops)].reset_index(drop=True)

        # 🎯 ZERO-HARDCODING FIX: Extract the tag list strictly from your config space with empty list fallback
        raw_tags = self.parser_config.get("entity_tagging") or []
        explicit_targets = [str(t).strip().lower() for t in raw_tags if t]
        
        # Extract normalized, synchronized attributes and description values
        attr_series, desc_series = self.post_processor.infer_schema_columns(df_dict)
        
        # 🧠 PHASE 1 RUNTIME ENGAGEMENT: Bootstrap domain identification directly from data file arrays
        discovered_hints = self.llm_classifier.discover_macro_domain(
            attr_series.tolist(), desc_series.tolist()
        )

        # 🧠 PHASE 2 STREAMING EXECUTION: Pass dynamically extracted definitions down the pipe
        llm_assignments = self.llm_classifier.discover_entities(
            attr_series, desc_series, explicit_targets, 
            generated_hints=discovered_hints, grounding_profile=grounding_profile
        )
        
        # Component 3: Saves exact layout attributes without subsequent corruption
        parsed_matrix = self.post_processor.execute(
            df_dict, attr_series, desc_series, llm_assignments,
            grounding_profile=grounding_profile, df_raw_sample=df_raw_sample
        )
        return parsed_matrix

    def _run_structural_wizard(self, report: dict) -> None:
        """Interactive terminal wizard to review structural recommendations and safety hash."""
        self.console.print("\n[bold cyan]📋 Structural Assessment Report[/bold cyan]")
        self.console.print(f"Structural Hash: [yellow]{report['structural_hash']}[/yellow]")
        
        # 📝 MANUAL OVERRIDE VISIBILITY: Display existing config-driven drops
        cleaner_cfg = self.global_config.get("cleaner", {})
        filters = cleaner_cfg.get("filters", {})
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
            
            self.console.print("\n[bold yellow]🛠️  ACTION REQUIRED: Structural Safety Gate[/bold yellow]")
            self.console.print("The pipeline has detected structural issues that are not yet addressed in your configuration.")
            self.console.print("To ensure the LLM focuses only on relevant data, please update [cyan]config.yaml[/cyan]:")
            self.console.print(" 1. Add columns to [bold]cleaner.filters.drop_attributes[/bold] to remove them.")
            self.console.print(" 2. Add columns to [bold]cleaner.filters.ignore_recommendations[/bold] to keep them.")
            
            self.console.print("\n[bold red]Pipeline stopped. Please update your configuration and re-run.[/bold red]")
            sys.exit(0)
        else:
            self.console.print("\n[green]✅ No unhandled structural issues detected.[/green]")

    def _execute_filtering(self, df: pd.DataFrame, drop_cols: List[str]) -> pd.DataFrame:
        """Physically removes attributes specified in the configuration."""
        if not drop_cols:
            return df
        existing_drops = [c for c in drop_cols if c in df.columns]
        if existing_drops:
            df = df.drop(columns=existing_drops)
        return df
