"""Utilities for initializing and managing interactive Jupyter Notebook sessions."""

import pandas as pd
import sys
import logging
from pathlib import Path
from typing import Tuple
from dd_common.path_coordinator import PathCoordinator
from dd_common.utilities import prepare_workspace as _prepare_workspace

logger = logging.getLogger(__name__)

def prepare_workspace(working_dir: str = ".") -> PathCoordinator:
    base_path = _prepare_workspace(working_dir)
    return PathCoordinator(working_dir=base_path)

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