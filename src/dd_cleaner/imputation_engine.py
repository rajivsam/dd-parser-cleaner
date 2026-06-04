"""Core engine for resolving missing values via the Resolution Hierarchy."""

import logging
import pandas as pd
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional

class MissingValueHandler:
    """
    Executes imputation strategies based on the hierarchical resolution:
    1. Attribute Overrides (Specific columns)
    2. Logical Type Defaults (Data classes)
    3. System Fallback (NaN + Warning)

    Attributes:
        mv_cfg (dict): Missing value configuration block.
        workspace_root (Path): Base directory for custom script resolution.
    """

    def __init__(self, config: Dict[str, Any], workspace_root: Path):
        """
        Initializes the handler.

        Args:
            config (dict): Global configuration.
            workspace_root (Path): Base directory for script relative pathing.
        """
        self.logger = logging.getLogger(__name__)
        self.cleaner_cfg = config.get("cleaner", {})
        self.mv_cfg = self.cleaner_cfg.get("missing_values", {})
        self.workspace_root = workspace_root
        self._custom_module = self._load_custom_logic()

    def _load_custom_logic(self):
        """
        Dynamically loads the custom logic script.

        Returns:
            Module: The imported python module or None.
        """
        logic_path = self.cleaner_cfg.get("custom_logic_path")
        if not logic_path:
            return None
        
        full_path = (self.workspace_root / logic_path).resolve()
        if not full_path.exists():
            self.logger.warning(f"Custom logic path not found: {full_path}")
            return None

        spec = importlib.util.spec_from_file_location("custom_logic", full_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def resolve(self, df: pd.DataFrame, col: str, logical_type: str) -> pd.Series:
        """
        Resolves the cleaning action for a specific column via the hierarchy.

        Args:
            df (pd.DataFrame): The parent dataset.
            col (str): Target column name.
            logical_type (str): The semantically inferred type (e.g., numeric, categorical).

        Returns:
            pd.Series: The transformed data series.
        """
        # 1. Attribute Override
        strategy = self.mv_cfg.get("attribute_overrides", {}).get(col)
        
        # 2. Logical Type Default
        if not strategy:
            strategy = self.mv_cfg.get("logical_defaults", {}).get(logical_type)

        if not strategy:
            self.logger.debug(f"No strategy for {col} ({logical_type}). System fallback: NaN")
            return df[col]

        return self._execute_strategy(df, col, strategy)

    def _execute_strategy(self, df: pd.DataFrame, col: str, strategy: str) -> pd.Series:
        """
        Dispatches to built-in or custom transformation logic.

        Args:
            df (pd.DataFrame): Operational dataset.
            col (str): Target column.
            strategy (str): Strategy identifier.

        Returns:
            pd.Series: Imputed data series.
        """
        if strategy.startswith("custom:"):
            return self._dispatch_custom(df, col, strategy.replace("custom:", ""))
        
        # Built-in Logic
        if strategy == "mean-imputation":
            fill_val = df[col].mean()
            # 🧮 Type Safety: If the series is an integer type, we round the mean 
            # to prevent a silent cast to float during fillna.
            if pd.api.types.is_integer_dtype(df[col]) and not pd.isna(fill_val):
                fill_val = round(fill_val)
            return df[col].fillna(fill_val)
        elif strategy == "median-imputation":
            return df[col].fillna(df[col].median())
        elif strategy == "mode-imputation":
            return df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else None)
        elif strategy == "ffill":
            return df[col].ffill()
        elif strategy == "bfill":
            return df[col].bfill()
        elif strategy.startswith("constant:"):
            val = strategy.replace("constant:", "")
            # Try to cast to numeric if possible
            try: val = float(val) if '.' in val else int(val)
            except ValueError: pass
            return df[col].fillna(val)
        
        self.logger.warning(f"Unknown strategy '{strategy}' for column {col}")
        return df[col]

    def _dispatch_custom(self, df: pd.DataFrame, col: str, func_name: str) -> pd.Series:
        """
        Calls a custom Python function defined in domain_logic.py.

        Args:
            df (pd.DataFrame): Operational dataset.
            col (str): Target column.
            func_name (str): Function name in the script.

        Returns:
            pd.Series: Resulting series from the custom hook.
        """
        if not self._custom_module or not hasattr(self._custom_module, func_name):
            self.logger.error(f"Custom function {func_name} not found in logic script.")
            return df[col]
        
        try:
            func = getattr(self._custom_module, func_name)
            # Transform Contract: func(df, col) -> pd.Series
            result = func(df, col)
            if not isinstance(result, pd.Series):
                self.logger.error(f"Custom function {func_name} must return a pd.Series.")
                return df[col]
            return result
        except Exception as e:
            self.logger.error(f"Error in custom function {func_name}: {e}")
            raise e