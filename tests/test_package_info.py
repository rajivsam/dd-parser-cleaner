import pytest
from dd_parser_cleaner import get_package_info, get_cli_command_names, get_package_version


def test_get_package_info_contains_expected_fields():
    info = get_package_info()

    assert isinstance(info, dict)
    assert info["package_name"] == "dd-parser-cleaner"
    assert info["version"] == get_package_version()
    assert "cli_commands" in info
    assert isinstance(info["cli_commands"], list)
    assert "classify-entities" in info["cli_commands"]
    assert "clean-dataset" in info["cli_commands"]


def test_get_cli_command_names_returns_list():
    names = get_cli_command_names()
    assert isinstance(names, list)
    assert "init-workspace" in names
    assert "dataset-bootstrap" in names
    assert "bootstrap-config" in names


def test_get_package_info_contains_agent_instructions_resource():
    info = get_package_info()
    assert "agent_instructions_resource" in info
    assert info["agent_instructions_resource"]["package"] == "dd_common"
    assert info["agent_instructions_resource"]["resource_name"] == "AGENTS.md"


def test_agent_instructions_resource_is_readable():
    import sys
    from importlib.resources import files
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))

    resource = files("dd_common").joinpath("AGENTS.md")
    assert resource.read_text().startswith("# dd-parser-cleaner Agent Instructions")


def test_get_package_info_contains_discovery_metadata():
    info = get_package_info()

    assert "manifest_schema_paths" in info
    assert isinstance(info["manifest_schema_paths"], dict)
    assert "handshake_spec" in info
    assert isinstance(info["handshake_spec"], dict)
    assert info["handshake_spec"]["status_values"] == ["ready", "blocked", "warnings"]
    assert "supported_dataset_types" in info
    assert "config_flags" in info
    assert info["config_flags"]["require_manifest_before_featurize"] is True
    assert info["config_flags"]["generate_surrogate_keys"] is True
    assert "dataset-bootstrap" in info["cli_help_map"]
