from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Any, Dict, List

PACKAGE_NAME = "dd-parser-cleaner"
CLI_COMMANDS = [
    "classify-entities",
    "clean-dataset",
    "init-workspace",
    "location-helper",
    "dataset-bootstrap",
    "bootstrap-config",
]


def get_cli_command_names() -> List[str]:
    """Return the supported dd-parser-cleaner CLI commands."""
    return list(CLI_COMMANDS)


def get_package_version() -> str:
    """Return the installed distribution version or fall back to a sensible default."""
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "0.5.0"


def get_package_info() -> Dict[str, Any]:
    """
    Return package discovery metadata for clients and agents.

    This function is intentionally additive and backward-compatible:
    - Keeps legacy keys for older clients.
    - Adds optional, machine-readable fields that agents can use to discover
      manifest schemas, handshake contract, supported dataset types, and
      important config flags.
    """
    base: Dict[str, Any] = {
        "package_name": PACKAGE_NAME,
        "version": get_package_version(),
        "entry_points": {
            "classify_entities": "dd_parser.cli:main",
            "clean_dataset": "dd_cleaner.cli:main",
            "init_workspace": "dd_common.workspace_cli:main",
            "location_helper": "dd_common.location_cli:main",
            "dataset_bootstrap": "dd_common.dataset_bootstrap_cli:main",
            "bootstrap_config": "dd_common.bootstrap_cli:main",
        },
        "cli_commands": get_cli_command_names(),
        "provided_packages": ["dd_parser", "dd_cleaner", "dd_common"],
        "documentation_note": (
            "This package includes the agent guidance file AGENTS.md as an installed package resource. "
            "Clients should use the package metadata below or importlib.resources to access it."
        ),
    }

    base.update(
        {
            "agent_instructions_resource": {
                "package": "dd_common",
                "resource_name": "AGENTS.md",
                "description": "Agent workflow guidance and human prompt instructions packaged with dd-parser-cleaner.",
                "access_examples": {
                    "python": (
                        "from importlib.resources import files\n"
                        "print(files('dd_common').joinpath('AGENTS.md').read_text())"
                    ),
                },
            },
            "manifest_schema_paths": {
                "dataset_manifest": "schemas/dataset_manifest.json",
                "attribute_manifest": "schemas/attribute_manifest.json",
                "handshake": "schemas/handshake.json",
            },
            "handshake_spec": {
                "handshake_file": "manifests/handshake.json",
                "status_values": ["ready", "blocked", "warnings"],
                "featurizer_contract": "Featurizer must read handshake and refuse to proceed if status == blocked",
            },
            "supported_dataset_types": [
                "cross_sectional",
                "event_log",
                "panel",
                "graph_homogeneous",
                "graph_bipartite",
                "graph_heterogeneous",
            ],
            "config_flags": {
                "require_manifest_before_featurize": True,
                "use_case_questions_enabled": False,
                "enable_dataset_questionnaire": False,
                "interactive_mode": False,
                "questionnaire_schema_path": "documents/config/dataset_questions.json",
                "handshake_require_questions": False,
                "graph_entity_limit": 5,
                "generate_surrogate_keys": True,
                "url_sample_size": 10,
            },
            "sample_manifests_location": "tests/fixtures/manifests",
            "cli_help_map": {
                "classify-entities": "Detect entities and emit attribute manifest",
                "clean-dataset": "Run cleaner validations and emit dataset manifest and handshake",
                "init-workspace": "Create KMDS workspace layout",
                "location-helper": "Resolve dataset paths and storage locations",
                "dataset-bootstrap": "Capture dataset type metadata before generating config",
                "bootstrap-config": "Create default config.yaml",
            },
            "compatibility_notes": (
                "New manifest fields are additive and optional. Existing cross-sectional outputs remain unchanged."
            ),
            "support_contact": "https://github.com/yourorg/dd-parser-cleaner/issues",
        }
    )

    return base
