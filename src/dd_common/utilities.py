import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def verify_workspace_status(working_dir: str = ".") -> bool:
    """
    Checks if the specified directory is already configured for dd-parser-cleaner.
    Returns True if core KMDS directories exist, False otherwise.
    """
    base = Path(working_dir).resolve()
    required_dirs = ["data", "data_dictionary", "documents", "notebooks", "scripts"]
    
    for folder in required_dirs:
        if not (base / folder).is_dir():
            return False
            
    return True

def prepare_workspace(working_dir: str = ".") -> Path:
    """
    Standardizes the workspace for dd-parser-cleaner.
    Ensures required directories (data, data_dictionary, documents, notebooks, scripts) 
    exist and creates a domain_logic stub if missing.
    """
    base = Path(working_dir).resolve()
    
    # 1. Ensure core directories exist
    required_dirs = ["data", "data_dictionary", "documents", "notebooks", "scripts"]
    for folder in required_dirs:
        dir_path = base / folder
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created missing directory: {folder}")
        else:
            print(f"✅ Verified directory: {folder}")

    # 2. Ensure domain_logic.py exists in scripts/
    logic_file = base / "scripts" / "domain_logic.py"
    if not logic_file.exists():
        with open(logic_file, "w") as f:
            f.write("import pandas as pd\nimport numpy as np\n\n"
                    "# Add your custom Transform, Filter, and Derivation logic here.\n")
        print(f"✨ Created initial logic stub: scripts/domain_logic.py")

    # 3. Verify Safety Gate (Handshake) location
    handshake_dir = base / "documents" / "dd_cleaner"
    handshake_file = handshake_dir / "parser_cleaner_handshake.md"
    if not handshake_file.exists():
        # Ensure the subdirectory exists even if the file doesn't yet
        handshake_dir.mkdir(parents=True, exist_ok=True)
        print(f"💡 Note: Workspace ready. Handshake file will be expected at {handshake_file} after parsing.")
              
    return base