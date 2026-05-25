import pandas as pd
import numpy as np


def clean_dataframe(df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
    """
    Clean and validate a single DataFrame.
    - Strip whitespace from strings
    - Parse date columns
    - Fill missing values
    - Remove fully duplicate rows
    """
    if df.empty:
        return df

    df = df.copy()

    str_cols = df.select_dtypes(include='object').columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace('nan', '')
        df[col] = df[col].replace('None', '')

    date_keywords = ['date', 'Date', '_at', 'month', 'Month']
    for col in df.columns:
        if any(kw in col for kw in date_keywords):
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except Exception:
                pass

    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = df[num_cols].fillna(0)

    df = df.drop_duplicates()

    df = df.reset_index(drop=True)

    return df


def validate_dataframe(df: pd.DataFrame, sheet_name: str) -> list:
    """
    Validate a DataFrame and return a list of warning messages.
    """
    warnings = []

    if df.empty:
        warnings.append(f"{sheet_name}: sheet is empty, skipping.")
        return warnings

    id_col_map = {
        'Customers'  : 'CustomerID',
        'Plans'      : 'PlanID',
        'Campaigns'  : 'CampaignID',
        'Sales'      : 'SaleID',
        'Leads'      : 'LeadID',
        'Usage'      : 'UsageID',
    }

    id_col = id_col_map.get(sheet_name)
    if id_col and id_col in df.columns:
        dupes = df[id_col].duplicated().sum()
        if dupes > 0:
            warnings.append(
                f"{sheet_name}: {dupes} duplicate {id_col} values found."
            )
        nulls = df[id_col].isna().sum() + (df[id_col] == '').sum()
        if nulls > 0:
            warnings.append(
                f"{sheet_name}: {nulls} missing {id_col} values found."
            )
    else:
        if id_col:
            warnings.append(
                f"{sheet_name}: expected column '{id_col}' not found."
            )

    return warnings


def transform_all(extracted_data: dict) -> tuple:
    """
    Clean and validate all sheets.
    Returns (cleaned_data dict, all_warnings list)
    """
    cleaned  = {}
    warnings = []

    for sheet_name, df in extracted_data.items():
        cleaned_df       = clean_dataframe(df, sheet_name)
        sheet_warnings   = validate_dataframe(cleaned_df, sheet_name)
        cleaned[sheet_name] = cleaned_df
        warnings.extend(sheet_warnings)

    return cleaned, warnings