import pandas as pd

def filter_invalid_loan_status_dates(df: pd.DataFrame) -> pd.Index:
    """
    Row-Filter Contract: Identifies valid loans by excluding specific statuses 
    and invalid date sequences (First Disbursement after Paid In Full).
    
    Args:
        df: The operational dataframe.
    Returns:
        pd.Index: The indices of the rows to KEEP.
    """
    # Ensure date columns are datetime objects for comparison
    # Note: Pipeline type casting usually handles this, but we ensure parity here.
    first_disb = pd.to_datetime(df["firstdisbursementdate"], errors='coerce')
    paid_full = pd.to_datetime(df["paidinfulldate"], errors='coerce')

    pna = (first_disb.isna()) | (first_disb > paid_full)

    to_exclude = (
        (df["loanstatus"].isin(["EXEMPT", "CANCLD", "COMMIT"])) |
        pna
    )

    excluded_count = to_exclude.sum()
    print(f"DEBUG: Row Filter 'filter_invalid_loan_status_dates' identified {excluded_count} rows for removal.")

    return df[~to_exclude].index