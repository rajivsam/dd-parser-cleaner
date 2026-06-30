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
    assert "bootstrap-config" in names
