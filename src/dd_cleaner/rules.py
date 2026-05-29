"""Executes vectorized transformation and data scrubbing business rules."""

import pandas as pd
from typing import List, Set, Dict, Any


class CleaningRulesEngine:
    """
    Applies transformation rules driven by the Policy Manifest.
    Eliminates hardcoded domain assumptions in favor of manifest-defined constants.
    """

    def __init__(self, active_prefixes: List[str], policy_manifest: Dict[str, Any] = None) -> None:
        """Initializes the engine with dynamic prefixes and the domain policy manifest."""
        self.active_prefixes = active_prefixes
        self.manifest = policy_manifest or {}
        
        # Extract formatting rules from manifest constants
        self.constants = self.manifest.get("constants", {})
        self.padding_rules = self.constants.get("FORMATTING_PADDING", {})  # e.g., {"zip": 5, "id": 10}
        self.title_case_tokens = self.constants.get("FORMATTING_TITLE_CASE", [])

    def identify_mixed_value_indices(self, df: pd.DataFrame) -> List[int]:
        """Identifies row indices containing values that deviate from the dominant type in their column."""
        quarantine_indices: Set[int] = set()
        
        for col in df.columns:
            # Isolate non-null values to determine the statistical dominant type
            non_null_series = df[col].dropna()
            if non_null_series.empty:
                continue
                
            # 🕵️ PANDAS INFERENCE: Leverage built-in type detection
            inferred = pd.api.types.infer_dtype(non_null_series)
            if "mixed" in inferred:
                dominant_type = non_null_series.map(type).value_counts().idxmax()
                # Collect indices where the value is present but its type is an outlier
                mixed_mask = df[col].apply(lambda x: x is not None and not pd.isna(x) and type(x) != dominant_type)
                quarantine_indices.update(df.index[mixed_mask].tolist())
                
        return sorted(list(quarantine_indices))

    def execute_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies zero-padding and vectorized title-casing to data cells defensively."""
        df_out = df.copy()
        
        for col in df_out.columns:
            col_lower = str(col).lower().strip()
            series_str = df_out[col].fillna("").astype(str).str.strip()
            
            # Rule 1: Match dynamically harvested domain entity prefix footprints
            is_domain_match = any(
                col_lower.startswith(prefix) or prefix in col_lower 
                for prefix in self.active_prefixes
            )
            
            # Rule 2: Manifest-Driven Zero-Padding
            # Instead of hardcoded 'zip' check, we look up tokens in the padding_rules map
            applied_padding = False
            for token, width in self.padding_rules.items():
                if token.lower() in col_lower:
                    df_out[col] = series_str.str.zfill(int(width))
                    applied_padding = True
                    break
            
            if applied_padding:
                continue
            
            # Rule 3: Dynamic or fallback string formatting title-casing
            # Uses tokens discovered/defined in the manifest (e.g., ['street', 'city', 'name'])
            should_title_case = is_domain_match or any(
                token.lower() in col_lower for token in self.title_case_tokens
            )
            
            if should_title_case:
                df_out[col] = series_str.str.title()
            else:
                df_out[col] = series_str

        return df_out
