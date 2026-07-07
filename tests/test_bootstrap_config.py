import sys
import yaml
from pathlib import Path

import dd_common.bootstrap_cli as bootstrap_cli


class DummyConsole:
    def __init__(self, answers=None):
        self.answers = answers or []
        self.index = 0

    def input(self, prompt: str = "") -> str:
        if "Attribute" in prompt:
            return "Field Name"
        if "event log" in prompt.lower():
            return self._next_answer("n")
        if "subject id" in prompt.lower():
            return self._next_answer("subject_id")
        return self._next_answer("0")

    def _next_answer(self, default: str) -> str:
        if self.index < len(self.answers):
            answer = self.answers[self.index]
            self.index += 1
            return answer
        return default

    def print(self, *args, **kwargs):
        return None


def test_bootstrap_generates_manifest_filenames(tmp_path, monkeypatch):
    for folder in ["data", "data_dictionary", "documents", "notebooks", "models"]:
        (tmp_path / folder).mkdir(parents=True, exist_ok=True)
    (tmp_path / "documents" / "config").mkdir(parents=True, exist_ok=True)

    (tmp_path / "data" / "sample.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (tmp_path / "data_dictionary" / "sample_dd.csv").write_text(
        "Field Name,Description\ncol1,desc\n", encoding="utf-8"
    )
    (tmp_path / "documents" / "config" / "dataset_questions.json").write_text(
        '{"questions": []}', encoding="utf-8"
    )

    monkeypatch.setattr(bootstrap_cli, "console", DummyConsole())
    monkeypatch.setattr(sys, "argv", ["bootstrap-config", str(tmp_path)])

    bootstrap_cli.main()

    generated_path = tmp_path / "provisional_config.yaml"
    assert generated_path.exists(), "bootstrap-config did not generate provisional_config.yaml"

    payload = yaml.safe_load(generated_path.read_text(encoding="utf-8"))
    assert payload["dataset_id"] == "sample"
    assert payload["parser"]["dataset_manifest_filename"] == "sample_dataset_manifest.json"
    assert payload["parser"]["attribute_manifest_filename"] == "sample_attribute_manifest.json"
    assert payload["cleaner"]["handshake_file"] == "sample_parser_cleaner_handshake.md"


def test_bootstrap_panel_dataset_enables_questionnaire_and_writes_config_yaml(tmp_path, monkeypatch):
    for folder in ["data", "data_dictionary", "documents", "notebooks", "models"]:
        (tmp_path / folder).mkdir(parents=True, exist_ok=True)
    (tmp_path / "documents" / "config").mkdir(parents=True, exist_ok=True)

    (tmp_path / "data" / "panel.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (tmp_path / "data_dictionary" / "panel_dd.csv").write_text(
        "Field Name,Description\ncol1,desc\n", encoding="utf-8"
    )
    (tmp_path / "documents" / "config" / "dataset_questions.json").write_text(
        '{"questions": []}', encoding="utf-8"
    )

    monkeypatch.setattr(bootstrap_cli, "console", DummyConsole())
    monkeypatch.setattr(sys, "argv", ["bootstrap-config", "--dataset-type", "panel", "--output", "config.yaml", str(tmp_path)])

    bootstrap_cli.main()

    generated_path = tmp_path / "config.yaml"
    assert generated_path.exists(), "bootstrap-config did not generate config.yaml for panel dataset"

    payload = yaml.safe_load(generated_path.read_text(encoding="utf-8"))
    assert payload["dataset_type"] == "panel"
    assert payload["enable_dataset_questionnaire"] is False
    assert payload["interactive_mode"] is False
    assert payload["handshake_require_questions"] is False
    assert payload["parser"]["data_dictionary_file"] == "panel_dd.csv"
    assert payload["cleaner"]["raw_dataset_file"] == "panel.csv"


def test_bootstrap_event_log_prompts_subject_id_attribute(tmp_path, monkeypatch):
    for folder in ["data", "data_dictionary", "documents", "notebooks", "models"]:
        (tmp_path / folder).mkdir(parents=True, exist_ok=True)
    (tmp_path / "documents" / "config").mkdir(parents=True, exist_ok=True)

    (tmp_path / "data" / "panel.csv").write_text("subject_id,score\n1,100\n1,110\n2,90\n", encoding="utf-8")
    (tmp_path / "data_dictionary" / "panel_dd.csv").write_text(
        "Field Name,Description\nsubject_id,Subject key\nscore,Numeric value\n", encoding="utf-8"
    )
    (tmp_path / "documents" / "config" / "dataset_questions.json").write_text(
        '{"questions": []}', encoding="utf-8"
    )

    monkeypatch.setattr(bootstrap_cli, "console", DummyConsole(answers=["y", "subject_id"]))
    monkeypatch.setattr(sys, "argv", ["bootstrap-config", "--dataset-type", "panel", "--output", "config.yaml", str(tmp_path)])

    bootstrap_cli.main()

    generated_path = tmp_path / "config.yaml"
    assert generated_path.exists(), "bootstrap-config did not generate config.yaml for event-log dataset"

    payload = yaml.safe_load(generated_path.read_text(encoding="utf-8"))
    assert payload["dataset_type"] == "event_log"
    assert payload["cleaner"]["structural_assessment"]["subject_id_attribute"] == "subject_id"


def test_dataset_bootstrap_writes_metadata(tmp_path, monkeypatch):
    from dd_common import dataset_bootstrap_cli as bootstrap_ds

    for folder in ["data", "data_dictionary", "documents", "notebooks", "models"]:
        (tmp_path / folder).mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "startup.csv").write_text("id,value\n1,10\n", encoding="utf-8")
    (tmp_path / "data_dictionary" / "startup_dd.csv").write_text(
        "Field Name,Description\nid,Identifier\nvalue,Value\n", encoding="utf-8"
    )

    class DummyBootstrapConsole:
        def __init__(self):
            self.answers = iter([
                "n",            # wide-short homogeneous dataset
                "tabular",      # Graph or Tabular
                "unsure",       # Cross-sectional/panel/unsure
                "customer",     # Subject
                "n",            # row represents single point
                "subject_id",   # subject id attribute
                "y",            # capture use case answers
                "Forecast sales",  # use case
                "Improve churn"      # analysis objective
            ])

        def input(self, prompt: str = "") -> str:
            return next(self.answers)

        def print(self, *args, **kwargs):
            pass

    monkeypatch.setattr(bootstrap_ds, "console", DummyBootstrapConsole())
    monkeypatch.setattr(sys, "argv", ["dataset-bootstrap", str(tmp_path)])

    bootstrap_ds.main()

    metadata_path = tmp_path / "bootstrap_metadata.yaml"
    assert metadata_path.exists()
    metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    assert metadata["dataset_type"] == "event_log"
    assert metadata["subject"] == "customer"
    assert metadata["subject_id_attribute"] == "subject_id"
    assert metadata["use_case_answers"]["use_case"] == "Forecast sales"
    assert metadata["use_case_answers"]["analysis_objective"] == "Improve churn"


def test_dataset_bootstrap_homogeneous_graph_uses_tabular_questionnaire(tmp_path, monkeypatch):
    from dd_common import dataset_bootstrap_cli as bootstrap_ds

    for folder in ["data", "data_dictionary", "documents", "notebooks", "models"]:
        (tmp_path / folder).mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "graph.csv").write_text("source,target\n1,2\n", encoding="utf-8")
    (tmp_path / "data_dictionary" / "graph_dd.csv").write_text(
        "Field Name,Description\nsource,Source node\ntarget,Target node\n", encoding="utf-8"
    )

    class DummyBootstrapConsole:
        def __init__(self):
            self.answers = iter([
                "n",            # wide-short homogeneous dataset
                "graph",           # Graph or Tabular
                "homogeneous",    # homogeneous or other
                "unsure",         # Cross-sectional/panel/unsure
                "node",           # Subject
                "y",              # row represents single point in time
                "y",              # all subjects same point in time
                "y",              # capture use case answers
                "Predict links",  # use case
                "Understand topology"  # analysis objective
            ])

        def input(self, prompt: str = "") -> str:
            return next(self.answers)

        def print(self, *args, **kwargs):
            pass

    monkeypatch.setattr(bootstrap_ds, "console", DummyBootstrapConsole())
    monkeypatch.setattr(sys, "argv", ["dataset-bootstrap", str(tmp_path)])

    bootstrap_ds.main()

    metadata_path = tmp_path / "bootstrap_metadata.yaml"
    assert metadata_path.exists()
    metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    assert metadata["dataset_type"] == "graph_homogeneous"
    assert metadata["graph_type"] == "homogeneous"
    assert metadata["subject"] == "node"
    assert metadata["use_case_answers"]["use_case"] == "Predict links"
    assert metadata["use_case_answers"]["analysis_objective"] == "Understand topology"


def test_bootstrap_config_uses_bootstrap_metadata(tmp_path, monkeypatch):
    for folder in ["data", "data_dictionary", "documents", "notebooks", "models"]:
        (tmp_path / folder).mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "startup.csv").write_text("id,value\n1,10\n", encoding="utf-8")
    (tmp_path / "data_dictionary" / "startup_dd.csv").write_text(
        "Field Name,Description\nid,Identifier\nvalue,Value\n", encoding="utf-8"
    )
    (tmp_path / "documents" / "config").mkdir(parents=True, exist_ok=True)
    (tmp_path / "documents" / "config" / "dataset_questions.json").write_text(
        '{"questions": []}', encoding="utf-8"
    )
    bootstrap_metadata = {
        "dataset_type": "event_log",
        "subject": "device",
        "subject_id_attribute": "id",
        "use_case_answers": {}
    }
    (tmp_path / "bootstrap_metadata.yaml").write_text(yaml.safe_dump(bootstrap_metadata), encoding="utf-8")

    monkeypatch.setattr(bootstrap_cli, "console", DummyConsole())
    monkeypatch.setattr(sys, "argv", ["bootstrap-config", str(tmp_path)])

    bootstrap_cli.main()

    generated_path = tmp_path / "provisional_config.yaml"
    assert generated_path.exists()
    payload = yaml.safe_load(generated_path.read_text(encoding="utf-8"))
    assert payload["dataset_type"] == "event_log"
    assert payload["cleaner"]["structural_assessment"]["subject_id_attribute"] == "id"


def test_bootstrap_config_propagates_wide_short_metadata(tmp_path, monkeypatch):
    for folder in ["data", "data_dictionary", "documents", "notebooks", "models"]:
        (tmp_path / folder).mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "startup.csv").write_text("id,value\n1,10\n", encoding="utf-8")
    (tmp_path / "data_dictionary" / "startup_dd.csv").write_text(
        "Field Name,Description\nid,Identifier\nvalue,Value\n", encoding="utf-8"
    )
    (tmp_path / "documents" / "config").mkdir(parents=True, exist_ok=True)
    (tmp_path / "documents" / "config" / "dataset_questions.json").write_text(
        '{"questions": []}', encoding="utf-8"
    )
    bootstrap_metadata = {
        "dataset_type": "cross-sectional",
        "subject": "customer",
        "wide_short_homogeneous": True,
        "wide_short_representative_column": "customer_id",
        "use_case_answers": {}
    }
    (tmp_path / "bootstrap_metadata.yaml").write_text(yaml.safe_dump(bootstrap_metadata), encoding="utf-8")

    monkeypatch.setattr(bootstrap_cli, "console", DummyConsole())
    monkeypatch.setattr(sys, "argv", ["bootstrap-config", str(tmp_path)])

    bootstrap_cli.main()

    generated_path = tmp_path / "provisional_config.yaml"
    assert generated_path.exists()
    payload = yaml.safe_load(generated_path.read_text(encoding="utf-8"))
    assert payload["parser"]["wide_short_homogeneous"] is True
    assert payload["parser"]["wide_short_representative_column"] == "customer_id"
