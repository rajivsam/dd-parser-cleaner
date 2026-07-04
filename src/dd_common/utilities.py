import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

def verify_workspace_status(working_path: Path) -> bool:
    """
    Checks if the specified Path is already configured for dd-parser-cleaner.
    Returns True if core KMDS directories exist, False otherwise.
    """
    base = working_path # Assume working_path is already resolved
    
    # Minimal set required for diagnostic discovery and bootstrapping.
    # While 'init-workspace' creates core workspace directories, we do not require
    # a top-level schemas folder for workspace-specific questionnaire config.
    required_dirs = ["data", "data_dictionary", "documents", "notebooks", "models"]
    
    for folder in required_dirs:
        if not (base / folder).is_dir():
            return False
            
    return True

def prepare_workspace(working_dir: str = ".") -> Path:
    """
    Standardizes the workspace for dd-parser-cleaner.
    Ensures required directories exist and provisions the dataset questionnaire schema.
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

    # 2. Provision workspace-specific questionnaire config under documents/config.
    config_dir = base / "documents" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Verified or created workspace config directory: {config_dir.relative_to(base)}")

    config_schema_file = config_dir / "dataset_questions.json"
    if not config_schema_file.exists():
        packaged_schema = Path(__file__).resolve().parent / "schemas" / "dataset_questions.json"
        if packaged_schema.exists():
            shutil.copy(packaged_schema, config_schema_file)
            print(f"📄 Provisioned questionnaire schema: {config_schema_file.relative_to(base)}")
        else:
            print(f"⚠️ Warning: Packaged questionnaire schema missing at {packaged_schema}. Create {config_schema_file.relative_to(base)} manually.")

    # 3. Verify Safety Gate (Handshake) location
    handshake_dir = base / "documents" / "dd_cleaner"
    handshake_file = handshake_dir / "parser_cleaner_handshake.md"
    if not handshake_file.exists():
        # Ensure the subdirectory exists even if the file doesn't yet
        handshake_dir.mkdir(parents=True, exist_ok=True)
        print(f"💡 Note: Workspace ready. Handshake file will be expected at {handshake_file} after parsing.")

    return base