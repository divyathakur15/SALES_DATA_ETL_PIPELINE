"""
transform.py — Step 2 of ETL Pipeline
Cleans data and builds dimension + fact tables ready for loading.
"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def build_dim_product(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create the dim_product dimension table.
    One row per unique product.
    """
    dim = (
        df[["product_name", "category"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim.insert(0, "product_id", range(1, len(dim) + 1))
    logger.info(f"  → dim_product: {len(dim)} rows")
    return dim


def build_dim_customer(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create the dim_customer dimension table.
    One row per unique customer email.
    """
    dim = (
        df[["customer_name", "customer_email", "customer_type"]]
        .drop_duplicates(subset=["customer_email"])
        .reset_index(drop=True)
    )
    dim.insert(0, "customer_id", range(1, len(dim) + 1))
    logger.info(f"  → dim_customer: {len(dim)} rows")
    return dim


def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create the dim_date dimension table.
    One row per unique order_date with date attributes.
    """
    dates = pd.to_datetime(df["order_date"]).drop_duplicates().reset_index(drop=True)
    dim = pd.DataFrame({
        "date_id":    range(1, len(dates) + 1),
        "full_date":  dates.dt.strftime("%Y-%m-%d"),
        "year":       dates.dt.year,
        "quarter":    dates.dt.quarter,
        "month":      dates.dt.month,
        "month_name": dates.dt.month_name(),
        "week":       dates.dt.isocalendar().week.astype(int),
        "day":        dates.dt.day,
        "weekday":    dates.dt.day_name(),
        "is_weekend": dates.dt.dayofweek >= 5,
    })
    logger.info(f"  → dim_date: {len(dim)} rows")
    return dim


def build_fact_sales(
    df: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_customer: pd.DataFrame,
    dim_date: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create the fact_sales table by joining foreign keys from dimension tables.
    """
    fact = df.copy()

    # Join product_id
    fact = fact.merge(
        dim_product[["product_id", "product_name"]],
        on="product_name", how="left"
    )

    # Join customer_id
    fact = fact.merge(
        dim_customer[["customer_id", "customer_email"]],
        on="customer_email", how="left"
    )

    # Join date_id
    dim_date_lookup = dim_date[["date_id", "full_date"]].rename(columns={"full_date": "order_date"})
    fact = fact.merge(dim_date_lookup, on="order_date", how="left")

    # Recalculate profit margin %
    fact["profit_margin_pct"] = (
        (fact["profit"] / fact["total_amount"]) * 100
    ).round(2)

    # Select and rename final columns
    fact = fact[[
        "order_id", "date_id", "product_id", "customer_id",
        "region", "quantity", "unit_price", "unit_cost",
        "total_amount", "total_cost", "profit", "profit_margin_pct", "status",
    ]]

    logger.info(f"  → fact_sales: {len(fact)} rows")
    return fact


def transform(df: pd.DataFrame) -> dict:
    """
    Run all transformations and return a dict of DataFrames.

    Returns:
        {
          "dim_product":  pd.DataFrame,
          "dim_customer": pd.DataFrame,
          "dim_date":     pd.DataFrame,
          "fact_sales":   pd.DataFrame,
        }
    """
    logger.info("Running transformations...")

    # Ensure date is string for consistent merging
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.strftime("%Y-%m-%d")

    dim_product  = build_dim_product(df)
    dim_customer = build_dim_customer(df)
    dim_date     = build_dim_date(df)
    fact_sales   = build_fact_sales(df, dim_product, dim_customer, dim_date)

    logger.info("  → All transformations complete ✅")
    return {
        "dim_product":  dim_product,
        "dim_customer": dim_customer,
        "dim_date":     dim_date,
        "fact_sales":   fact_sales,
    }
