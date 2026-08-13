import json
import shutil
from pathlib import Path

import pandas as pd
import pytest
import yaml
from dd_common.path_coordinator import PathCoordinator
from dd_parser.post_processor import MetadataPostProcessor


def _make_config(config_path: Path, dataset_type: str = "cross-sectional") -> None:
    config = {
        "working_dir": str(config_path.parent),
        "documents_dir": "documents",
        "dataset_type": dataset_type,
        "parser": {
            "data_dictionary_file": "sba_dd.csv",
            "data_dictionary_attribute_col_name": "Field Name",
            "dd_parser_output_dir": "dd_analysis_results",
            "output_filename": "sba_loans_raw_analysis_results.csv",
            "dataset_manifest_filename": "sba_loans_raw_dataset_manifest.json",
            "attribute_manifest_filename": "sba_loans_raw_attribute_manifest.json",
            "entity_tagging": [],
        },
        "cleaner": {
            "raw_dataset_file": "sba_loans_raw.csv",
            "clean_output_filename": "sba_loans_raw_clean.csv",
            "metadata_table_filename": "sba_loans_metadata_table.csv",
            "user_cleaned_output_filename": "sba_loans_raw_user_cleaned.csv",
            "dd_cleaner_output_dir": "dd_cleaner",
            "handshake_file": "sba_parser_cleaner_handshake.md",
            "profiling_report_filename": "sba_loans_raw_profiling_report.md",
            "quarantine_dir": "quarantine",
            "quarantine_filename": "sba_loans_raw_quarantine.csv",
        },
    }
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")


@pytest.fixture
def processor(tmp_path):
    config_path = tmp_path / "config.yaml"
    _make_config(config_path, dataset_type="cross-sectional")
    coordinator = PathCoordinator(config_path=str(config_path))
    return MetadataPostProcessor(coordinator, coordinator.config["parser"])


def test_cross_sectional_execute_leaves_static_dynamic_none(processor):
    df = pd.DataFrame(
        {
            "attribute_name": ["loan_id", "amount", "created_date"],
            "provisional_entity_assignment": ["unassigned"] * 3,
            "static_dynamic": ["static"] * 3,
            "logical_type": ["numeric", "numeric", "datetime"],
            "physical_type": ["int", "float", "datetime"],
        }
    )
    attributes = pd.Series(["loan_id", "amount", "created_date"])
    descriptions = pd.Series(["Loan identifier", "Loan amount", "Created timestamp"])
    llm_assignments = {
        "loan_id": {"entity_assignment": "subject", "static_dynamic": "static"},
        "amount": {"entity_assignment": "feature", "static_dynamic": "dynamic"},
        "created_date": {"entity_assignment": "time_key", "static_dynamic": "dynamic"},
    }

    result = processor.execute(
        df,
        attributes,
        descriptions,
        llm_assignments,
        grounding_profile=None,
        df_raw_sample=None,
        dataset_type="cross-sectional",
        bridge_report=None,
        use_case_answers=None,
    )

    assert "static_dynamic" in result.columns
    assert result["static_dynamic"].tolist() == ["none", "none", "none"]


def test_cross_sectional_report_omits_static_dynamic_column(tmp_path):
    config_path = tmp_path / "config.yaml"
    _make_config(config_path, dataset_type="cross-sectional")
    coordinator = PathCoordinator(config_path=str(config_path))
    processor = MetadataPostProcessor(coordinator, coordinator.config["parser"])

    df = pd.DataFrame(
        {
            "attribute_name": ["loan_id", "amount"],
            "provisional_entity_assignment": ["unassigned", "unassigned"],
            "static_dynamic": ["none", "none"],
            "logical_type": ["numeric", "numeric"],
            "physical_type": ["int", "float"],
        }
    )

    processor._write_provisional_report(df, dataset_type="cross-sectional")
    report_text = (coordinator.parser_provisional_report_path).read_text(encoding="utf-8")

    assert "Static/Dynamic" not in report_text
    assert "Attribute" in report_text
    assert "Assignment" in report_text


def test_panel_report_includes_static_dynamic_column(tmp_path):
    config_path = tmp_path / "config.yaml"
    _make_config(config_path, dataset_type="panel")
    coordinator = PathCoordinator(config_path=str(config_path))
    processor = MetadataPostProcessor(coordinator, coordinator.config["parser"])

    df = pd.DataFrame(
        {
            "attribute_name": ["loan_id", "amount"],
            "provisional_entity_assignment": ["unassigned", "unassigned"],
            "static_dynamic": ["static", "dynamic"],
            "logical_type": ["numeric", "numeric"],
            "physical_type": ["int", "float"],
        }
    )

    processor._write_provisional_report(df, dataset_type="panel")
    report_text = (coordinator.parser_provisional_report_path).read_text(encoding="utf-8")

    assert "Static/Dynamic" in report_text
    assert "dynamic" in report_text


def test_wide_short_homogeneous_manifest_detection(tmp_path):
    config_path = tmp_path / "config.yaml"
    config = {
        "working_dir": str(tmp_path),
        "documents_dir": "documents",
        "dataset_type": "cross-sectional",
        "dataset_id": "sp_2017_weekly_product_revenue_by_product_id",
        "parser": {
            "data_dictionary_file": "olist_example_dd.csv",
            "data_dictionary_attribute_col_name": "attribute",
            "csv_target_column_index": 0,
            "dd_parser_output_dir": "dd_analysis_results",
            "output_filename": "sp_2017_weekly_product_revenue_by_product_id_analysis_results.csv",
            "dataset_manifest_filename": "sp_2017_weekly_dataset_manifest.json",
            "attribute_manifest_filename": "sp_2017_weekly_attribute_manifest.json",
            "entity_tagging": [],
        },
        "cleaner": {
            "raw_dataset_file": "SP_2017_weekly_product_revenue_by_product_id.csv",
            "clean_output_filename": "sp_2017_weekly_clean.csv",
            "metadata_table_filename": "sp_2017_weekly_metadata_table.csv",
            "user_cleaned_output_filename": "sp_2017_weekly_user_cleaned.csv",
            "dd_cleaner_output_dir": "dd_cleaner",
            "handshake_file": "sp_2017_weekly_parser_cleaner_handshake.md",
            "profiling_report_filename": "sp_2017_weekly_profiling_report.md",
            "quarantine_dir": "quarantine",
            "quarantine_filename": "sp_2017_weekly_quarantine.csv",
            "structural_assessment": {
                "dataset_type": "cross-sectional",
                "subject_id_attribute": None,
                "null_threshold": 0.95,
            },
        },
    }
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    (tmp_path / "documents").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data_dictionary").mkdir(parents=True, exist_ok=True)

    source_raw = Path(__file__).resolve().parent / "data" / "SP_2017_weekly_product_revenue_by_product_id.csv"
    source_dd = Path(__file__).resolve().parent / "data_dictionary" / "olist_example_dd.csv"
    shutil.copy(source_raw, tmp_path / "data" / source_raw.name)
    shutil.copy(source_dd, tmp_path / "data_dictionary" / source_dd.name)

    coordinator = PathCoordinator(config_path=str(config_path))
    processor = MetadataPostProcessor(coordinator, coordinator.config["parser"])

    df_dict = pd.read_csv(tmp_path / "data_dictionary" / "olist_example_dd.csv")
    df_raw_sample = pd.read_csv(tmp_path / "data" / "SP_2017_weekly_product_revenue_by_product_id.csv", nrows=100)
    df_synced = processor.synchronize_with_raw_headers(df_dict, df_raw_sample)

    manifest = processor._build_dataset_manifest(df_synced, "cross-sectional", use_case_answers={})

    assert manifest["notes_structure"] == "wide_short_homogeneous"
    assert manifest["flags"]["skip_columnwise_intelligence"] is True
    assert manifest["wide_short_group"]["representative_column"] != "woy"
    assert manifest["wide_short_group"]["count_columns"] == len(df_synced) - 1
    assert isinstance(manifest["wide_short_group"]["group_name"], str)


def test_wide_short_config_drives_manifest_construction(tmp_path):
    config_path = tmp_path / "config.yaml"
    config = {
        "working_dir": str(tmp_path),
        "documents_dir": "documents",
        "dataset_type": "cross-sectional",
        "dataset_id": "sp_2017_weekly_product_revenue_by_product_id",
        "parser": {
            "data_dictionary_file": "olist_example_dd.csv",
            "data_dictionary_attribute_col_name": "attribute",
            "csv_target_column_index": 0,
            "dd_parser_output_dir": "dd_analysis_results",
            "output_filename": "sp_2017_weekly_product_revenue_by_product_id_analysis_results.csv",
            "dataset_manifest_filename": "sp_2017_weekly_dataset_manifest.json",
            "attribute_manifest_filename": "sp_2017_weekly_attribute_manifest.json",
            "entity_tagging": [],
            "wide_short_homogeneous": True,
            "wide_short_representative_column": "woy",
        },
        "cleaner": {
            "raw_dataset_file": "SP_2017_weekly_product_revenue_by_product_id.csv",
            "clean_output_filename": "sp_2017_weekly_clean.csv",
            "metadata_table_filename": "sp_2017_weekly_metadata_table.csv",
            "user_cleaned_output_filename": "sp_2017_weekly_user_cleaned.csv",
            "dd_cleaner_output_dir": "dd_cleaner",
            "handshake_file": "sp_2017_weekly_parser_cleaner_handshake.md",
            "profiling_report_filename": "sp_2017_weekly_profiling_report.md",
            "quarantine_dir": "quarantine",
            "quarantine_filename": "sp_2017_weekly_quarantine.csv",
            "structural_assessment": {
                "dataset_type": "cross-sectional",
                "subject_id_attribute": None,
                "null_threshold": 0.95,
            },
        },
    }
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    (tmp_path / "documents").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data_dictionary").mkdir(parents=True, exist_ok=True)

    source_raw = Path(__file__).resolve().parent / "data" / "SP_2017_weekly_product_revenue_by_product_id.csv"
    source_dd = Path(__file__).resolve().parent / "data_dictionary" / "olist_example_dd.csv"
    shutil.copy(source_raw, tmp_path / "data" / source_raw.name)
    shutil.copy(source_dd, tmp_path / "data_dictionary" / source_dd.name)

    coordinator = PathCoordinator(config_path=str(config_path))
    processor = MetadataPostProcessor(coordinator, coordinator.config["parser"])

    df_dict = pd.read_csv(tmp_path / "data_dictionary" / "olist_example_dd.csv")
    df_raw_sample = pd.read_csv(tmp_path / "data" / "SP_2017_weekly_product_revenue_by_product_id.csv", nrows=100)
    df_synced = processor.synchronize_with_raw_headers(df_dict, df_raw_sample)

    manifest = processor._build_dataset_manifest(df_synced, "cross-sectional", use_case_answers={})

    assert manifest["notes_structure"] == "wide_short_homogeneous"
    assert manifest["wide_short_group"]["representative_column"] == "woy"
    assert manifest["flags"]["skip_columnwise_intelligence"] is True
    assert manifest["wide_short_group"]["count_columns"] == len(df_synced) - 1


def test_wide_short_heuristic_requires_a_shared_repeated_prefix(tmp_path):
    config_path = tmp_path / "config.yaml"
    config = {
        "working_dir": str(tmp_path),
        "documents_dir": "documents",
        "dataset_type": "cross-sectional",
        "parser": {
            "data_dictionary_file": "sample_dd.csv",
            "data_dictionary_attribute_col_name": "attribute",
            "entity_tagging": [],
        },
        "cleaner": {
            "raw_dataset_file": "sample.csv",
            "clean_output_filename": "sample_clean.csv",
            "metadata_table_filename": "sample_metadata_table.csv",
            "user_cleaned_output_filename": "sample_user_cleaned.csv",
            "dd_cleaner_output_dir": "dd_cleaner",
            "handshake_file": "sample_parser_cleaner_handshake.md",
            "profiling_report_filename": "sample_profiling_report.md",
            "quarantine_dir": "quarantine",
            "quarantine_filename": "sample_quarantine.csv",
        },
    }
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    df = pd.DataFrame({
        "attribute_name": ["woy"] + [f"metric_{idx}" for idx in range(1, 61)],
        "description": ["Week of year"] + [f"{suffix} value" for suffix in ["Sales", "Inventory", "Margin", "Returns"] * 15],
    })

    coordinator = PathCoordinator(config_path=str(config_path))
    processor = MetadataPostProcessor(coordinator, coordinator.config["parser"])
    result = processor._infer_wide_short_homogeneous_info(df)

    assert result == {}
