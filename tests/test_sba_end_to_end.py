import json
import sys
from pathlib import Path
from shutil import copyfile

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
        return json.dumps({"logical_entities": ["Business", "Loan", "Location"]})
    return json.dumps({"entity_assignment": "unassigned", "static_dynamic": "static"})


def test_sba_end_to_end_workflow(tmp_path, monkeypatch):
    """
    End-to-end SBA workflow regression test covering:
    init-workspace -> dataset-bootstrap -> bootstrap-config -> classify-entities -> clean-dataset.
    """
    # 1. Prepare a clean workspace
    workspace_dir = tmp_path
    prepare_workspace(str(workspace_dir))

    # 2. Copy SBA sample data into the temp workspace
    src_root = Path(__file__).resolve().parent.parent
    sample_data = src_root / "tests" / "data" / "sba_loans_raw.csv"
    sample_dictionary = src_root / "tests" / "data_dictionary" / "sba_dd.csv"

    target_data = workspace_dir / "data" / "sba_loans_raw.csv"
    target_dd = workspace_dir / "data_dictionary" / "sba_dd.csv"
    copyfile(sample_data, target_data)
    copyfile(sample_dictionary, target_dd)

    # 3. Run dataset-bootstrap to capture metadata
    monkeypatch.setattr(sys, "argv", [
        "dataset-bootstrap",
        str(workspace_dir),
        "--graph-mode", "tabular",
        "--dataset-type", "cross-sectional",
        "--subject", "loan",
        "--skip-use-case-answers",
        "--no-wide-short-homogeneous"
    ])
    dataset_bootstrap_cli.main()

    metadata_path = workspace_dir / "bootstrap_metadata.yaml"
    assert metadata_path.exists(), "dataset-bootstrap did not write bootstrap_metadata.yaml"

    metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    assert metadata["dataset_type"] == "cross-sectional"
    assert metadata["subject"] == "loan"

    # 4. Run bootstrap-config to generate the workspace config.yaml
    monkeypatch.setattr(bootstrap_cli, "console", DummyBootstrapConfigConsole())
    monkeypatch.setattr(sys, "argv", ["bootstrap-config", "--output", "config.yaml", str(workspace_dir)])
    bootstrap_cli.main()

    config_path = workspace_dir / "config.yaml"
    assert config_path.exists(), "bootstrap-config did not generate config.yaml"

    config_payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert config_payload["dataset_type"] == "cross-sectional"
    assert config_payload["parser"]["data_dictionary_file"] == "sba_dd.csv"
    assert config_payload["cleaner"]["raw_dataset_file"] == "sba_loans_raw.csv"

    # 5. Run classify-entities with deterministic LLM behavior
    monkeypatch.setattr("dd_parser.orchestrator.LLMEntityClassifier.is_ready", lambda self: True)
    monkeypatch.setattr("dd_parser.llm_client.LLMEntityClassifier._call_llm", _dummy_llm_call)

    coordinator = PathCoordinator(config_path=str(config_path))
    parser_orchestrator = PipelineOrchestrator(path_coordinator=coordinator)
    parser_orchestrator.process_pipeline()

    assert coordinator.data_dictionary_csv_path.exists(), "Parser did not generate data_dictionary_csv_path"
    assert coordinator.dataset_manifest_path.exists(), "Parser did not generate dataset manifest"
    assert coordinator.attribute_manifest_path.exists(), "Parser did not generate attribute manifest"
    assert coordinator.handshake_path.exists(), "Parser did not generate handshake file"

    # 6. Run clean-dataset against the parser handshake
    cleaner_coord = PathCoordinator(config_path=str(config_path))
    cleaner = CleanerOrchestrator(path_coordinator=cleaner_coord)
    cleaner.run_pipeline(action="full")

    assert cleaner_coord.profiling_report_path.exists(), "Cleaner did not generate profiling report"
    assert cleaner_coord.clean_dataset_output_path.exists(), "Cleaner did not generate clean dataset output"
    assert cleaner_coord.synchronized_dictionary_path.exists(), "Cleaner did not generate synchronized dictionary"
    assert (cleaner_coord.cleaner_narrative_directory / "cleaning_recommendations.md").exists(), "Cleaner did not generate recommendations report"
