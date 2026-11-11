import pandas as pd
from django.db import connection


TABLE_MAP = {
    'Customers' : 'etl_customer',
    'Plans'     : 'etl_plan',
    'Campaigns' : 'etl_campaign',
    'Sales'     : 'etl_sale',
    'Leads'     : 'etl_lead',
    'Usage'     : 'etl_usage',
}


def load_dataframe(df: pd.DataFrame, table_name: str) -> int:
    """
    Load a DataFrame into the database table.
    Uses pandas to_sql with replace strategy.
    Returns number of rows inserted.
    """
    if df.empty:
        return 0

    from django.db import connections
    db_settings = connections['default'].settings_dict

    # Build SQLAlchemy connection string
    engine = _get_engine(db_settings)

    # Clean column names — lowercase, replace spaces with underscores
    df.columns = [
        col.lower().replace(' ', '_').replace('-', '_').replace('/', '_')
        for col in df.columns
    ]

    df.to_sql(
        table_name,
        engine,
        if_exists='replace',
        index=False,
        chunksize=500,
    )

    return len(df)


def _get_engine(db_settings: dict):
    """Build SQLAlchemy engine from Django DB settings."""
    from sqlalchemy import create_engine

    engine_map = {
        'django.db.backends.sqlite3'  : 'sqlite',
        'django.db.backends.mysql'    : 'mysql+pymysql',
        'django.db.backends.postgresql': 'postgresql',
    }

    backend  = db_settings.get('ENGINE', '')
    dialect  = engine_map.get(backend, 'sqlite')

    if dialect == 'sqlite':
        db_name = db_settings.get('NAME', 'db.sqlite3')
        return create_engine(f'sqlite:///{db_name}')

    user     = db_settings.get('USER', '')
    password = db_settings.get('PASSWORD', '')
    host     = db_settings.get('HOST', 'localhost')
    port     = db_settings.get('PORT', '3306')
    name     = db_settings.get('NAME', '')

    return create_engine(
        f'{dialect}://{user}:{password}@{host}:{port}/{name}'
    )


def load_all(cleaned_data: dict) -> dict:
    """
    Load all cleaned DataFrames into database tables.
    Returns dict of { sheet_name: rows_loaded }
    """
    results = {}

    for sheet_name, df in cleaned_data.items():
        if df.empty:
            results[sheet_name] = 0
            continue
        table_name = TABLE_MAP.get(sheet_name, f'etl_{sheet_name.lower()}')
        rows = load_dataframe(df, table_name)
        results[sheet_name] = rows

    return results