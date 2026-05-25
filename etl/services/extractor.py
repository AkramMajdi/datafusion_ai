import pandas as pd
from pathlib import Path


SUPPORTED_SHEETS = [
    'Customers', 'Plans', 'Campaigns', 'Sales', 'Leads', 'Usage'
]


def extract_from_excel(file_path: str) -> dict:
    """
    Read all sheets from the Excel file.
    Returns a dict: { sheet_name: DataFrame }
    """
    result = {}
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    xl = pd.ExcelFile(file_path)
    available_sheets = xl.sheet_names

    for sheet in SUPPORTED_SHEETS:
        if sheet in available_sheets:
            df = pd.read_excel(file_path, sheet_name=sheet, header=1)
            df = df.dropna(how='all')
            result[sheet] = df
        else:
            result[sheet] = pd.DataFrame()

    return result


def extract_from_csv(file_path: str) -> dict:
    """
    Read a single CSV file.
    Returns a dict with one key: { 'data': DataFrame }
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(file_path)
    df = df.dropna(how='all')

    return {'data': df}