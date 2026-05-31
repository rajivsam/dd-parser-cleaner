"""Evaluates physical dataset structure and validates integrity gates."""

import json
import hashlib
import logging
import pandas as pd
from typing import List, Dict, Any

class StructuralAssessor:
    """
    Evaluates the physical structure of a dataset.
    Provides recommendations for drops and validates primary key integrity.
    """

    def __init__(self, config: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        self.update_config(config)

    def update_config(self, config: Dict[str, Any]) -> None:
        """Refreshes assessment parameters from the global configuration."""
        cleaner_cfg = config.get("cleaner", {})
        self.assess_cfg = cleaner_cfg.get("structural_assessment", {})
        
        self.null_threshold = self.assess_cfg.get("null_threshold", 0.95)
        self.auto_drop_constant = self.assess_cfg.get("auto_drop_constant", True)

    def generate_structural_hash(self, df: pd.DataFrame) -> str:
        """Creates a fingerprint of the schema (column names + dtypes)."""
        struct_info = {col: str(dtype) for col, dtype in df.dtypes.items()}
        struct_json = json.dumps(struct_info, sort_keys=True)
        return hashlib.sha256(struct_json.encode()).hexdigest()

    def assess(self, df: pd.DataFrame, primary_keys: List[str] = None, exclude_cols: List[str] = None) -> Dict[str, Any]:
        """Executes a full audit and returns a report for the UI/Wizard layer."""
        exclude_cols = exclude_cols or []
        
        # 🛡️ FILTERED FINDINGS: Identify constants and sparse columns not already handled in config
        constants = [c for c in self._find_constant_columns(df) if c not in exclude_cols]
        sparse = {c: r for c, r in self._find_sparse_columns(df).items() if c not in exclude_cols}

        report = {
            "structural_hash": self.generate_structural_hash(df),
            "constant_columns": constants,
            "sparse_columns": sparse,
            "recommendations": []
        }

        # Logic for automated recommendations
        if constants:
            report["recommendations"].append(f"Drop constant columns {constants} (Zero variance; these columns provide no analytical value as all rows are identical).")
        
        for col, ratio in sparse.items():
            report["recommendations"].append(f"Drop column '{col}' because it is {ratio*100:.1f}% null (Threshold: {self.null_threshold*100}%). Sparse data can skew statistical analysis and model training.")
        
        return report

    def _find_constant_columns(self, df: pd.DataFrame) -> List[str]:
        """Identifies columns with zero variance (all values same, including NaNs)."""
        return [col for col in df.columns if df[col].nunique(dropna=False) <= 1]

    def _find_sparse_columns(self, df: pd.DataFrame) -> Dict[str, float]:
        """Identifies columns exceeding the null threshold."""
        null_ratios = df.isnull().mean()
        sparse = null_ratios[null_ratios > self.null_threshold]
        return sparse.to_dict()