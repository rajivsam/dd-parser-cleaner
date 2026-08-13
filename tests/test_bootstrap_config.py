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
                "1",            # one subject row
                "1",            # tabular analysis goal
                "customer",     # subject
                "1",            # cross-sectional taxonomy
                "n",            # no use-case answers
                "n",            # not wide-short homogeneous after classification
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
    assert metadata["dataset_type"] == "cross-sectional"
    assert metadata["subject"] == "customer"
    assert metadata["subject_id_attribute"] is None or metadata["subject_id_attribute"] == ""
    assert metadata["use_case_answers"] == {}


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
                "1",            # one subject row
                "2",            # network/graph analysis goal
                "y",            # confirm true network graph
                "node",         # subject
                "n",            # no use-case answers
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
    assert metadata["use_case_answers"] == {}


def test_dataset_bootstrap_resolves_single_active_file_and_uses_tabular_branch(tmp_path, monkeypatch):
    from dd_common import dataset_bootstrap_cli as bootstrap_ds

    for folder in ["data", "data_dictionary", "documents", "notebooks", "models"]:
        (tmp_path / folder).mkdir(parents=True, exist_ok=True)

    (tmp_path / "data" / "active.csv").write_text("customer_id,score\n1,10\n2,20\n", encoding="utf-8")
    (tmp_path / "data" / "backup.csv").write_text("customer_id,score\n9,90\n", encoding="utf-8")
    (tmp_path / "data_dictionary" / "schema_v2.csv").write_text(
        "Field Name,Description\ncustomer_id,Customer id\nscore,Score\n", encoding="utf-8"
    )
    (tmp_path / "data_dictionary" / "schema_old.csv").write_text(
        "Field Name,Description\nold_id,Old id\n", encoding="utf-8"
    )

    class DummyBootstrapConsole:
        def __init__(self):
            self.answers = iter([
                "2",            # data folder has multiple files; choose single active file
                "1",            # select active.csv
                "1",            # data_dictionary choose schema_v2
                "1",            # single row represents one subject
                "1",            # analysis goal: tabular grouping/analysis
                "customer",     # subject
                "1",            # cross-sectional
                "n",            # skip capture use-case answers
                "n",            # not wide-short after classification
            ])

        def input(self, prompt: str = "") -> str:
            return next(self.answers)

        def print(self, *args, **kwargs):
            pass

    monkeypatch.setattr(bootstrap_ds, "console", DummyBootstrapConsole())
    monkeypatch.setattr(sys, "argv", ["dataset-bootstrap", "--skip-use-case-answers", str(tmp_path)])

    bootstrap_ds.main()

    metadata = yaml.safe_load((tmp_path / "bootstrap_metadata.yaml").read_text(encoding="utf-8"))
    assert metadata["dataset_type"] == "cross-sectional"
    assert metadata["subject"] == "customer"
    assert metadata["wide_short_homogeneous"] is False
    assert metadata["graph_mode"] == "tabular"


def test_dataset_bootstrap_defers_wide_short_until_after_tabular_classification(tmp_path, monkeypatch):
    from dd_common import dataset_bootstrap_cli as bootstrap_ds

    for folder in ["data", "data_dictionary", "documents", "notebooks", "models"]:
        (tmp_path / folder).mkdir(parents=True, exist_ok=True)

    (tmp_path / "data" / "active.csv").write_text("customer_id,score\n1,10\n2,20\n", encoding="utf-8")
    (tmp_path / "data_dictionary" / "schema.csv").write_text(
        "Field Name,Description\ncustomer_id,Customer id\nscore,Score\n", encoding="utf-8"
    )

    prompt_order = []

    class DummyBootstrapConsole:
        def __init__(self):
            self.answers = iter([
                "1",  # select the one dataset file
                "1",  # select the data dictionary file
                "1",  # single-row subject flow
                "1",  # tabular analysis goal
                "customer",  # subject
                "1",  # cross-sectional taxonomy
                "n",  # no use-case prompts
                "n",  # not wide-short after classification
            ])

        def input(self, prompt: str = "") -> str:
            prompt_order.append(prompt)
            return next(self.answers)

        def print(self, *args, **kwargs):
            pass

    monkeypatch.setattr(bootstrap_ds, "console", DummyBootstrapConsole())
    monkeypatch.setattr(sys, "argv", ["dataset-bootstrap", str(tmp_path)])

    bootstrap_ds.main()

    assert not any("wide-and-short" in prompt.lower() for prompt in prompt_order)

    goal_index = next(i for i, prompt in enumerate(prompt_order) if "primary analysis goal" in prompt.lower())
    subject_index = next(i for i, prompt in enumerate(prompt_order) if "single primary subject" in prompt.lower())

    assert goal_index < len(prompt_order)
    assert subject_index < len(prompt_order)

    metadata = yaml.safe_load((tmp_path / "bootstrap_metadata.yaml").read_text(encoding="utf-8"))
    assert metadata["wide_short_homogeneous"] is False


def test_dataset_bootstrap_auto_detects_wide_short_shape_without_prompt(tmp_path, monkeypatch):
    from dd_common import dataset_bootstrap_cli as bootstrap_ds

    for folder in ["data", "data_dictionary", "documents", "notebooks", "models"]:
        (tmp_path / folder).mkdir(parents=True, exist_ok=True)

    wide_df = "".join(
        [
            "customer_id,feat_1,feat_2,feat_3,feat_4,feat_5,feat_6,feat_7,feat_8,feat_9\n",
            "1,10,11,12,13,14,15,16,17,18\n",
            "2,20,21,22,23,24,25,26,27,28\n",
        ]
    )
    (tmp_path / "data" / "wide_short.csv").write_text(wide_df, encoding="utf-8")
    (tmp_path / "data_dictionary" / "wide_short_dd.csv").write_text(
        "Field Name,Description\ncustomer_id,Customer id\nfeat_1,Feature 1\nfeat_2,Feature 2\nfeat_3,Feature 3\nfeat_4,Feature 4\nfeat_5,Feature 5\nfeat_6,Feature 6\nfeat_7,Feature 7\nfeat_8,Feature 8\nfeat_9,Feature 9\n",
        encoding="utf-8",
    )

    prompt_order = []

    class DummyBootstrapConsole:
        def __init__(self):
            self.answers = iter([
                "1",  # select the single dataset file
                "1",  # select the one schema file
                "1",  # single-row subject flow
                "1",  # tabular analysis goal
                "customer",  # subject
                "1",  # cross-sectional taxonomy
                "n",  # no use-case prompts
            ])

        def input(self, prompt: str = "") -> str:
            prompt_order.append(prompt)
            return next(self.answers)

        def print(self, *args, **kwargs):
            pass

    monkeypatch.setattr(bootstrap_ds, "console", DummyBootstrapConsole())
    monkeypatch.setattr(sys, "argv", ["dataset-bootstrap", str(tmp_path)])

    bootstrap_ds.main()

    assert not any("wide-and-short" in prompt.lower() for prompt in prompt_order)
    metadata = yaml.safe_load((tmp_path / "bootstrap_metadata.yaml").read_text(encoding="utf-8"))
    assert metadata["wide_short_homogeneous"] is True
    assert metadata["wide_short_representative_column"] == "feat_1"


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
