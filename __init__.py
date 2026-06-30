from __future__ import annotations

import sys
from pathlib import Path

# Ensure local src packages are importable when working from the repository root.
_repo_root = Path(__file__).resolve().parent
_src_path = _repo_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from dd_common import get_package_info, get_cli_command_names, get_package_version

__all__ = [
    "get_package_info",
    "get_cli_command_names",
    "get_package_version",
]
