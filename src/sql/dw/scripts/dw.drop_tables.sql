--!script
drop table if exists {{catalog}}.dw.dim_customer;
drop table if exists {{catalog}}.dw.dim_product;  
drop table if exists {{catalog}}.dw.dim_store; 
drop table if exists {{catalog}}.dw.fact_sales;