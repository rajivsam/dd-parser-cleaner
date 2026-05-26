import pytest
import pandas as pd
from path_coordinator import PathCoordinator
from dd_parser.structural_assessor import StructuralAssessor

def test_structural_assessor_constants(managed_test_config):
    """Verify detection of columns with zero variance."""
    coordinator = PathCoordinator(config_path=managed_test_config)
    assessor = StructuralAssessor(coordinator.config)
    df = pd.DataFrame({
        "const_val": ["A", "A", "A"],
        "const_null": [None, None, None],
        "varied": ["A", "B", "A"]
    })
    report = assessor.assess(df)
    
    assert "const_val" in report["constant_columns"]
    assert "const_null" in report["constant_columns"]
    assert "varied" not in report["constant_columns"]

def test_structural_assessor_null_threshold(managed_test_config):
    """Verify detection of sparse columns based on config threshold."""
    coordinator = PathCoordinator(config_path=managed_test_config)
    assessor = StructuralAssessor(coordinator.config)
    # Override threshold for testing: 50%
    assessor.null_threshold = 0.5
    
    df = pd.DataFrame({
        "healthy": [1, 2, None, 4],    # 25% null
        "sparse": [1, None, None, None] # 75% null
    })
    report = assessor.assess(df)
    
    assert "healthy" not in report["sparse_columns"]
    assert "sparse" in report["sparse_columns"]
    assert report["sparse_columns"]["sparse"] == 0.75

def test_structural_assessor_pk_validation(managed_test_config):
    """Verify primary key integrity checks (uniqueness and nullability)."""
    coordinator = PathCoordinator(config_path=managed_test_config)
    assessor = StructuralAssessor(coordinator.config)
    
    # Case 1: Duplicate PKs
    df_dup = pd.DataFrame({"pk": [1, 1, 2], "data": [10, 20, 30]})
    report_dup = assessor.assess(df_dup, primary_keys=["pk"])
    assert report_dup["pk_validation"]["is_valid"] is False
    
    # Case 2: Null in PK
    df_null = pd.DataFrame({"pk": [1, None, 3], "data": [10, 20, 30]})
    report_null = assessor.assess(df_null, primary_keys=["pk"])
    assert report_null["pk_validation"]["is_valid"] is False

    # Case 3: Valid PK
    df_valid = pd.DataFrame({"pk": [1, 2, 3], "data": [10, 20, 30]})
    report_valid = assessor.assess(df_valid, primary_keys=["pk"])
    assert report_valid["pk_validation"]["is_valid"] is True

def test_structural_assessor_exclusions(managed_test_config):
    """Verify that excluded columns are filtered out of recommendations."""
    coordinator = PathCoordinator(config_path=managed_test_config)
    assessor = StructuralAssessor(coordinator.config)
    df = pd.DataFrame({
        "const": ["A", "A", "A"],
        "sparse": [1, None, None, None]
    })
    assessor.null_threshold = 0.5
    
    # Case: Exclude the problematic columns
    report = assessor.assess(df, exclude_cols=["const", "sparse"])
    assert "const" not in report["constant_columns"]
    assert "sparse" not in report["sparse_columns"]
    assert len(report["recommendations"]) == 0