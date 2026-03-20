"""
extract.py — Step 1 of ETL Pipeline
Reads raw sales data from a CSV file and returns a DataFrame.
"""
import pandas as pd
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "order_id", "order_date", "product_name", "category",
    "customer_name", "customer_email", "customer_type",
    "region", "quantity", "unit_price", "unit_cost",
    "total_amount", "total_cost", "profit", "status",
]


def extract(filepath: str) -> pd.DataFrame:
    """
    Read the CSV file and return a raw DataFrame.

    Args:
        filepath: Path to the CSV file.

    Returns:
        pd.DataFrame with raw data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If required columns are missing.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    logger.info(f"Extracting data from: {filepath}")
    df = pd.read_csv(filepath)
    logger.info(f"  → Loaded {len(df)} rows, {len(df.columns)} columns")

    # Validate required columns
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    logger.info("  → Column validation passed ✅")
    return df


if __name__ == "__main__":
    df = extract("data/raw/sales_data.csv")
    print(df.head())
    print(f"\nShape: {df.shape}")
    print(f"\nData types:\n{df.dtypes}")
