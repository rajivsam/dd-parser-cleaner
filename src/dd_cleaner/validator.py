"""Universal validation engine driven by domain-specific Policy Manifests."""

import logging
import pandas as pd
from typing import Dict, Any, List, Tuple

class UniversalValidator:
    """
    Executes validation logic defined in external JSON manifests.
    Supports dynamic operators and configurable actions (flag vs quarantine).
    """

    def __init__(self, policy_manifest: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.manifest = policy_manifest or {}
        self.rules = self.manifest.get("validation_rules", [])
        
        # Map schema operators to pandas/python logic
        self._operators = {
            "gt": lambda s, v: s > v,
            "lt": lambda s, v: s < v,
            "ge": lambda s, v: s >= v,
            "le": lambda s, v: s <= v,
            "eq": lambda s, v: s == v,
            "ne": lambda s, v: s != v,
            "in": lambda s, v: s.isin(v if isinstance(v, list) else [v]),
            "between": lambda s, v: s.between(v[0], v[1]) if (isinstance(v, list) and len(v) == 2) else s
        }

    def execute_validation(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[int]]:
        """
        Applies all manifest rules to the dataframe.
        Returns the modified dataframe (with flags) and a list of indices to quarantine.
        """
        if not self.rules:
            self.logger.info("No validation rules found in manifest. Skipping.")
            return df, []

        quarantine_indices = set()
        df_out = df.copy()

        for rule in self.rules:
            attr = rule.get("attribute")
            op_key = rule.get("operator")
            val = rule.get("value")
            action = rule.get("action", "flag_warning")
            rule_id = rule.get("rule_id", "unknown_rule")

            if attr not in df_out.columns:
                self.logger.debug(f"Attribute '{attr}' for rule '{rule_id}' not in dataset. Skipping.")
                continue

            if op_key not in self._operators:
                self.logger.warning(f"Unsupported operator '{op_key}' in rule '{rule_id}'.")
                continue

            # Apply operator logic to create a mask of VIOLATIONS
            # Note: The manifest defines what is VALID or what the threshold is. 
            # Here we identify rows that FAIL the criteria.
            try:
                # Convert column to numeric if the rule value is numeric for safe comparison
                series = df_out[attr]
                if isinstance(val, (int, float)):
                    series = pd.to_numeric(series, errors='coerce')

                # We generate a mask where the condition is NOT met (the violation)
                # Example: if rule is 'le 350000', violation is 'series > 350000'
                is_valid = self._operators[op_key](series, val)
                violations = df_out[~is_valid & series.notna()]

                if not violations.empty:
                    self.logger.info(f"🚩 Rule '{rule_id}': Found {len(violations)} violations on '{attr}'. Action: {action}")
                    
                    if action == "quarantine":
                        quarantine_indices.update(violations.index.tolist())
                    elif action == "flag_warning":
                        df_out[f"warn_{rule_id}"] = ~is_valid
            
            except Exception as e:
                self.logger.error(f"Failed to execute rule '{rule_id}': {e}")

        return df_out, sorted(list(quarantine_indices))