-- ============================================================
-- Sales Data Warehouse — Star Schema
-- File: sql/create_tables.sql
-- ============================================================

-- Create and select the database
CREATE DATABASE IF NOT EXISTS sales_dw;
USE sales_dw;

-- ──────────────────────────────────────────────────────────────
-- DIMENSION TABLES
-- ──────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS dim_product (
    product_id   INT          PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category     VARCHAR(50)  NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id    INT          PRIMARY KEY,
    customer_name  VARCHAR(100) NOT NULL,
    customer_email VARCHAR(150) NOT NULL UNIQUE,
    customer_type  VARCHAR(50)  NOT NULL   -- Enterprise, SMB, Individual
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id    INT         PRIMARY KEY,
    full_date  DATE        NOT NULL UNIQUE,
    year       SMALLINT    NOT NULL,
    quarter    TINYINT     NOT NULL,
    month      TINYINT     NOT NULL,
    month_name VARCHAR(15) NOT NULL,
    week       TINYINT     NOT NULL,
    day        TINYINT     NOT NULL,
    weekday    VARCHAR(10) NOT NULL,
    is_weekend BOOLEAN     NOT NULL DEFAULT FALSE
);

-- ──────────────────────────────────────────────────────────────
-- FACT TABLE
-- ──────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS fact_sales (
    order_id          INT            PRIMARY KEY,
    date_id           INT            NOT NULL,
    product_id        INT            NOT NULL,
    customer_id       INT            NOT NULL,
    region            VARCHAR(20)    NOT NULL,
    quantity          INT            NOT NULL,
    unit_price        DECIMAL(10,2)  NOT NULL,
    unit_cost         DECIMAL(10,2)  NOT NULL,
    total_amount      DECIMAL(12,2)  NOT NULL,
    total_cost        DECIMAL(12,2)  NOT NULL,
    profit            DECIMAL(12,2)  NOT NULL,
    profit_margin_pct DECIMAL(5,2)   NOT NULL,
    status            VARCHAR(20)    NOT NULL,

    FOREIGN KEY (date_id)     REFERENCES dim_date(date_id),
    FOREIGN KEY (product_id)  REFERENCES dim_product(product_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id)
);
