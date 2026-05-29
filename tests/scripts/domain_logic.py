import pandas as pd
import numpy as np
from datetime import datetime

def handle_categorical_missing(df: pd.DataFrame, col: str) -> pd.Series:
    """
    Transform Contract: Encodes null values as 'MISSING' for categorical columns.
    
    Args:
        df (pd.DataFrame): The full dataframe context.
        col (str): The specific categorical column to process.
    """
    return df[col].fillna("Missing")

def datetime_to_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derivation Contract: Converts all datetime columns to numeric days since the Unix Epoch.
    Used for cross-sectional alignment where raw dates are replaced by temporal offsets.
    """
    baseline = pd.Timestamp("1970-01-01")
    date_cols = df.select_dtypes(include=['datetime64']).columns
    for col in date_cols:
        df[f"{col}_numeric"] = (df[col] - baseline).dt.days
    return df

def filter_active_health_universe(df: pd.DataFrame) -> pd.Index:
    """
    Row-Filter Contract: Defines the analytical universe for monitoring.
    Excludes: Administrative statuses (EXEMPT, CANCLD, COMMIT) and 
    integrity errors (disbursement after repayment).
    """
    status_upper = df["loanstatus"].astype(str).str.upper().str.strip()
    excluded_statuses = ["EXEMPT", "CANCLD", "COMMIT"]
    status_mask = status_upper.isin(excluded_statuses)

    # Integrity Gate: Only check if columns exist; if 100% null, mask will be False
    pna_mask = pd.Series([False] * len(df), index=df.index)
    if "firstdisbursementdate" in df.columns and "paidinfulldate" in df.columns:
        first_disb = pd.to_datetime(df["firstdisbursementdate"], errors='coerce')
        paid_full = pd.to_datetime(df["paidinfulldate"], errors='coerce')
        pna_mask = (first_disb.isna()) | (first_disb > paid_full)

    to_exclude = status_mask | pna_mask
    return df[~to_exclude].index

def derive_loan_distress_metric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derivation Contract: Transforms granular loan status into a 3-tier ordinal metric.
    0: Healthy (PIF, Current, Commit)
    1: Under Duress (Liquidation, Deferred, Past Due)
    2: Written Off (Charged Off)
    """
    if "loanstatus" in df.columns:
        status_upper = df["loanstatus"].astype(str).str.upper().str.strip()

        # Define Health Tiers
        healthy_mask = status_upper.isin(["PAID IN FULL", "PIF", "CURRENT", "COMMIT", "CANCLD"])
        duress_mask = status_upper.str.contains("LIQ|DEFERRED|EXEMPT|PAST DUE|LATE", na=False)
        chgoff_mask = status_upper.isin(["CHGOFF", "CHARGED OFF"])

        # 0 = Healthy, 1 = Duress, 2 = Written Off
        df["loan_distress_score"] = 0
        df.loc[duress_mask, "loan_distress_score"] = 1
        df.loc[chgoff_mask, "loan_distress_score"] = 2
        
        # Add label for easier EDA
        df["loan_distress_label"] = df["loan_distress_score"].map({0: "Healthy", 1: "Under Duress", 2: "Written Off"})

    return df