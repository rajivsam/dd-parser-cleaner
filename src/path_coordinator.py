import os
from typing import Dict, Any

class PlatformPathResolver:
    """
    Encapsulates structural pipeline layout constants.
    Guarantees runtime modules and test clients conform to the same directory rules.
    """
    def __init__(self, working_dir: str, config: Dict[str, Any]):
        self.working_dir = os.path.abspath(working_dir)
        self.config = config

    @property
    def raw_data_input_path(self) -> str:
        """Enforces that raw data files live strictly inside the data/ folder."""
        filename = self.config.get("raw_dataset_file", "sba_loans_raw.csv")
        return os.path.join(self.working_dir, "data", filename)

    @property
    def data_dictionary_dir(self) -> str:
        """Resolves target data dictionary folder destinations."""
        raw_dir = self.config.get("dd_parser_output_dir", "dd_analysis_results")
        target_dir = os.path.join(self.working_dir, "data_dictionary", raw_dir)
        os.makedirs(target_dir, exist_ok=True)
        return target_dir

    @property
    def data_dictionary_csv_path(self) -> str:
        """Resolves the absolute path to the data dictionary CSV output file."""
        filename = self.config.get("output_filename", "sba_analysis_results.csv")
        return os.path.join(self.data_dictionary_dir, filename)

    @property
    def data_cleaner_dir(self) -> str:
        """Resolves target data cleaner folder destinations inside data/."""
        raw_dir = self.config.get("dd_cleaner_output_dir", "dd_cleaner_results")
        target_dir = os.path.join(self.working_dir, "data", raw_dir)
        os.makedirs(target_dir, exist_ok=True)
        return target_dir

    @property
    def documents_dir(self) -> str:
        """Forces analytical markdown deliverables straight into documents/."""
        raw_dir = self.config.get("documents_dir", "documents")
        target_dir = os.path.join(self.working_dir, raw_dir)
        os.makedirs(target_dir, exist_ok=True)
        return target_dir
