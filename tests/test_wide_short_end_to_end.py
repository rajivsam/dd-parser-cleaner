import json
import sys
from pathlib import Path
from shutil import copyfile

import pandas as pd
import yaml
from dd_common.utilities import prepare_workspace
from dd_common import dataset_bootstrap_cli, bootstrap_cli
from dd_common.path_coordinator import PathCoordinator
from dd_parser.orchestrator import PipelineOrchestrator
from dd_cleaner.orchestrator import CleanerOrchestrator


class DummyBootstrapConsole:
    def __init__(self, answers=None):
        self.answers = iter(answers or [])

    def input(self, prompt: str = "") -> str:
        try:
            return next(self.answers)
        except StopIteration:
            return ""

    def print(self, *args, **kwargs):
        return None


class DummyBootstrapConfigConsole:
    def input(self, prompt: str = "") -> str:
        return "Field Name"

    def print(self, *args, **kwargs):
        return None


def _dummy_llm_call(self, prompt: str, timeout: float = 10.0) -> str:
    if "logical_entities" in prompt:
        return json.dumps({"logical_entities": ["Product", "Revenue", "Time"]})
    return json.dumps({"entity_assignment": "unassigned", "static_dynamic": "static"})


def test_wide_short_dataset_end_to_end(tmp_path, monkeypatch):
    """End-to-end workflow for the wide-short Olist dataset."""
    workspace_dir = tmp_path
    prepare_workspace(str(workspace_dir))

    repo_root = Path(__file__).resolve().parent.parent
    source_raw = repo_root / "tests" / "data" / "SP_2017_weekly_product_revenue_by_product_id.csv"
    source_dd = repo_root / "tests" / "data_dictionary" / "olist_example_dd.csv"

    target_raw = workspace_dir / "data" / source_raw.name
    target_dd = workspace_dir / "data_dictionary" / source_dd.name
    copyfile(source_raw, target_raw)
    copyfile(source_dd, target_dd)

    monkeypatch.setattr(sys, "argv", [
        "dataset-bootstrap",
        str(workspace_dir),
        "--graph-mode", "graph",
        "--graph-homogeneous",
        "--dataset-type", "cross-sectional",
        "--subject", "week of the year",
        "--wide-short-homogeneous",
        "--wide-short-representative-column", "woy",
        "--use-case", "Forecast weekly revenue for products",
        "--analysis-objective", "Improve revenue planning"
    ])
    dataset_bootstrap_cli.main()

    metadata_path = workspace_dir / "bootstrap_metadata.yaml"
    assert metadata_path.exists(), "dataset-bootstrap did not write bootstrap_metadata.yaml"
    metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    assert metadata["dataset_type"] == "graph_homogeneous"
    assert metadata["subject"] == "week of the year"
    assert metadata["use_case_answers"]["use_case"] == "Forecast weekly revenue for products"

    monkeypatch.setattr(bootstrap_cli, "console", DummyBootstrapConfigConsole())
    monkeypatch.setattr(sys, "argv", ["bootstrap-config", "--output", "config.yaml", str(workspace_dir)])
    bootstrap_cli.main()

    config_path = workspace_dir / "config.yaml"
    assert config_path.exists(), "bootstrap-config did not generate config.yaml"
    config_payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert config_payload["dataset_type"] == "graph_homogeneous"
    assert config_payload["parser"]["data_dictionary_file"] == "olist_example_dd.csv"
    assert config_payload["parser"]["wide_short_homogeneous"] is True
    assert config_payload["parser"]["wide_short_representative_column"] == "woy"
    assert config_payload["cleaner"]["raw_dataset_file"] == "SP_2017_weekly_product_revenue_by_product_id.csv"

    monkeypatch.setattr("dd_parser.orchestrator.LLMEntityClassifier.is_ready", lambda self: True)
    monkeypatch.setattr("dd_parser.llm_client.LLMEntityClassifier._call_llm", _dummy_llm_call)

    coordinator = PathCoordinator(config_path=str(config_path))
    parser_orchestrator = PipelineOrchestrator(path_coordinator=coordinator)
    parser_orchestrator.process_pipeline()

    assert coordinator.data_dictionary_csv_path.exists(), "Parser did not generate data_dictionary_csv_path"
    assert coordinator.dataset_manifest_path.exists(), "Parser did not generate dataset manifest"
    assert coordinator.attribute_manifest_path.exists(), "Parser did not generate attribute manifest"
    assert coordinator.handshake_path.exists(), "Parser did not generate handshake file"

    cleaner_coord = PathCoordinator(config_path=str(config_path))
    cleaner = CleanerOrchestrator(path_coordinator=cleaner_coord)
    cleaner.run_pipeline(action="full")

    assert cleaner_coord.profiling_report_path.exists(), "Cleaner did not generate profiling report"
    assert cleaner_coord.clean_dataset_output_path.exists(), "Cleaner did not generate clean dataset output"
    assert cleaner_coord.synchronized_dictionary_path.exists(), "Cleaner did not generate synchronized dictionary"
    assert (cleaner_coord.cleaner_narrative_directory / "cleaning_recommendations.md").exists(), "Cleaner did not generate recommendations report"


def test_wide_short_seed_selection_limits_to_first_and_representative_column(tmp_path, monkeypatch):
    """Verify wide-short datasets only seed the first and representative columns for parser classification."""
    from dd_parser.orchestrator import PipelineOrchestrator

    config_path = tmp_path / "config.yaml"
    config = {
        "working_dir": str(tmp_path),
        "documents_dir": "documents",
        "dataset_type": "cross-sectional",
        "dataset_id": "wide_short_test",
        "parser": {
            "data_dictionary_file": "sample_dd.csv",
            "data_dictionary_attribute_col_name": "attribute",
            "wide_short_homogeneous": True,
            "wide_short_representative_column": "rep_col",
            "entity_tagging": [],
        },
        "cleaner": {
            "raw_dataset_file": "sample.csv",
            "clean_output_filename": "sample_clean.csv",
            "metadata_table_filename": "sample_metadata_table.csv",
            "user_cleaned_output_filename": "sample_user_cleaned.csv",
            "dd_cleaner_output_dir": "dd_cleaner",
            "handshake_file": "sample_parser_cleaner_handshake.md",
            "profiling_report_filename": "sample_profiling_report.md",
            "quarantine_dir": "quarantine",
            "quarantine_filename": "sample_quarantine.csv",
            "structural_assessment": {
                "dataset_type": "cross-sectional",
                "subject_id_attribute": None,
                "null_threshold": 0.95,
            },
        },
    }
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    for folder in ["data", "data_dictionary", "documents", "notebooks", "models"]:
        (tmp_path / folder).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr("dd_parser.orchestrator.LLMEntityClassifier.is_ready", lambda self: True)
    coordinator = PathCoordinator(config_path=str(config_path))
    orchestrator = PipelineOrchestrator(path_coordinator=coordinator)

    attr_series = pd.Series(["first_col", "rep_col", "other_1", "other_2"])
    desc_series = pd.Series(["First column", "Representative measure", "Other measure 1", "Other measure 2"])

    seed_attrs, seed_descs = orchestrator._select_wide_short_seed_attributes(attr_series, desc_series)

    assert len(seed_attrs) == 2
    assert seed_attrs.iloc[0] == "first_col"
    assert seed_attrs.iloc[1] == "rep_col"
    assert seed_descs.iloc[1] == "Representative measure"
