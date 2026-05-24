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
        """Initializes the coordinator with explicit configuration and workspace paths."""
        # 🎯 FIX: Explicitly set base_dir to working_dir if provided, fallback to default parent resolution
        if working_dir is not None:
            self.base_dir = Path(working_dir).resolve()
        else:
            self.base_dir = Path(__file__).resolve().parent.parent
            
        self.logger = logging.getLogger(__name__)
        self._config_name = config_path
        self._loaded_config = None

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
    def documents_dir(self) -> str:
        """Base layout folder for Human-in-the-Loop context summaries."""
        dirname = self._get_required_val(self.config, "documents_dir", "global")
        return str(self.base_dir / dirname)

    # --- PARSER MODULE ENDPOINTS ---
    @property
    def data_dictionary_attribute_col_name(self) -> str:
        """The target text string column header identifying primary attribute names."""
        return self._get_required_val(self._parser_config, "data_dictionary_attribute_col_name", "parser")

    @property
    def data_dictionary_path(self) -> Path:
        """INPUT: Resolves raw metadata configuration blueprints."""
        filename = self._get_required_val(self._parser_config, "data_dictionary_file", "parser")
        return self.base_dir / "data_dictionary" / filename

    @property
    def parser_output_directory(self) -> Path:
        """
        OUTPUT DIR: Target directory location rooted strictly within the data_dictionary workspace layout.
        Targets: {$working_dir}/data_dictionary/{dd_parser_output_dir}
        """
        out_dir_name = self._get_required_val(self._parser_config, "dd_parser_output_dir", "parser")
        out_dir = self.base_dir / "documents" / out_dir_name
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    @property
    def data_dictionary_csv_path(self) -> str:
        """
        OUTPUT FILE: Primary contract endpoint requested directly by core parser clients.
        Targets: {$working_dir}/data_dictionary/{dd_parser_output_dir}/{$output_filename}
        """
        filename = self._get_required_val(self._parser_config, "output_filename", "parser")
        return str(self.parser_output_directory / filename)

    # --- CLEANER MODULE ENDPOINTS ---
    @property
    def raw_dataset_path(self) -> Path:
        """
        INPUT PATH: Resolves production operational tables strictly inside 
        the data directory layout workspace: {$working_dir}/data/{$raw_dataset_file}
        """
        filename = self._get_required_val(self._cleaner_config, "raw_dataset_file", "cleaner")
        return self.base_dir / "data" / filename

    @property
    def cleaner_output_directory(self) -> Path:
        """OUTPUT DIR: Target directory location for clean table metrics."""
        out_dir_name = self._get_required_val(self._cleaner_config, "dd_cleaner_output_dir", "cleaner")
        out_dir = self.base_dir / "data" / out_dir_name
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    @property
    def clean_dataset_output_path(self) -> str:
        """OUTPUT FILE: Endpoint contract where cleaned table datasets are stored."""
        filename = self._get_required_val(self._cleaner_config, "clean_output_filename", "cleaner")
        return str(self.cleaner_output_directory / filename)
    
    @property
    def profiling_report_path(self) -> Path:
        """
        Authoritative routing endpoint for the markdown data quality profiling report.
        Maps dynamically to: {$working_dir}/documents/{$dd_cleaner_output_dir}/{$profiling_report_filename}
        """
        output_dir = self._get_required_val(self._cleaner_config, "dd_cleaner_output_dir", "cleaner")
        filename = self._get_required_val(self._cleaner_config, "profiling_report_filename", "cleaner")
        
        # Consistent with standard cleaner output storage rules
        target_dir = Path(self.base_dir) / "documents" / output_dir
        return target_dir / filename

    @property
    def parser_provisional_report_path(self) -> Path:
        """
        Authoritative routing for the provisional entity assignment report.
        Targets: {$base_dir}/documents/{$parser_provisional_assingnment_dir}/{$parser_provisional_assingnment_filename}
        """
        dir_name = self._get_required_val(self._parser_config, "parser_provisional_assingnment_dir", "parser")
        file_name = self._get_required_val(self._parser_config, "parser_provisional_assingnment_filename", "parser")
        return Path(self.documents_dir) / dir_name / file_name
