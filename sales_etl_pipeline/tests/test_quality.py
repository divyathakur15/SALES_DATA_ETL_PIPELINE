"""
test_quality.py — Unit tests for src/quality/quality.py
Run with: pytest tests/test_quality.py -v
"""
import pytest
import pandas as pd
from src.quality.quality import (
    check_missing_values,
    check_duplicates,
    check_numeric_columns,
    validate_status,
    run_quality_checks,
)


class TestMissingValues:

    def test_drops_rows_with_null_order_id(self, raw_sales_df):
        raw_sales_df.loc[0, "order_id"] = None
        result = check_missing_values(raw_sales_df)
        assert len(result) == len(raw_sales_df) - 1

    def test_drops_rows_with_null_customer_name(self, raw_sales_df):
        raw_sales_df.loc[1, "customer_name"] = None
        result = check_missing_values(raw_sales_df)
        assert len(result) == len(raw_sales_df) - 1

    def test_clean_data_unchanged(self, raw_sales_df):
        """Clean data should pass through with no rows dropped."""
        result = check_missing_values(raw_sales_df)
        assert len(result) == len(raw_sales_df)


class TestDuplicates:

    def test_removes_duplicate_order_ids(self, raw_sales_df):
        duped = pd.concat([raw_sales_df, raw_sales_df.iloc[[0]]], ignore_index=True)
        result = check_duplicates(duped)
        assert len(result) == len(raw_sales_df)

    def test_no_duplicates_unchanged(self, raw_sales_df):
        result = check_duplicates(raw_sales_df)
        assert len(result) == len(raw_sales_df)

    def test_all_order_ids_unique_after_check(self, raw_sales_df):
        duped = pd.concat([raw_sales_df, raw_sales_df], ignore_index=True)
        result = check_duplicates(duped)
        assert result["order_id"].nunique() == result["order_id"].count()


class TestNumericColumns:

    def test_removes_negative_quantity(self, raw_sales_df):
        raw_sales_df.loc[0, "quantity"] = -5
        result = check_numeric_columns(raw_sales_df)
        assert (result["quantity"] > 0).all()

    def test_removes_zero_unit_price(self, raw_sales_df):
        raw_sales_df.loc[0, "unit_price"] = 0
        result = check_numeric_columns(raw_sales_df)
        assert (result["unit_price"] > 0).all()

    def test_coerces_invalid_string_to_nan_and_drops(self, raw_sales_df):
        raw_sales_df.loc[0, "quantity"] = "not_a_number"
        result = check_numeric_columns(raw_sales_df)
        assert len(result) == len(raw_sales_df) - 1


class TestStatusValidation:

    def test_removes_unknown_status(self, raw_sales_df):
        raw_sales_df.loc[0, "status"] = "INVALID"
        result = validate_status(raw_sales_df)
        assert "INVALID" not in result["status"].values

    def test_keeps_valid_statuses(self, raw_sales_df):
        result = validate_status(raw_sales_df)
        valid = {"Completed", "Returned", "Pending"}
        assert set(result["status"].unique()).issubset(valid)


class TestRunQualityChecks:

    def test_clean_data_passes_all_checks(self, raw_sales_df):
        result = run_quality_checks(raw_sales_df)
        assert len(result) == len(raw_sales_df)

    def test_dirty_data_is_cleaned(self, dirty_sales_df):
        """dirty_sales_df has duplicates, nulls, bad status, negative qty."""
        result = run_quality_checks(dirty_sales_df)
        assert result["order_id"].nunique() == result["order_id"].count()
        assert result["customer_name"].notna().all()
        assert (result["quantity"] > 0).all()
        assert set(result["status"].unique()).issubset({"Completed", "Returned", "Pending"})

    def test_returns_dataframe(self, raw_sales_df):
        result = run_quality_checks(raw_sales_df)
        assert isinstance(result, pd.DataFrame)
