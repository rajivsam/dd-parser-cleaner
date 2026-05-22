import os
import yaml
from pathlib import Path

class PathCoordinator:
    """
    Centralised path routing infrastructure contract.
    Ensures zero file paths are hardcoded across application and client boundaries.
    """
    def __init__(self, config_path: str = "config.yaml"):
        self.base_dir = Path(__file__).resolve().parent.parent
        self._config_name = config_path
        self._loaded_config = None

    @property
    def config(self) -> dict:
        """Lazily loads and tracks context configurations across active boundaries."""
        if self._loaded_config is None:
            target_cfg = self.base_dir / self._config_name
            if not target_cfg.exists():
                return {}
            with open(target_cfg, "r") as f:
                self._loaded_config = yaml.safe_load(f) or {}
        return self._loaded_config

    @property
    def _parser_config(self) -> dict:
        return self.config.get("parser", self.config)

    @property
    def _cleaner_config(self) -> dict:
        return self.config.get("cleaner", self.config)

    # --- SHARED GLOBAL DIR CONTRACTS ---
    @property
    def documents_dir(self) -> str:
        """Base layout folder for Human-in-the-Loop context summaries."""
        dirname = self.config.get("documents_dir", "documents")
        return str(self.base_dir / dirname)

    # --- PARSER MODULE ENDPOINTS ---
    @property
    def data_dictionary_path(self) -> Path:
        """INPUT: Resolves raw metadata configuration blueprints."""
        filename = self._parser_config.get("data_dictionary_file", "sba_dd.csv")
        return self.base_dir / "data_dictionary" / filename

    @property
    def parser_output_directory(self) -> Path:
        """
        OUTPUT DIR: Target directory location rooted strictly within the data_dictionary workspace layout.
        Targets: {$working_dir}/data_dictionary/{dd_parser_output_dir}
        """
        out_dir_name = self._parser_config.get("dd_parser_output_dir", "dd_analysis_results")
        # 🧼 FIX: Append the parser results folder directly inside the data_dictionary subdirectory
        out_dir = self.base_dir / "data_dictionary" / out_dir_name
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    @property
    def data_dictionary_csv_path(self) -> str:
        """
        OUTPUT FILE: Primary contract endpoint requested directly by core parser clients.
        Targets: {$working_dir}/data_dictionary/{dd_parser_output_dir}/{$output_filename}
        """
        filename = self._parser_config.get("output_filename", "sba_analysis_results.csv")
        return str(self.parser_output_directory / filename)

    # --- CLEANER MODULE ENDPOINTS ---
    @property
    def raw_dataset_path(self) -> Path:
        """
        INPUT PATH: Resolves production operational tables strictly inside 
        the data directory layout workspace: {$working_dir}/data/{$raw_dataset_file}
        """
        filename = self._cleaner_config.get("raw_dataset_file", "sba_loans_raw.csv")
        return self.base_dir / "data" / filename

    @property
    def cleaner_output_directory(self) -> Path:
        """OUTPUT DIR: Target directory location for clean table metrics."""
        out_dir_name = self._cleaner_config.get("dd_cleaner_output_dir", "dd_cleaner_results")
        out_dir = self.base_dir / out_dir_name
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    @property
    def clean_dataset_output_path(self) -> str:
        """OUTPUT FILE: Endpoint contract where cleaned table datasets are stored."""
        filename = self._cleaner_config.get("clean_output_filename", "sba_loans_clean.csv")
        return str(self.cleaner_output_directory / filename)


# Clean interface mapping for platform components
PlatformPathResolver = PathCoordinator
