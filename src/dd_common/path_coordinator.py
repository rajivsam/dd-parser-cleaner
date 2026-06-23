import os
import yaml
import logging
from pathlib import Path
from typing import Any, Optional, Union

class PathCoordinator:
    """
    Centralised path routing infrastructure contract.
    Ensures zero file paths are hardcoded across application and client boundaries.
    """
    def __init__(self, config_path: str = "config.yaml", working_dir: Optional[Union[str, Path]] = None):
        """
        Initializes the coordinator. 
        Anchors base_dir to config.yaml's working_dir for centralized pathing.
        """
        if working_dir is not None:
            self.base_dir = Path(working_dir).resolve()
        else:
            self.base_dir = Path(__file__).resolve().parent.parent.parent
            
        self.logger = logging.getLogger(__name__)
        self._config_name = config_path
        self._loaded_config = None

        # 🎯 CONFIG PIVOT: Set authoritative base_dir from config if specified
        config_val = self.config.get("working_dir")
        if config_val:
            self.base_dir = Path(config_val).resolve()

    @property
    def working_dir(self) -> Path:
        """Authoritative working directory (synonymous with base_dir after config pivot)."""
        return self.base_dir

    @property
    def config(self) -> dict:
        """Lazily loads and tracks context configurations across active boundaries."""
        if self._loaded_config is None:
            target_cfg = self.base_dir / self._config_name
            if not target_cfg.exists():
                msg = f"❌ Critical Configuration Error: Config file not found at {target_cfg}"
                self.logger.error(msg)
                raise FileNotFoundError(msg)
            with open(target_cfg, "r") as f:
                self._loaded_config = yaml.safe_load(f) or {}
        return self._loaded_config

    @property
    def _parser_config(self) -> dict:
        val = self.config.get("parser")
        if val is None:
            msg = "The 'parser' section is missing in config.yaml. Execution requires a fully specified config file. Please set the required section and try again."
            self.logger.error(msg)
            raise ValueError(msg)
        return val

    @property
    def _cleaner_config(self) -> dict:
        val = self.config.get("cleaner")
        if val is None:
            msg = "The 'cleaner' section is missing in config.yaml. Execution requires a fully specified config file. Please set the required section and try again."
            self.logger.error(msg)
            raise ValueError(msg)
        return val

    def _get_required_val(self, config_dict: dict, key: str, section_name: str) -> Any:
        """Helper to enforce required configuration keys and report specific missing variables."""
        val = config_dict.get(key)
        if val is None:
            msg = (f"Variable '{key}' is missing in the '{section_name}' section. "
                   f"Execution requires a fully specified config file and if this is not specified, "
                   f"execution cannot proceed. Please set the required variable and try again.")
            self.logger.error(msg)
            raise ValueError(msg)
        return val

    # --- SHARED GLOBAL DIR CONTRACTS ---
    @property
    def documents_dir(self) -> Path:
        """Base layout folder for Human-in-the-Loop context summaries."""
        dirname = self._get_required_val(self.config, "documents_dir", "global")
        return self.working_dir / dirname

    # --- PARSER MODULE ENDPOINTS ---
    @property
    def data_dictionary_attribute_col_name(self) -> str:
        """The target text string column header identifying primary attribute names."""
        return self._get_required_val(self._parser_config, "data_dictionary_attribute_col_name", "parser")

    @property
    def data_dictionary_path(self) -> Path:
        """INPUT: Resolves raw metadata configuration blueprints."""
        filename = self._get_required_val(self._parser_config, "data_dictionary_file", "parser")
        return self.working_dir / "data_dictionary" / filename

    @property
    def parser_output_directory(self) -> Path:
        """
        OUTPUT DIR: Target directory location for parser results (CSV/MD).
        Targets: {$working_dir}/{$documents_dir}/{$dd_parser_output_dir}
        """
        out_dir_name = self._get_required_val(self._parser_config, "dd_parser_output_dir", "parser")
        out_dir = Path(self.documents_dir) / out_dir_name
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    @property
    def data_dictionary_csv_path(self) -> Path:
        """
        OUTPUT FILE: Primary contract endpoint requested directly by core parser clients.
        Targets: {$working_dir}/{$documents_dir}/{$dd_parser_output_dir}/{$output_filename}
        """
        filename = self._get_required_val(self._parser_config, "output_filename", "parser")
        return self.parser_output_directory / filename

    # --- CLEANER MODULE ENDPOINTS ---
    @property
    def cleaner_narrative_directory(self) -> Path:
        """
        Authoritative 'Inbox' for cleaner narrative artifacts and handshake logic.
        Targets: {$working_dir}/{$documents_dir}/{$dd_cleaner_output_dir}
        """
        out_dir_name = self._get_required_val(self._cleaner_config, "dd_cleaner_output_dir", "cleaner")
        target_dir = Path(self.documents_dir) / out_dir_name
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir

    @property
    def raw_dataset_path(self) -> Path:
        """
        INPUT PATH: Resolves production operational tables strictly inside 
        the data directory layout workspace: {$working_dir}/data/{$raw_dataset_file}
        """
        filename = self._get_required_val(self._cleaner_config, "raw_dataset_file", "cleaner")
        return self.working_dir / "data" / filename

    @property
    def cleaner_output_directory(self) -> Path:
        """OUTPUT DIR: Target directory location for clean table metrics."""
        out_dir_name = self._get_required_val(self._cleaner_config, "dd_cleaner_output_dir", "cleaner")
        out_dir = self.working_dir / "data" / out_dir_name
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    @property
    def clean_dataset_output_path(self) -> Path:
        """OUTPUT FILE: Endpoint contract where cleaned table datasets are stored."""
        filename = self._get_required_val(self._cleaner_config, "clean_output_filename", "cleaner")
        return self.cleaner_output_directory / filename
    
    @property
    def user_cleaned_dataset_path(self) -> Path:
        """OUTPUT FILE: Endpoint where user-processed/augmented datasets are stored."""
        filename = self._get_required_val(self._cleaner_config, "user_cleaned_output_filename", "cleaner")
        return self.cleaner_output_directory / filename

    @property
    def synchronized_dictionary_path(self) -> Path:
        """
        Authoritative 'AI Baseline': The subsetted dictionary after Integrity Sync.
        Targets: {$cleaner_narrative_directory}/synchronized_dictionary.csv
        """
        return self.cleaner_narrative_directory / "synchronized_dictionary.csv"

    @property
    def metadata_table_path(self) -> Path:
        """
        Authoritative 'Expert Authority': The final metadata lookup for featurization.
        Targets: {$cleaner_output_directory}/{$metadata_table_filename}
        """
        filename = self._get_required_val(self._cleaner_config, "metadata_table_filename", "cleaner")
        return self.cleaner_output_directory / filename

    @property
    def profiling_report_path(self) -> Path:
        """
        Authoritative routing endpoint for the markdown data quality profiling report.
        Targets: {$cleaner_narrative_directory}/{$profiling_report_filename}
        """
        filename = self._get_required_val(self._cleaner_config, "profiling_report_filename", "cleaner")
        return self.cleaner_narrative_directory / filename

    @property
    def parser_provisional_report_path(self) -> Path:
        """
        Authoritative routing for the human-readable markdown assignment report.
        Redirected to the Cleaner's handshake 'Inbox' per the protocol.
        """
        return self.handshake_path

    @property
    def quarantine_path(self) -> Path:
        """
        Authoritative routing for isolated mixed-value records.
        Targets: {$base_dir}/data/{$quarantine_dir}/{$quarantine_filename}
        """
        dir_name = self._get_required_val(self._cleaner_config, "quarantine_dir", "cleaner")
        file_name = self._get_required_val(self._cleaner_config, "quarantine_filename", "cleaner")
        
        target_dir = self.working_dir / "data" / dir_name
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir / file_name

    @property
    def handshake_path(self) -> Path:
        """
        Authoritative routing for the parser-cleaner handshake narrative.
        Targets: {$cleaner_narrative_directory}/{$handshake_file}
        """
        filename = self._get_required_val(self._cleaner_config, "handshake_file", "cleaner")
        return self.cleaner_narrative_directory / filename