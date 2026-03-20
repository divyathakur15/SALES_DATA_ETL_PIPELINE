"""
quality.py — Data Quality Checks
Validates and cleans the raw DataFrame before transformation.
"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def check_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows where critical fields are null, log a summary."""
    critical = ["order_id", "order_date", "product_name", "customer_name", "quantity", "unit_price"]
    before = len(df)
    df = df.dropna(subset=critical)
    dropped = before - len(df)
    if dropped:
        logger.warning(f"  ⚠ Dropped {dropped} rows with missing critical values")
    else:
        logger.info("  → No missing critical values ✅")
    return df


def check_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate order_id rows."""
    before = len(df)
    df = df.drop_duplicates(subset=["order_id"])
    dropped = before - len(df)
    if dropped:
        logger.warning(f"  ⚠ Removed {dropped} duplicate order_id rows")
    else:
        logger.info("  → No duplicate order IDs ✅")
    return df


def check_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure numeric columns have valid (positive) values."""
    numeric_cols = ["quantity", "unit_price", "unit_cost", "total_amount", "profit"]
    before = len(df)
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # Remove rows where any numeric column is null or negative quantity/price
    df = df.dropna(subset=numeric_cols)
    df = df[df["quantity"] > 0]
    df = df[df["unit_price"] > 0]
    dropped = before - len(df)
    if dropped:
        logger.warning(f"  ⚠ Removed {dropped} rows with invalid numeric values")
    else:
        logger.info("  → Numeric validation passed ✅")
    return df


def validate_status(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only known status values."""
    valid_statuses = {"Completed", "Returned", "Pending"}
    before = len(df)
    df = df[df["status"].isin(valid_statuses)]
    dropped = before - len(df)
    if dropped:
        logger.warning(f"  ⚠ Removed {dropped} rows with unknown status values")
    else:
        logger.info("  → Status validation passed ✅")
    return df


def run_quality_checks(df: pd.DataFrame) -> pd.DataFrame:
    """Run all data quality checks and return a clean DataFrame."""
    logger.info("Running data quality checks...")
    df = check_missing_values(df)
    df = check_duplicates(df)
    df = check_numeric_columns(df)
    df = validate_status(df)
    logger.info(f"  → Quality checks complete. {len(df)} rows passed ✅")
    return df
