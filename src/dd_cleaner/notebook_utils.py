"""Utilities for initializing and managing interactive Jupyter Notebook sessions."""
from typing import List
import json
import pandas as pd
import logging
from pathlib import Path
from typing import Tuple
from dd_common.path_coordinator import PathCoordinator
from dd_common.utilities import prepare_workspace as _prepare_workspace, verify_workspace_status
from dd_cleaner.assistant import CleaningAssistant
from rich.console import Console

logger = logging.getLogger(__name__)

def prepare_workspace(working_dir: str = ".") -> PathCoordinator:
    base_path = _prepare_workspace(working_dir)
    return PathCoordinator(working_dir=base_path)

def init_notebook_session(working_dir: str, config_path: str = "config.yaml") -> Tuple[PathCoordinator, pd.DataFrame]:
    """
    Initializes a notebook session by setting up the PathCoordinator
    and returning a DataFrame listing available artifacts.

    Args:
        working_dir (str): The root directory of the KMDS workspace.
        config_path (str): Optional path to the authoritative config.yaml file.
            If absolute, it is used directly. If relative, it is resolved from
            the working directory.

    Returns:
        Tuple[PathCoordinator, pd.DataFrame]: A tuple containing the PathCoordinator
        instance and a DataFrame detailing the available project artifacts.

    Raises:
        FileNotFoundError: If the workspace is not initialized or required files
                           from previous CLI steps are missing.
        ValueError: If config.yaml is missing or malformed.
    """
    console = Console()

    # 1. Resolve Project Root and Validate Workspace
    target_path = Path(working_dir).resolve()

    if not verify_workspace_status(target_path):
        error_msg = (
            f"❌ Error: The directory '{target_path}' is not an initialized KMDS workspace.\n"
            "👉 Please run 'init-workspace' first to create the required structure."
        )
        console.print(f"[bold red]{error_msg}[/bold red]")
        raise FileNotFoundError(error_msg)

    # 2. Setup Coordinator (will load the requested config path)
    config_file = Path(config_path)
    if config_file.is_absolute():
        config_path_norm = str(config_file)
    else:
        candidate_path = target_path / config_file
        if candidate_path.exists():
            config_path_norm = str(candidate_path.resolve())
        elif config_file.exists():
            config_path_norm = str(config_file.resolve())
        else:
            config_path_norm = str(candidate_path)

    try:
        coord = PathCoordinator(config_path=config_path_norm, working_dir=str(target_path))
    except FileNotFoundError as e:
        error_msg = (
            f"❌ Error: {e}\n"
            "👉 A 'config.yaml' file is required. Please run 'bootstrap-config' to generate one."
        )
        console.print(f"[bold red]{error_msg}[/bold red]")
        raise ValueError(error_msg) # Re-raise as ValueError for config issue
    
    # 2. No legacy scripts directory is required; optional custom logic is loaded by explicit config paths.

    # 3. Construct Artifacts DataFrame and Validate Required Files
    artifacts_data = []
    missing_files_for_session = []

    # Define all expected artifacts and their paths
    expected_artifacts = {
        "Raw Data": coord.raw_dataset_path,
        "Cleaned Data": coord.clean_dataset_output_path,
        "User Cleaned Data": coord.user_cleaned_dataset_path,
        "Tagged Entities (DD)": coord.data_dictionary_csv_path,
        "Cleaning Recommendations Report": coord.cleaner_narrative_directory / "cleaning_recommendations.md",
        "Profiling Report": coord.profiling_report_path,
        "Handshake File": coord.handshake_path,
        "Quarantine File": coord.quarantine_path,
        "Metadata Authority": coord.metadata_table_path
    }

    for name, path in expected_artifacts.items():
        exists = path.exists()
        artifacts_data.append({
            "Artifact Name": name,
            "File Name": path.name,
            "Location": str(path.relative_to(coord.working_dir)) if path.is_relative_to(coord.working_dir) else str(path),
            "Exists": exists
        })
        # Check for mandatory files for a successful session
        if name in ["Raw Data", "Tagged Entities (DD)"] and not exists:
            missing_files_for_session.append(f"- {name} at {path}")

    artifacts_df = pd.DataFrame(artifacts_data)

    if missing_files_for_session:
        error_msg = (
            "❌ Missing required output files from 'classify-entities' or 'clean-dataset --action full':\n"
            f"{'\\n'.join(missing_files_for_session)}\n"
            "\n👉 Please ensure you have run 'classify-entities' and 'clean-dataset --action full' successfully."
        )
        console.print(f"[bold red]{error_msg}[/bold red]")
        raise FileNotFoundError(error_msg)

    console.print(f"[bold green]✅ Notebook session initialized for workspace:[/bold green] [cyan]{target_path}[/cyan]")
    console.print("\n[bold blue]Available Artifacts:[/bold blue]")
    console.print(artifacts_df)

    return coord, artifacts_df

# Convenience methods
def get_raw_data(coord: PathCoordinator) -> pd.DataFrame:
    """Loads the raw dataset into a Pandas DataFrame."""
    path = coord.raw_dataset_path
    if not path.exists():
        raise FileNotFoundError(f"Raw dataset not found at {path}")
    return pd.read_csv(path)

def get_cleaned_data(coord: PathCoordinator) -> pd.DataFrame:
    """Loads the cleaned dataset into a Pandas DataFrame."""
    path = coord.clean_dataset_output_path
    if not path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found at {path}")
    return pd.read_csv(path)

def get_tagged_entities(coord: PathCoordinator) -> pd.DataFrame:
    """Loads the tagged entities (processed Data Dictionary) into a Pandas DataFrame."""
    path = coord.data_dictionary_csv_path
    if not path.exists():
        raise FileNotFoundError(f"Tagged entities (Data Dictionary) not found at {path}")
    return pd.read_csv(path)

def get_quarantined_data(coord: PathCoordinator) -> pd.DataFrame:
    """Loads the quarantined data into a Pandas DataFrame."""
    path = coord.quarantine_path
    if not path.exists():
        console.print(f"[bold yellow]⚠️ Warning:[/bold yellow] Quarantine file not found at [cyan]{path}[/cyan]. Returning empty DataFrame.")
        return pd.DataFrame()
    return pd.read_csv(path)

def get_attributes_by_tag(coord: PathCoordinator, tag_name: str) -> List[str]:
    """
    Discovery API: Retrieves attributes matching a specific semantic tag.
    Example: 'geographic', 'pii', etc.
    """
    profile_json = coord.profiling_report_path.with_suffix(".json")
    assistant = CleaningAssistant(
        config=coord.config, 
        profile_path=profile_json, 
        dd_path=coord.data_dictionary_csv_path
    )
    return assistant.get_attributes_by_tag(tag_name)

def get_attributes_by_entity(coord: PathCoordinator, entity_name: str) -> List[str]:
    """
    Discovery API: Retrieves attributes assigned to a specific business entity concept.
    """
    profile_json = coord.profiling_report_path.with_suffix(".json")
    assistant = CleaningAssistant(
        config=coord.config, 
        profile_path=profile_json, 
        dd_path=coord.data_dictionary_csv_path
    )
    return assistant.get_attributes_by_entity(entity_name)

def get_metadata_table(coord: PathCoordinator) -> pd.DataFrame:
    """
    Retrieves the authoritative metadata table (Expert Overrides).

    Validation:
    1. Returns existing Metadata Table if it exists, enriched with the current bootstrap config.
    2. If not, checks if the Cleaner has run (verifies Synchronized Dictionary).
    3. Bootstraps from the Cleaner's synchronized AI baseline.
    """
    auth_path = coord.metadata_table_path
    if auth_path.exists():
        df = pd.read_csv(auth_path)
        return _enrich_with_bootstrap_metadata(df, coord)

    # Check if cleaner conclusion artifacts exist
    sync_path = coord.synchronized_dictionary_path
    if not sync_path.exists():
        raise FileNotFoundError(
            "❌ Error: The Cleaner has not established a baseline yet.\n"
            "👉 Please run 'clean-dataset --action full' before attempting to set metadata authority."
        )

    logger.info(f"Bootstrapping metadata authority from cleaner baseline: {sync_path.name}")
    df = pd.read_csv(sync_path)
    return _enrich_with_bootstrap_metadata(df, coord)


def get_dataset_metadata(coord: PathCoordinator) -> dict:
    """Returns dataset-level metadata from the active config or saved dataset metadata artifact."""
    if coord.dataset_metadata_path.exists():
        with open(coord.dataset_metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return _extract_dataset_metadata(coord)


def _extract_dataset_metadata(coord: PathCoordinator) -> dict:
    return {
        "dataset_type": coord.config.get("dataset_type"),
        "subject": coord.config.get("subject"),
        "subject_id_attribute": coord.config.get("cleaner", {}).get("structural_assessment", {}).get("subject_id_attribute"),
        "wide_short_homogeneous": coord.config.get("parser", {}).get("wide_short_homogeneous", False),
        "wide_short_representative_column": coord.config.get("parser", {}).get("wide_short_representative_column"),
        "graph_type": coord.config.get("graph_type"),
        "notes": coord.config.get("notes"),
        "use_case_answers": coord.config.get("use_case_answers") or {},
    }


def _flatten_dataset_metadata(metadata: dict) -> dict:
    flattened = {
        "dataset_type": metadata.get("dataset_type"),
        "subject": metadata.get("subject"),
        "subject_id_attribute": metadata.get("subject_id_attribute"),
        "wide_short_homogeneous": metadata.get("wide_short_homogeneous", False),
        "wide_short_representative_column": metadata.get("wide_short_representative_column"),
        "graph_type": metadata.get("graph_type"),
        "notes": metadata.get("notes"),
    }
    return flattened


def _enrich_with_bootstrap_metadata(df: pd.DataFrame, coord: PathCoordinator) -> pd.DataFrame:
    """Enriches metadata tables with dataset bootstrap metadata from the active config."""
    metadata_values = _flatten_dataset_metadata(_extract_dataset_metadata(coord))
    for col, val in metadata_values.items():
        if col not in df.columns:
            df[col] = val
        else:
            df[col] = df[col].fillna(val)
    return df


def save_dataset_metadata(coord: PathCoordinator, metadata: dict) -> None:
    """Persist dataset-level metadata as a separate artifact."""
    path = coord.dataset_metadata_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Dataset metadata saved to: {path}")

def save_metadata_table(coord: PathCoordinator, df: pd.DataFrame):
    """
    Persists the metadata table as the new Authority.
    Enforces 'Raw Data Verification' (Golden Rule) to prevent schema drift.
    """
    # 1. Verify against Raw Data headers (The ground truth)
    raw_headers = pd.read_csv(coord.raw_dataset_path, nrows=0).columns.tolist()
    
    # 🎯 COLUMN RESOLUTION: Prefer standardized 'attribute_name' for processed metadata
    attr_col = "attribute_name" if "attribute_name" in df.columns else coord.data_dictionary_attribute_col_name
    table_attrs = df[attr_col].unique().tolist()
    invalid_attrs = [a for a in table_attrs if a not in raw_headers]
    
    if invalid_attrs:
        raise ValueError(f"❌ Schema Drift Detected! Attributes in metadata not in raw data: {invalid_attrs}")

    # 2. Enrich with dataset-level metadata from the active config.
    metadata_values = {
        "dataset_type": coord.config.get("dataset_type"),
        "subject": coord.config.get("subject"),
        "subject_id_attribute": coord.config.get("cleaner", {}).get("structural_assessment", {}).get("subject_id_attribute"),
        "wide_short_homogeneous": coord.config.get("parser", {}).get("wide_short_homogeneous", False),
        "wide_short_representative_column": coord.config.get("parser", {}).get("wide_short_representative_column"),
        "graph_type": coord.config.get("graph_type"),
        "notes": coord.config.get("notes"),
    }
    use_case_answers = coord.config.get("use_case_answers") or {}
    metadata_values["use_case_answer_use_case"] = use_case_answers.get("use_case")
    metadata_values["use_case_answer_analysis_objective"] = use_case_answers.get("analysis_objective")
    for col, val in metadata_values.items():
        if col not in df.columns:
            df[col] = val

    # 3. Persist to data/dd_cleaner (The analytical destination)
    path = coord.metadata_table_path
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"✅ Metadata Authority (Expert Overrides) saved to: {path}")

def save_user_cleaned_data(coord: PathCoordinator, df: pd.DataFrame):
    """
    Persists the user-processed dataset to the configured output path.
    """
    path = coord.user_cleaned_dataset_path
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"✅ User-cleaned dataset saved to: {path}")


