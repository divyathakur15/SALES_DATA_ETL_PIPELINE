create database sales_dw;
use sales_dw;


CREATE DATABASE IF NOT EXISTS sales_dw;

CREATE USER IF NOT EXISTS 'etl_user'@'localhost'
IDENTIFIED BY 'Divya@1516';

GRANT ALL PRIVILEGES ON sales_dw.* TO 'etl_user'@'localhost';

FLUSH PRIVILEGES;


select * from dim_customer;
select * from dim_date;
select * from dim_product;
select * from fact_sales;