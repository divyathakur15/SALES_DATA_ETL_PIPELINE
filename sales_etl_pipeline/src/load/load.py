"""
load.py — Step 3 of ETL Pipeline
Loads transformed DataFrames into MySQL database tables.
"""
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# NOTE: In a real project, install mysql-connector-python:
#   pip install mysql-connector-python
# And set credentials in a .env file (never hardcode them).
# ─────────────────────────────────────────────────────────────

LOAD_ORDER = ["dim_product", "dim_customer", "dim_date", "fact_sales"]

TABLE_KEY_MAP = {
    "dim_product":  "product_id",
    "dim_customer": "customer_id",
    "dim_date":     "date_id",
    "fact_sales":   "order_id",
}


def get_connection(config: dict):
    """
    Create and return a MySQL connection.

    Args:
        config: dict with keys: host, user, password, database, port
    """
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=config.get("host", "localhost"),
            user=config.get("user", "root"),
            password=config.get("password", ""),
            database=config.get("database", "sales_dw"),
            port=config.get("port", 3306),
        )
        logger.info("  → Connected to MySQL ✅")
        return conn
    except ImportError:
        raise ImportError("Run: pip install mysql-connector-python")
    except Exception as e:
        raise ConnectionError(f"Could not connect to MySQL: {e}")


def load_table(conn, table_name: str, df: pd.DataFrame) -> None:
    """
    Insert DataFrame rows into a MySQL table.
    Uses INSERT IGNORE to avoid duplicate key errors on re-runs.
    """
    if df.empty:
        logger.warning(f"  ⚠ Skipping {table_name}: DataFrame is empty")
        return

    cursor = conn.cursor()
    cols   = ", ".join(df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))
    sql = f"INSERT IGNORE INTO {table_name} ({cols}) VALUES ({placeholders})"

    rows = [tuple(row) for row in df.itertuples(index=False, name=None)]
    cursor.executemany(sql, rows)
    conn.commit()
    logger.info(f"  → Loaded {cursor.rowcount} rows into {table_name} ✅")
    cursor.close()


def run_sql_file(conn, filepath: str) -> None:
    """Execute a .sql file (e.g., to create tables)."""
    with open(filepath, "r") as f:
        sql_script = f.read()
    cursor = conn.cursor()
    for statement in sql_script.split(";"):
        stmt = statement.strip()
        if stmt:
            cursor.execute(stmt)
    conn.commit()
    cursor.close()
    logger.info(f"  → Executed SQL file: {filepath} ✅")


def load(tables: dict, config: dict) -> None:
    """
    Load all dimension and fact tables into MySQL.

    Args:
        tables: dict of {table_name: pd.DataFrame}
        config: MySQL connection config dict
    """
    logger.info("Loading data into MySQL...")
    conn = get_connection(config)

    # Run schema creation SQL
    schema_file = os.path.join("sql", "create_tables.sql")
    if os.path.exists(schema_file):
        run_sql_file(conn, schema_file)

    # Load tables in correct order (dimensions before facts)
    for table_name in LOAD_ORDER:
        if table_name in tables:
            load_table(conn, table_name, tables[table_name])

    conn.close()
    logger.info("  → All tables loaded successfully ✅")


def save_to_csv(tables: dict, output_dir: str = "data/processed") -> None:
    """
    Fallback: save transformed tables as CSV files.
    Useful for testing without a MySQL connection.
    """
    os.makedirs(output_dir, exist_ok=True)
    for table_name, df in tables.items():
        path = os.path.join(output_dir, f"{table_name}.csv")
        df.to_csv(path, index=False)
        logger.info(f"  → Saved {table_name} → {path} ({len(df)} rows)")
