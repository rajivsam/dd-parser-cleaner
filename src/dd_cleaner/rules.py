"""Executes vectorized transformation and data scrubbing business rules."""

import pandas as pd
from typing import List, Set


class CleaningRulesEngine:
    """Applies title-casing and zero-padding rules defensively using dynamic prefixes."""

    def __init__(self, active_prefixes: List[str]) -> None:
        """Initializes the engine with dynamic domain entity prefixes."""
        self.active_prefixes = active_prefixes

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
            
            # Rule 2: Smart Zero-Padding on codes/ZIP/ID target fields
            if any(token in col_lower for token in ["zip", "id", "number", "code"]):
                pad_width = 5 if "zip" in col_lower else 0
                if pad_width > 0:
                    df_out[col] = series_str.str.zfill(pad_width)
                else:
                    df_out[col] = series_str
            
            # Rule 3: Dynamic or fallback string formatting title-casing
            elif is_domain_match or any(token in col_lower for token in ["name", "street", "city", "state"]):
                df_out[col] = series_str.str.title()
            
            else:
                df_out[col] = series_str

        return df_out
