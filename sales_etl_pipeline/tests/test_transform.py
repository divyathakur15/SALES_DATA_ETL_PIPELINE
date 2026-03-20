"""
test_transform.py — Unit tests for src/transform/transform.py
Run with: pytest tests/test_transform.py -v
"""
import pytest
import pandas as pd
from src.transform.transform import (
    build_dim_product,
    build_dim_customer,
    build_dim_date,
    build_fact_sales,
    transform,
)


class TestDimProduct:

    def test_unique_products_only(self, raw_sales_df):
        result = build_dim_product(raw_sales_df)
        assert result["product_name"].nunique() == len(result)

    def test_has_product_id_column(self, raw_sales_df):
        result = build_dim_product(raw_sales_df)
        assert "product_id" in result.columns

    def test_product_ids_start_at_one(self, raw_sales_df):
        result = build_dim_product(raw_sales_df)
        assert result["product_id"].min() == 1

    def test_correct_columns(self, raw_sales_df):
        result = build_dim_product(raw_sales_df)
        assert set(result.columns) == {"product_id", "product_name", "category"}

    def test_row_count_matches_unique_products(self, raw_sales_df):
        expected = raw_sales_df["product_name"].nunique()
        result = build_dim_product(raw_sales_df)
        assert len(result) == expected


class TestDimCustomer:

    def test_unique_customers_by_email(self, raw_sales_df):
        result = build_dim_customer(raw_sales_df)
        assert result["customer_email"].nunique() == len(result)

    def test_has_customer_id_column(self, raw_sales_df):
        result = build_dim_customer(raw_sales_df)
        assert "customer_id" in result.columns

    def test_correct_columns(self, raw_sales_df):
        result = build_dim_customer(raw_sales_df)
        assert set(result.columns) == {
            "customer_id", "customer_name", "customer_email", "customer_type"
        }


class TestDimDate:

    def test_unique_dates_only(self, raw_sales_df):
        raw_sales_df["order_date"] = pd.to_datetime(
            raw_sales_df["order_date"]
        ).dt.strftime("%Y-%m-%d")
        result = build_dim_date(raw_sales_df)
        assert result["full_date"].nunique() == len(result)

    def test_has_required_date_columns(self, raw_sales_df):
        raw_sales_df["order_date"] = pd.to_datetime(
            raw_sales_df["order_date"]
        ).dt.strftime("%Y-%m-%d")
        result = build_dim_date(raw_sales_df)
        for col in ["date_id", "full_date", "year", "month", "quarter", "weekday", "is_weekend"]:
            assert col in result.columns, f"Missing: {col}"

    def test_year_values_are_correct(self, raw_sales_df):
        raw_sales_df["order_date"] = pd.to_datetime(
            raw_sales_df["order_date"]
        ).dt.strftime("%Y-%m-%d")
        result = build_dim_date(raw_sales_df)
        assert (result["year"] == 2023).all()

    def test_month_range(self, raw_sales_df):
        raw_sales_df["order_date"] = pd.to_datetime(
            raw_sales_df["order_date"]
        ).dt.strftime("%Y-%m-%d")
        result = build_dim_date(raw_sales_df)
        assert result["month"].between(1, 12).all()


class TestFactSales:

    def test_row_count_matches_source(self, transformed_tables, raw_sales_df):
        assert len(transformed_tables["fact_sales"]) == len(raw_sales_df)

    def test_no_null_foreign_keys(self, transformed_tables):
        fact = transformed_tables["fact_sales"]
        for fk in ["product_id", "customer_id", "date_id"]:
            assert fact[fk].notna().all(), f"Null FK found in {fk}"

    def test_profit_margin_calculated(self, transformed_tables):
        fact = transformed_tables["fact_sales"]
        assert "profit_margin_pct" in fact.columns
        assert (fact["profit_margin_pct"].notna()).all()

    def test_profit_margin_is_percentage(self, transformed_tables):
        fact = transformed_tables["fact_sales"]
        # Margins should be between -100% and 100% for typical sales
        assert fact["profit_margin_pct"].between(-100, 100).all()

    def test_fact_contains_all_required_columns(self, transformed_tables):
        fact = transformed_tables["fact_sales"]
        required = [
            "order_id", "date_id", "product_id", "customer_id",
            "region", "quantity", "unit_price", "total_amount",
            "profit", "profit_margin_pct", "status"
        ]
        for col in required:
            assert col in fact.columns, f"Missing column: {col}"


class TestTransformIntegration:

    def test_returns_all_four_tables(self, transformed_tables):
        assert set(transformed_tables.keys()) == {
            "dim_product", "dim_customer", "dim_date", "fact_sales"
        }

    def test_all_tables_are_dataframes(self, transformed_tables):
        for name, df in transformed_tables.items():
            assert isinstance(df, pd.DataFrame), f"{name} is not a DataFrame"

    def test_foreign_key_integrity(self, transformed_tables):
        """Every FK in fact_sales must exist in its dimension table."""
        fact        = transformed_tables["fact_sales"]
        dim_product = transformed_tables["dim_product"]
        dim_customer = transformed_tables["dim_customer"]
        dim_date    = transformed_tables["dim_date"]

        assert fact["product_id"].isin(dim_product["product_id"]).all()
        assert fact["customer_id"].isin(dim_customer["customer_id"]).all()
        assert fact["date_id"].isin(dim_date["date_id"]).all()
