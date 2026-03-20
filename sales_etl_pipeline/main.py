"""
main.py — ETL Pipeline Entry Point
Runs the full Extract → Quality Check → Transform → Load pipeline.

Usage:
    python main.py                  # runs ETL, saves CSVs (no MySQL needed)
    python main.py --mysql          # runs ETL and loads into MySQL
"""
import logging
import argparse
import os
import sys

# Make src importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from extract.extract       import extract
from quality.quality       import run_quality_checks
from transform.transform   import transform
from load.load             import load, save_to_csv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log"),
    ]
)
logger = logging.getLogger(__name__)

# ── MySQL config (or load from .env in production) ──────────
MYSQL_CONFIG = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "user":     os.getenv("DB_USER",     "root"),
    "password": os.getenv("DB_PASSWORD", "Divya@1516"),
    "database": os.getenv("DB_NAME",     "sales_dw"),
    "port":     int(os.getenv("DB_PORT", "3306")),
}

RAW_DATA_PATH = "data/raw/sales_data.csv"


def run_pipeline(use_mysql: bool = False):
    logger.info("=" * 55)
    logger.info("  SALES DATA ETL PIPELINE — STARTING")
    logger.info("=" * 55)

    # 1. EXTRACT
    logger.info("\n📥 STEP 1: Extract")
    raw_df = extract(RAW_DATA_PATH)

    # 2. QUALITY CHECKS
    logger.info("\n🔍 STEP 2: Data Quality Checks")
    clean_df = run_quality_checks(raw_df)

    # 3. TRANSFORM
    logger.info("\n⚙️  STEP 3: Transform")
    tables = transform(clean_df)

    # 4. LOAD
    logger.info("\n📤 STEP 4: Load")
    if use_mysql:
        load(tables, MYSQL_CONFIG)
    else:
        save_to_csv(tables)
        logger.info("  (Tip: run with --mysql to load into MySQL)")

    logger.info("\n" + "=" * 55)
    logger.info("  ✅ PIPELINE COMPLETE")
    logger.info("=" * 55)
    return tables


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sales Data ETL Pipeline")
    parser.add_argument("--mysql", action="store_true",
                        help="Load into MySQL instead of saving CSVs")
    args = parser.parse_args()
    run_pipeline(use_mysql=args.mysql)
