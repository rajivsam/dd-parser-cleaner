"""Utilities for initializing and managing interactive Jupyter Notebook sessions."""

import pandas as pd
import sys
import logging
from pathlib import Path
from typing import Tuple
from path_coordinator import PathCoordinator

logger = logging.getLogger(__name__)

def prepare_workspace(working_dir: str = ".") -> PathCoordinator:
    """
    Standardizes the workspace for the Migration Assistant.
    Ensures required directories exist and creates a domain_logic stub if missing.
    """
    coord = PathCoordinator(working_dir=working_dir)
    
    # 1. Ensure scripts directory exists
    scripts_dir = coord.base_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    
    # 2. Ensure domain_logic.py exists
    logic_file = scripts_dir / "domain_logic.py"
    if not logic_file.exists():
        with open(logic_file, "w") as f:
            f.write("import pandas as pd\nimport numpy as np\n\n"
                    "# Add your custom Transform, Filter, and Derivation logic here.\n")
        print(f"✨ Created initial logic stub: {logic_file}")

    # 3. Verify Safety Gate (Handshake)
    # Note: Handshake is usually in documents/dd_cleaner/
    handshake_dir = coord.base_dir / "documents" / "dd_cleaner"
    handshake_file = handshake_dir / "parser_cleaner_handshake.md"
    if not handshake_file.exists():
        print(f"⚠️  Warning: Handshake file missing at {handshake_file}. "
              "Discovery and full cleaning may be restricted.")
              
    return coord

def init_notebook_session(working_dir: str = ".") -> Tuple[PathCoordinator, pd.DataFrame]:
    """
    Initializes a notebook session by setting up the PathCoordinator 
    and loading the raw dataset for experimentation.

    Assumes the notebook may be running from within the 'notebooks/' subdirectory.
    """
    current_path = Path.cwd()
    
    # 1. Resolve Project Root
    # If running inside 'notebooks/', the project root is the parent directory.
    # We verify if we need to move up one level.
    if current_path.name == "notebooks":
        base_path = current_path.parent
    else:
        base_path = Path(working_dir)

    # 2. Setup Coordinator
    coord = PathCoordinator(working_dir=str(base_path))
    
    # 2. Ensure scripts directory is in path for easy importing of domain_logic
    scripts_path = str(coord.base_dir / "scripts")
    if scripts_path not in sys.path:
        sys.path.append(scripts_path)
        
    # 3. Load sample data
    raw_data_path = coord.raw_dataset_path
    if not raw_data_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at {raw_data_path}")
        
    df = pd.read_csv(raw_data_path)
    return coord, df