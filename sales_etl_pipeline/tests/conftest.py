"""
conftest.py — Shared pytest fixtures
These fixtures are automatically available in all test files.
"""
import pytest
import pandas as pd
import sys, os

# Make src importable from tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def raw_sales_df():
    """A small, clean DataFrame that mimics the real CSV."""
    return pd.DataFrame({
        "order_id":       [1001, 1002, 1003, 1004, 1005],
        "order_date":     ["2023-01-15", "2023-02-20", "2023-03-10",
                           "2023-04-05", "2023-05-18"],
        "product_name":   ["Laptop Pro", "Wireless Mouse", "USB-C Hub",
                           "Laptop Pro", "Office Chair"],
        "category":       ["Electronics", "Electronics", "Electronics",
                           "Electronics", "Furniture"],
        "customer_name":  ["Alice Johnson", "Bob Smith", "Alice Johnson",
                           "Carol White", "Bob Smith"],
        "customer_email": ["alice@example.com", "bob@example.com",
                           "alice@example.com", "carol@example.com",
                           "bob@example.com"],
        "customer_type":  ["Enterprise", "SMB", "Enterprise",
                           "Enterprise", "SMB"],
        "region":         ["North", "South", "East", "West", "North"],
        "quantity":       [2, 5, 3, 1, 2],
        "unit_price":     [1250.00, 34.50, 52.00, 1180.00, 360.00],
        "unit_cost":      [820.00, 12.00, 19.00, 800.00, 185.00],
        "total_amount":   [2500.00, 172.50, 156.00, 1180.00, 720.00],
        "total_cost":     [1640.00, 60.00, 57.00, 800.00, 370.00],
        "profit":         [860.00, 112.50, 99.00, 380.00, 350.00],
        "status":         ["Completed", "Completed", "Returned",
                           "Completed", "Pending"],
    })


@pytest.fixture
def dirty_sales_df(raw_sales_df):
    """A DataFrame with common data quality problems injected."""
    df = raw_sales_df.copy()
    # Duplicate row
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    # Missing critical value
    df.loc[1, "customer_name"] = None
    # Negative quantity
    df.loc[2, "quantity"] = -3
    # Invalid status
    df.loc[3, "status"] = "UNKNOWN_STATUS"
    return df


@pytest.fixture
def transformed_tables(raw_sales_df):
    """Pre-built star-schema tables from the clean fixture."""
    from src.transform.transform import transform
    raw_sales_df["order_date"] = pd.to_datetime(
        raw_sales_df["order_date"]
    ).dt.strftime("%Y-%m-%d")
    return transform(raw_sales_df)
