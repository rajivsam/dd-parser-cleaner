import pytest
from pathlib import Path
from dd_common.utilities import prepare_workspace, verify_workspace_status


def test_verify_workspace_status_with_all_required_directories(tmp_path: Path):
    required_dirs = ["data", "data_dictionary", "documents", "notebooks", "models"]
    for directory in required_dirs:
        (tmp_path / directory).mkdir(parents=True, exist_ok=True)

    assert verify_workspace_status(tmp_path) is True


def test_prepare_workspace_logs_verified_directories_when_present(tmp_path: Path, capsys):
    required_dirs = ["data", "data_dictionary", "documents", "notebooks", "models"]
    for directory in required_dirs:
        (tmp_path / directory).mkdir(parents=True, exist_ok=True)

    prepare_workspace(working_dir=str(tmp_path))
    captured = capsys.readouterr()

    for directory in required_dirs:
        assert f"✅ Verified directory: {directory}" in captured.out


def test_prepare_workspace_creates_missing_directories(tmp_path: Path, capsys):
    required_dirs = ["data", "data_dictionary", "documents", "notebooks", "models"]

    prepare_workspace(working_dir=str(tmp_path))
    captured = capsys.readouterr()

    for directory in required_dirs:
        assert (tmp_path / directory).is_dir()
        assert f"📁 Created missing directory: {directory}" in captured.out
