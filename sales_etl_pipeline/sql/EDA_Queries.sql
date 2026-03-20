 # Exploratory Data Analysis
 
use sales_dw;

# EDA Query 1 — Overview of the Data
-- How many rows in each table?

select "fact_sales" as Table_name , count(*) as total_rows from fact_sales 
union all
select "dim_customer", count(*) from dim_customer
union all
select "dim_product", count(*) from dim_product
union all
select "dim_date", count(*) from dim_date;


# EDA Query 2 — Overall Sales Summary
-- Total revenue, profit, orders and average order value

