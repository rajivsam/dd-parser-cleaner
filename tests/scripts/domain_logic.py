import pandas as pd
import numpy as np

def filter_active_health_universe(df: pd.DataFrame) -> pd.Index:
    """
    Filter Contract: Excludes administrative/integrity noise.
    Keeps records that are NOT in ['CANCLD', 'EXEMPT', 'COMMIT', 'pna'].
    """
    # Locate the status column (case-insensitive search for flexibility)
    status_col = next((c for c in df.columns if c.lower() == 'status'), None)
    
    if not status_col:
        return df.index
        
    noise = ['CANCLD', 'EXEMPT', 'COMMIT', 'pna']
    mask = ~df[status_col].astype(str).isin(noise)
    return df[mask].index

def derive_loan_distress_metric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derivation Contract: Adds a 3-tier ordinal distress score.
    0: Healthy, 1: Under Duress, 2: Written Off
    """
    status_col = next((c for c in df.columns if c.lower() == 'status'), 'status')
    
    if status_col not in df.columns:
        df['loan_distress_metric'] = 0
        return df
        
    s = df[status_col].astype(str).str.upper()
    conditions = [
        s.str.contains('CHGOFF|WRITEOFF', na=False),
        s.str.contains('PAID|CANCLD', na=False)
    ]
    choices = [2, 0]
    df['loan_distress_metric'] = np.select(conditions, choices, default=1)
    return df

def impute_categorical_missing(df: pd.DataFrame, col: str) -> pd.Series:
    """
    Vectorized handler to encode null values in a categorical column 
    as a specific 'MISSING' category string.
    """
    return df[col].fillna("MISSING")
