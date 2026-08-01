import pytest
import pandas as pd
import yaml
from pathlib import Path
from shutil import copyfile
from dd_common.path_coordinator import PathCoordinator
from dd_cleaner.orchestrator import CleanerOrchestrator
from dd_cleaner.notebook_utils import get_dataset_metadata, get_metadata_table, save_metadata_table

def test_metadata_authority_lifecycle(managed_test_config):
    """
    Tests the sequence: Run Cleaner -> Load Baseline -> Expert Override -> Save Authority.
    """
    coord = PathCoordinator(config_path=managed_test_config)
    
    # 1. Setup: Ensure we have a clean slate for the authority file
    if coord.metadata_table_path.exists():
        coord.metadata_table_path.unlink()

    # 2. Execution: Run the cleaner to establish the 'Clean Bucket'
    # This generates 'synchronized_dictionary.csv' and the clean dataset.
    orch = CleanerOrchestrator(coord)
    orch.run_pipeline(action="full")
    
    assert coord.synchronized_dictionary_path.exists(), "Cleaner failed to produce synchronized baseline"

    # 3. Discovery: Notebook loads the metadata (bootstraps from Synchronized Dictionary)
    df_metadata = get_metadata_table(coord)
    assert not df_metadata.empty
    assert "dataset_type" in df_metadata.columns
    assert df_metadata["dataset_type"].iloc[0] == coord.config["dataset_type"]
    assert "wide_short_homogeneous" in df_metadata.columns
    assert df_metadata["wide_short_homogeneous"].iloc[0] == coord.config.get("parser", {}).get("wide_short_homogeneous", False)
    
    # 4. Action: Expert overrides a logical type
    # Standardized header used by parser/cleaner output
    attr_col = "attribute_name" if "attribute_name" in df_metadata.columns else coord.data_dictionary_attribute_col_name
    target_attr = df_metadata.iloc[0][attr_col]
    df_metadata.loc[df_metadata[attr_col] == target_attr, "logical_type"] = "expert_override"
    
    # 5. Persistence: Save the expert authority
    save_metadata_table(coord, df_metadata)
    assert coord.metadata_table_path.exists()

    # 6. Verification: Reload and ensure it is authoritative
    df_reloaded = get_metadata_table(coord)
    val = df_reloaded[df_reloaded[attr_col] == target_attr]["logical_type"].values[0]
    assert val == "expert_override"


def test_dataset_metadata_artifact_is_saved_and_loaded(managed_test_config):
    coord = PathCoordinator(config_path=managed_test_config)
    if coord.dataset_metadata_path.exists():
        coord.dataset_metadata_path.unlink()

    orch = CleanerOrchestrator(coord)
    orch.run_pipeline(action="full")

    assert coord.dataset_metadata_path.exists()
    dataset_metadata = get_dataset_metadata(coord)
    assert dataset_metadata["dataset_type"] == coord.config["dataset_type"]
    assert dataset_metadata["subject"] == coord.config.get("subject")
    assert dataset_metadata["use_case_answers"] == coord.config.get("use_case_answers", {})


def test_metadata_fails_if_cleaner_not_run(managed_test_config):
    """
    Ensures we cannot get or bootstrap metadata if the cleaner hasn't established a baseline.
    """
    coord = PathCoordinator(config_path=managed_test_config)
    
    # Manually remove artifacts to simulate 'pre-cleaner' state
    if coord.metadata_table_path.exists(): coord.metadata_table_path.unlink()
    if coord.synchronized_dictionary_path.exists(): coord.synchronized_dictionary_path.unlink()
    
    # Attempting to get metadata should now fail
    with pytest.raises(FileNotFoundError, match="Cleaner has not established a baseline"):
        get_metadata_table(coord)


def test_init_notebook_session_uses_explicit_config_path(tmp_path):
    """Verify the notebook session can initialize with an arbitrary config file path."""
    from dd_cleaner.notebook_utils import init_notebook_session

    workspace_dir = tmp_path
    for folder in ["data", "data_dictionary", "documents", "notebooks", "models"]:
        (workspace_dir / folder).mkdir(parents=True, exist_ok=True)

    config_path = tmp_path / "olist_config.yaml"
    config_payload = {
        "working_dir": str(workspace_dir),
        "dataset_id": "olist_test",
        "documents_dir": "documents",
        "parser": {
            "data_dictionary_file": "olist_example_dd.csv",
            "data_dictionary_attribute_col_name": "attribute",
            "dd_parser_output_dir": "dd_analysis_results",
            "output_filename": "olist_analysis_results.csv",
            "entity_tagging": [],
            "wide_short_homogeneous": True,
            "wide_short_representative_column": "woy",
        },
        "cleaner": {
            "raw_dataset_file": "olist.csv",
            "clean_output_filename": "olist_clean.csv",
            "metadata_table_filename": "olist_metadata_table.csv",
            "user_cleaned_output_filename": "olist_user_cleaned.csv",
            "dd_cleaner_output_dir": "dd_cleaner",
            "handshake_file": "olist_parser_cleaner_handshake.md",
            "profiling_report_filename": "olist_profiling_report.md",
            "quarantine_dir": "quarantine",
            "quarantine_filename": "olist_quarantine.csv",
            "structural_assessment": {
                "dataset_type": "cross-sectional",
                "null_threshold": 0.95,
            },
        },
    }
    config_path.write_text(yaml.safe_dump(config_payload), encoding="utf-8")

    # Use actual repository sample files so notebook init exercise mirrors real state.
    sample_root = Path(__file__).resolve().parent
    raw_data_src = sample_root / "data" / "SP_2017_weekly_product_revenue_by_product_id.csv"
    dict_src = sample_root / "data_dictionary" / "olist_example_dd.csv"

    raw_data_dest = workspace_dir / "data" / config_payload["cleaner"]["raw_dataset_file"]
    tagged_entities_dir = workspace_dir / "documents" / config_payload["parser"]["dd_parser_output_dir"]
    tagged_entities_dir.mkdir(parents=True, exist_ok=True)
    tagged_entities_dest = tagged_entities_dir / config_payload["parser"]["output_filename"]

    copyfile(raw_data_src, raw_data_dest)
    copyfile(dict_src, tagged_entities_dest)

    coord, artifacts = init_notebook_session(str(workspace_dir), config_path=str(config_path))

    assert coord.config["dataset_id"] == "olist_test"
    assert coord.config["parser"]["wide_short_homogeneous"] is True
    assert coord.working_dir == workspace_dir.resolve()
    assert "Raw Data" in artifacts["Artifact Name"].tolist()