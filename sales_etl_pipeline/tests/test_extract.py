"""
test_extract.py — Unit tests for src/extract/extract.py
Run with: pytest tests/test_extract.py -v
"""
import pytest
import pandas as pd
import os
import tempfile
from src.extract.extract import extract, REQUIRED_COLUMNS


class TestExtract:

    def test_extract_returns_dataframe(self, raw_sales_df, tmp_path):
        """extract() should return a pandas DataFrame."""
        csv_path = tmp_path / "test_sales.csv"
        raw_sales_df.to_csv(csv_path, index=False)
        result = extract(str(csv_path))
        assert isinstance(result, pd.DataFrame)

    def test_extract_correct_row_count(self, raw_sales_df, tmp_path):
        """extract() should load all rows from the CSV."""
        csv_path = tmp_path / "test_sales.csv"
        raw_sales_df.to_csv(csv_path, index=False)
        result = extract(str(csv_path))
        assert len(result) == len(raw_sales_df)

    def test_extract_all_columns_present(self, raw_sales_df, tmp_path):
        """extract() should load all expected columns."""
        csv_path = tmp_path / "test_sales.csv"
        raw_sales_df.to_csv(csv_path, index=False)
        result = extract(str(csv_path))
        for col in REQUIRED_COLUMNS:
            assert col in result.columns, f"Missing column: {col}"

    def test_extract_missing_file_raises_error(self):
        """extract() should raise FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            extract("data/raw/this_file_does_not_exist.csv")

    def test_extract_missing_columns_raises_error(self, tmp_path):
        """extract() should raise ValueError when required columns are absent."""
        bad_df = pd.DataFrame({"order_id": [1], "product": ["Laptop"]})
        csv_path = tmp_path / "bad.csv"
        bad_df.to_csv(csv_path, index=False)
        with pytest.raises(ValueError, match="Missing required columns"):
            extract(str(csv_path))

    def test_extract_preserves_data_types(self, raw_sales_df, tmp_path):
        """Numeric columns should remain numeric after extract."""
        csv_path = tmp_path / "test_sales.csv"
        raw_sales_df.to_csv(csv_path, index=False)
        result = extract(str(csv_path))
        assert pd.api.types.is_numeric_dtype(result["quantity"])
        assert pd.api.types.is_numeric_dtype(result["unit_price"])
        assert pd.api.types.is_numeric_dtype(result["profit"])
