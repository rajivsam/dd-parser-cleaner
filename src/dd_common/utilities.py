import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__) 

def verify_workspace_status(working_path: Path) -> bool:
    """
    Checks if the specified Path is already configured for dd-parser-cleaner.
    Returns True if core KMDS directories exist, False otherwise.
    """
    base = working_path # Assume working_path is already resolved
    
    # Minimal set required for diagnostic discovery and bootstrapping.
    # While 'init-workspace' creates 5 directories, we enforce the core KMDS
    # structure required for workspace verification and notebook integration.
    required_dirs = ["data", "data_dictionary", "documents", "notebooks", "models"]
    
    for folder in required_dirs:
        if not (base / folder).is_dir():
            return False
            
    return True

def prepare_workspace(working_dir: str = ".") -> Path:
    """
    Standardizes the workspace for dd-parser-cleaner.
    Ensures required directories (data, data_dictionary, documents, notebooks, models) 
    exist and creates a domain_logic stub if missing.
    """
    base = Path(working_dir).resolve()
    
    # 1. Ensure core directories exist
    required_dirs = ["data", "data_dictionary", "documents", "notebooks", "models"]
    for folder in required_dirs:
        dir_path = base / folder
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created missing directory: {folder}")
        else:
            print(f"✅ Verified directory: {folder}")
    
    # The 'scripts' directory and domain_logic.py are no longer managed by init-workspace.
    # Users are expected to manage their own scripts for imperative transformations.

    # 2. Verify Safety Gate (Handshake) location
    handshake_dir = base / "documents" / "dd_cleaner"
    handshake_file = handshake_dir / "parser_cleaner_handshake.md"
    if not handshake_file.exists():
        # Ensure the subdirectory exists even if the file doesn't yet
        handshake_dir.mkdir(parents=True, exist_ok=True)
        print(f"💡 Note: Workspace ready. Handshake file will be expected at {handshake_file} after parsing.")
              
    return base