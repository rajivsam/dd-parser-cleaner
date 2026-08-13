import json
import sys
from pathlib import Path
from shutil import copyfile

import yaml
from dd_common import bootstrap_cli, dataset_bootstrap_cli
from dd_common.path_coordinator import PathCoordinator
from dd_common.utilities import prepare_workspace
from dd_cleaner.orchestrator import CleanerOrchestrator
from dd_parser.orchestrator import PipelineOrchestrator


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
        return json.dumps({"logical_entities": ["Traffic", "Weather", "Temporal"]})
    return json.dumps({"entity_assignment": "unassigned", "static_dynamic": "static"})


def test_mn_traffic_end_to_end_workflow(tmp_path, monkeypatch):
    workspace_dir = tmp_path
    prepare_workspace(str(workspace_dir))

    sample_data = Path(__file__).resolve().parent / "data" / "MN_traffic.csv"
    sample_dictionary = Path(__file__).resolve().parent.parent / "tests" / "data_dictionary" / "MN_traffic_dd.csv"
    copyfile(sample_data, workspace_dir / "data" / "MN_traffic.csv")
    copyfile(sample_dictionary, workspace_dir / "data_dictionary" / "MN_traffic_dd.csv")

    monkeypatch.setattr(dataset_bootstrap_cli, "console", DummyBootstrapConsole([
        "1",          # single row = one subject
        "1",          # tabular analysis goal
        "3",          # panel dataset type
        "segment_id"  # subject id attribute
    ]))
    monkeypatch.setattr(sys, "argv", [
        "dataset-bootstrap",
        str(workspace_dir),
        "--graph-mode", "tabular",
        "--dataset-type", "panel",
        "--subject", "traffic",
        "--skip-use-case-answers",
        "--no-wide-short-homogeneous"
    ])
    dataset_bootstrap_cli.main()

    metadata_path = workspace_dir / "bootstrap_metadata.yaml"
    assert metadata_path.exists(), "dataset-bootstrap did not write bootstrap_metadata.yaml"

    metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    assert metadata["dataset_type"] == "panel"
    assert metadata["subject"] == "traffic"

    monkeypatch.setattr(bootstrap_cli, "console", DummyBootstrapConfigConsole())
    monkeypatch.setattr(sys, "argv", ["bootstrap-config", "--output", "config.yaml", str(workspace_dir)])
    bootstrap_cli.main()

    config_path = workspace_dir / "config.yaml"
    assert config_path.exists(), "bootstrap-config did not generate config.yaml"

    config_payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert config_payload["dataset_type"] == "panel"
    assert config_payload["parser"]["data_dictionary_file"] == "MN_traffic_dd.csv"
    assert config_payload["cleaner"]["raw_dataset_file"] == "MN_traffic.csv"

    monkeypatch.setattr("dd_parser.orchestrator.LLMEntityClassifier.is_ready", lambda self: True)
    monkeypatch.setattr("dd_parser.llm_client.LLMEntityClassifier._call_llm", _dummy_llm_call)

    monkeypatch.setattr(sys, "argv", ["dd_parser", "--config", str(config_path)])
    import dd_parser.cli as parser_cli
    parser_cli.main()

    coordinator = PathCoordinator(config_path=str(config_path))
    assert coordinator.dataset_manifest_path.exists(), "Parser did not generate dataset manifest for MN traffic"
    assert coordinator.attribute_manifest_path.exists(), "Parser did not generate attribute manifest for MN traffic"
    assert coordinator.handshake_path.exists(), "Parser did not generate handshake for MN traffic"
    assert coordinator.data_dictionary_csv_path.exists(), "Parser did not emit the analysis CSV for MN traffic"

    monkeypatch.setattr(sys, "argv", ["dd_cleaner", "--config", str(config_path), "--action", "full"])
    import dd_cleaner.cli as cleaner_cli
    cleaner_cli.main()

    assert coordinator.profiling_report_path.exists(), "Cleaner did not generate profiling report for MN traffic"
    assert coordinator.clean_dataset_output_path.exists(), "Cleaner did not generate clean dataset output for MN traffic"
    assert coordinator.synchronized_dictionary_path.exists(), "Cleaner did not generate synchronized dictionary for MN traffic"
    assert (coordinator.cleaner_narrative_directory / "cleaning_recommendations.md").exists(), "Cleaner did not generate recommendations report for MN traffic"
