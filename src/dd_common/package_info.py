from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Any, Dict, List

PACKAGE_NAME = "dd-parser-cleaner"
CLI_COMMANDS = [
    "classify-entities",
    "clean-dataset",
    "init-workspace",
    "location-helper",
    "bootstrap-config",
]


def get_cli_command_names() -> List[str]:
    """Return the supported dd-parser-cleaner CLI commands."""
    return list(CLI_COMMANDS)


def get_package_version() -> str:
    """Return the installed distribution version or fall back to the declared package name."""
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "0.5.0"


def get_package_info() -> Dict[str, Any]:
    """Return package discovery metadata for clients."""
    return {
        "package_name": PACKAGE_NAME,
        "version": get_package_version(),
        "entry_points": {
            "classify_entities": "dd_parser.cli:main",
            "clean_dataset": "dd_cleaner.cli:main",
            "init_workspace": "dd_common.workspace_cli:main",
            "location_helper": "dd_common.location_cli:main",
            "bootstrap_config": "dd_common.bootstrap_cli:main",
        },
        "cli_commands": get_cli_command_names(),
        "provided_packages": ["dd_parser", "dd_cleaner", "dd_common"],
        "documentation_note": (
            "This package does not ship embedded documents in the installed distribution. "
            "Use the repository top-level USER_GUIDE.md and documents/ folder for onboarding and implementation guidance."
        ),
    }
