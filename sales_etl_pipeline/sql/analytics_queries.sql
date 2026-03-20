-- ============================================================
-- Sales Analytics Queries
-- File: sql/analytics_queries.sql
-- Run these after loading data into MySQL.
-- ============================================================

USE sales_dw;

-- ── 1. Total Sales & Profit by Region ────────────────────────
SELECT
    fs.region,
    COUNT(fs.order_id)            AS total_orders,
    SUM(fs.quantity)              AS total_units,
    ROUND(SUM(fs.total_amount),2) AS total_revenue,
    ROUND(SUM(fs.profit),2)       AS total_profit,
    ROUND(AVG(fs.profit_margin_pct),2) AS avg_margin_pct
FROM fact_sales fs
WHERE fs.status = 'Completed'
GROUP BY fs.region
ORDER BY total_revenue DESC;


-- ── 2. Top 5 Best-Selling Products (by Revenue) ──────────────
SELECT
    dp.product_name,
    dp.category,
    SUM(fs.quantity)              AS units_sold,
    ROUND(SUM(fs.total_amount),2) AS total_revenue,
    ROUND(SUM(fs.profit),2)       AS total_profit
FROM fact_sales fs
JOIN dim_product dp ON fs.product_id = dp.product_id
WHERE fs.status = 'Completed'
GROUP BY dp.product_name, dp.category
ORDER BY total_revenue DESC
LIMIT 5;


-- ── 3. Monthly Sales Trend ───────────────────────────────────
SELECT
    dd.year,
    dd.month,
    dd.month_name,
    COUNT(fs.order_id)            AS orders,
    ROUND(SUM(fs.total_amount),2) AS monthly_revenue,
    ROUND(SUM(fs.profit),2)       AS monthly_profit
FROM fact_sales fs
JOIN dim_date dd ON fs.date_id = dd.date_id
WHERE fs.status = 'Completed'
GROUP BY dd.year, dd.month, dd.month_name
ORDER BY dd.year, dd.month;


-- ── 4. Customer Purchase Behavior ───────────────────────────
SELECT
    dc.customer_name,
    dc.customer_type,
    COUNT(fs.order_id)            AS total_orders,
    ROUND(SUM(fs.total_amount),2) AS total_spent,
    ROUND(AVG(fs.total_amount),2) AS avg_order_value,
    ROUND(SUM(fs.profit),2)       AS total_profit_generated
FROM fact_sales fs
JOIN dim_customer dc ON fs.customer_id = dc.customer_id
WHERE fs.status = 'Completed'
GROUP BY dc.customer_name, dc.customer_type
ORDER BY total_spent DESC
LIMIT 10;


-- ── 5. Sales by Product Category & Quarter ──────────────────
SELECT
    dp.category,
    dd.quarter,
    COUNT(fs.order_id)            AS orders,
    ROUND(SUM(fs.total_amount),2) AS revenue,
    ROUND(SUM(fs.profit),2)       AS profit
FROM fact_sales fs
JOIN dim_product dp ON fs.product_id = dp.product_id
JOIN dim_date    dd ON fs.date_id    = dd.date_id
WHERE fs.status = 'Completed'
GROUP BY dp.category, dd.quarter
ORDER BY dp.category, dd.quarter;


-- ── 6. Return Rate by Product ────────────────────────────────
SELECT
    dp.product_name,
    COUNT(fs.order_id) AS total_orders,
    SUM(CASE WHEN fs.status = 'Returned' THEN 1 ELSE 0 END) AS returned_orders,
    ROUND(
        SUM(CASE WHEN fs.status = 'Returned' THEN 1 ELSE 0 END) * 100.0
        / COUNT(fs.order_id), 2
    ) AS return_rate_pct
FROM fact_sales fs
JOIN dim_product dp ON fs.product_id = dp.product_id
GROUP BY dp.product_name
ORDER BY return_rate_pct DESC;


-- ── 7. Weekend vs Weekday Sales ──────────────────────────────
SELECT
    CASE WHEN dd.is_weekend THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(fs.order_id)            AS orders,
    ROUND(SUM(fs.total_amount),2) AS revenue,
    ROUND(AVG(fs.total_amount),2) AS avg_order_value
FROM fact_sales fs
JOIN dim_date dd ON fs.date_id = dd.date_id
WHERE fs.status = 'Completed'
GROUP BY day_type
ORDER BY day_type;
