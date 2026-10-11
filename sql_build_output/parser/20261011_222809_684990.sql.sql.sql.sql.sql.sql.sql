
CREATE CATALOG IF NOT EXISTS dev_sql_build
MANAGED LOCATION 'abfss://hub@datalakegeneva.dfs.core.windows.net/managed/dev_sql_build';
create schema if not exists dev_sql_build.`dw`;
create schema if not exists dev_sql_build.`source`;
create schema if not exists dev_sql_build.`stage`;
create schema if not exists dev_sql_build.`audit`;
--!script
drop table if exists dev_sql_build.audit.audit;
drop table if exists dev_sql_build.audit.table;  
drop table if exists dev_sql_build.audit.test; 
drop table if exists dev_sql_build.audit.version;
--!script
drop table if exists dev_sql_build.source._england_sales;
drop table if exists dev_sql_build.source._ireland_sales;  
drop table if exists dev_sql_build.source._scotland_sales; 
drop table if exists dev_sql_build.source._wales_sales;
drop table if exists dev_sql_build.source._customer;
drop table if exists dev_sql_build.source._store;
drop table if exists dev_sql_build.source._product;
--!script
drop table if exists dev_sql_build.stage._dw_fact_sales;
drop table if exists dev_sql_build.stage._dw_dim_product;
drop table if exists dev_sql_build.stage._dw_dim_customer;
drop table if exists dev_sql_build.stage._dw_dim_store;
drop table if exists dev_sql_build.stage._dw_dim_strore;
--!script
drop table if exists dev_sql_build.dw.dim_customer;
drop table if exists dev_sql_build.dw.dim_product;  
drop table if exists dev_sql_build.dw.dim_store; 
drop table if exists dev_sql_build.dw.fact_sales;
create table if not exists `audit`.`table` (
    `table_id`              string      not null,
    `job_run_id`            bigint      not null,
    `from_catalog`          string      not null,
    `from_schema`           string      not null,
    `from_object`           string      not null,
    `catalog`               string      not null,
    `schema`                string      not null,
    `object`                string      not null,
    `data_set`              string      not null,
    `num_affected_rows`     bigint      not null,
    `num_updated_rows`      bigint      not null,
    `num_deleted_rows`      bigint      not null,
    `num_inserted_rows`     bigint      not null,
    `num_invalid_rows`      bigint      not null,
    `created_date`          timestamp   not null,
    `created_by`            string      not null,
    constraint `table_pk`   primary key (`table_id`)
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
);
create table if not exists `audit`.`test` (
    `test_id`       bigint      generated always as identity,
    `job_run_id`    bigint      not null,
    `snapshot_date` date        not null,
    `test_set`      string      not null,
    `test`          string      not null,
    `succeeded`     boolean     not null,
    `classname`     string      not null,
    `failure_count` bigint      not null,
    `failure`       string      not null,
    `message`       string      not null,
    `time`          double      not null,
    `created_by`    string      not null,
    `created_date`  timestamp   not null,
    constraint `test_pk` primary key (`test_id`)
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name',
  'delta.appendOnly' = 'true'
);
create table if not exists `audit`.`version` (
    `version`       string      not null,
    `git_version`   string      not null,
    `catalog`       string      not null,
    `component`     bigint      not null,
    `change_set`    date        not null,
    `path`          string      not null,
    `created_date`  timestamp   not null,
    `created_by`    string      not null,
    constraint `version_pk` primary key (`version`)
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name',
  'delta.appendOnly' = 'true'
);
create table if not exists `audit`.`audit` (
    `job_run_id`    bigint      not null,
    `environment`   string      not null,
    `catalog`       string      not null,
    `snapshot_date` date        not null,
    `created_date`  timestamp   not null,
    `created_by`    string      not null,
    `updated_date`  timestamp   not null,
    `updated_by`    string      not null,
    constraint `audit_pk` primary key (`job_run_id`)
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
);
create table if not exists `source`.`_ireland_sales` (
    `customer_id`           bigint          not null,
    `product_id`            string          not null,
    `store_id`              string          not null,
    `transaction_date`      timestamp       not null,
    `unit`                  int             not null,
    `price`                 decimal(6,4)    not null,
    `amount`                decimal(10,4)   not null,
    `discount`              decimal(6,4)    not null,
    `_job_run_id`           bigint          not null,
    `_created_date`         timestamp       not null,
    `_created_by`           string          not null,
    `_updated_date`         timestamp       not null,
    `_updated_by`           string          not null,
    constraint `_ireland_sales_pk` primary key (
        `_job_run_id`,
        `customer_id`,
        `product_id`,
        `store_id`,
        `transaction_date`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by auto;
create table if not exists `source`.`_customer` (
    `customer_id`           bigint          not null,
    `first_name`            string          not null,
    `last_name`             string          not null,
    `date_of_brith`         date            not null,
    `gender`                string          not null,
    `_job_run_id`           bigint          not null,
    `_created_date`         timestamp       not null,
    `_created_by`           string          not null,
    `_updated_date`         timestamp       not null,
    `_updated_by`           string          not null,
    constraint `_customer_pk` primary key (
        `_job_run_id`,
        `customer_id`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by auto;
create table if not exists `source`.`_england_sales` (
    `customer_id`           bigint          not null,
    `product_id`            string          not null,
    `store_id`              string          not null,
    `transaction_date`      timestamp       not null,
    `unit`                  int             not null,
    `price`                 decimal(6,4)    not null,
    `amount`                decimal(10,4)   not null,
    `discount`              decimal(6,4)    not null,
    `_job_run_id`           bigint          not null,
    `_created_date`         timestamp       not null,
    `_created_by`           string          not null,
    `_updated_date`         timestamp       not null,
    `_updated_by`           string          not null,
    constraint `_england_sales_pk` primary key (
        `_job_run_id`,
        `customer_id`,
        `product_id`,
        `store_id`,
        `transaction_date`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by auto;
create table if not exists `source`.`_scotland_sales` (
    `customer_id`           bigint          not null,
    `product_id`            string          not null,
    `store_id`              string          not null,
    `transaction_date`      timestamp       not null,
    `unit`                  int             not null,
    `price`                 decimal(6,4)    not null,
    `amount`                decimal(10,4)   not null,
    `discount`              decimal(6,4)    not null,
    `_job_run_id`           bigint          not null,
    `_created_date`         timestamp       not null,
    `_created_by`           string          not null,
    `_updated_date`         timestamp       not null,
    `_updated_by`           string          not null,
    constraint `_scotland_sales_pk` primary key (
        `_job_run_id`,
        `customer_id`,
        `product_id`,
        `store_id`,
        `transaction_date`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by auto;
create table if not exists `source`.`_store` (
    `store_id`              bigint          not null,
    `address_line_1`        string          not null,
    `address_line_2`        string          not null,
    `address_line_3`        string          not null,
    `postcode`              string          not null,
    `county`                string          not null,
    `region`                string          not null,
    `country`               string          not null,
    `_job_run_id`           bigint          not null,
    `_created_date`         timestamp       not null,
    `_created_by`           string          not null,
    `_updated_date`         timestamp       not null,
    `_updated_by`           string          not null,
    constraint `_store_pk` primary key (
        `_job_run_id`,
        `store_id`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by auto;
create table if not exists `source`.`_product` (
    `product_id`            bigint          not null,
    `sku`                   string          not null,
    `name`                  string          not null,
    `sub_category`          string          not null,
    `category`              string          not null,
    `_job_run_id`           bigint          not null,
    `_created_date`         timestamp       not null,
    `_created_by`           string          not null,
    `_updated_date`         timestamp       not null,
    `_updated_by`           string          not null,
    constraint `_product_pk` primary key (
        `_job_run_id`,
        `product_id`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by auto;
create table if not exists `source`.`_wales_sales` (
    `customer_id`           bigint          not null,
    `product_id`            string          not null,
    `store_id`              string          not null,
    `transaction_date`      timestamp       not null,
    `unit`                  int             not null,
    `price`                 decimal(6,4)    not null,
    `amount`                decimal(10,4)   not null,
    `discount`              decimal(6,4)    not null,
    `_job_run_id`           bigint          not null,
    `_created_date`         timestamp       not null,
    `_created_by`           string          not null,
    `_updated_date`         timestamp       not null,
    `_updated_by`           string          not null,
    constraint `_wales_sales_pk` primary key (
        `_job_run_id`,
        `customer_id`,
        `product_id`,
        `store_id`,
        `transaction_date`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by auto;
create table if not exists `stage`.`_dw_dim_customer` (
    `customer_id`           bigint          not null,
    `first_name`            string          not null,
    `last_name`             string          not null,
    `date_of_brith`         date            not null,
    `gender`                string          not null,
    `_job_run_id`           bigint          not null,
    `_created_date`         timestamp       not null,
    `_created_by`           string          not null,
    `_updated_date`         timestamp       not null,
    `_updated_by`           string          not null,
    constraint `_dw_dim_customer_pk` primary key (
        `_job_run_id`,
        `customer_id`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by auto;
create table if not exists `stage`.`_dw_dim_store` (
    `store_id`              bigint          not null,
    `address_line_1`        string          not null,
    `address_line_2`        string          not null,
    `address_line_3`        string          not null,
    `postcode`              string          not null,
    `county`                string          not null,
    `region`                string          not null,
    `country`               string          not null,
    `_job_run_id`           bigint          not null,
    `_created_date`         timestamp       not null,
    `_created_by`           string          not null,
    `_updated_date`         timestamp       not null,
    `_updated_by`           string          not null,
    constraint `_dw_dim_store_pk` primary key (
        `_job_run_id`,
        `store_id`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by auto;
create table if not exists `stage`.`_dw_dim_product` (
    `product_id`            bigint          not null,
    `sku`                   string          not null,
    `name`                  string          not null,
    `sub_category`          string          not null,
    `category`              string          not null,
    `_job_run_id`           bigint          not null,
    `_created_date`         timestamp       not null,
    `_created_by`           string          not null,
    `_updated_date`         timestamp       not null,
    `_updated_by`           string          not null,
    constraint `_dw_dim_product_pk` primary key (
        `_job_run_id`,
        `product_id`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by auto;
create table if not exists `stage`.`_dw_fact_sales` (
    `customer_id`           bigint          not null,
    `product_id`            string          not null,
    `store_id`              string          not null,
    `transaction_date`      timestamp       not null,
    `unit`                  int             not null,
    `price`                 decimal(6,4)    not null,
    `amount`                decimal(10,4)   not null,
    `discount`              decimal(6,4)    not null,
    `_job_run_id`           bigint          not null,
    `_created_date`         timestamp       not null,
    `_created_by`           string          not null,
    `_updated_date`         timestamp       not null,
    `_updated_by`           string          not null,
    constraint `_dw_fact_sales_pk` primary key (
        `_job_run_id`,
        `customer_id`,
        `product_id`,
        `store_id`,
        `transaction_date`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by auto;
create table if not exists `dw`.`dim_store` (
    `store_key`          bigint generated always as identity,
    `store_id`              bigint          not null,
    `store_name`            string          not null,
    `address_line_1`        string          not null,
    `address_line_2`        string          not null,
    `address_line_3`        string          not null,
    `postcode`              string          not null,
    `county`                string          not null,
    `region`                string          not null,
    `country`               string          not null,
    `_job_run_id`           bigint          not null,
    `_created_date`         timestamp       not null,
    `_created_by`           string          not null,
    `_updated_date`         timestamp       not null,
    `_updated_by`           string          not null,
    constraint `dim_store_pk` primary key (
        `store_key`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by auto;
create table if not exists `dw`.`dim_product` (
    `product_key`           bigint generated always as identity,
    `product_id`            bigint          not null,
    `sku`                   string          not null,
    `name`                  string          not null,
    `sub_category`          string          not null,
    `category`              string          not null,
    `_job_run_id`           bigint          not null,
    `_created_date`         timestamp       not null,
    `_created_by`           string          not null,
    `_updated_date`         timestamp       not null,
    `_updated_by`           string          not null,
    constraint `dim_product_pk` primary key (
        `product_key`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by auto;
create table if not exists `dw`.`fact_sales` (
    `customer_key`          bigint          not null,
    `product_key`           bigint          not null,
    `store_key`             bigint          not null,
    `date_key`              date            not null,
    `time_key`              int             not null,
    `unit`                  int             not null,
    `price`                 decimal(6,4)    not null,
    `amount`                decimal(10,4)   not null,
    `discount`              decimal(6,4)    not null,
    `_job_run_id`           bigint          not null,
    `_created_date`         timestamp       not null,
    `_created_by`           string          not null,
    `_updated_date`         timestamp       not null,
    `_updated_by`           string          not null,
    constraint `fact_sales_pk` primary key (
        `customer_key`,
        `product_key`,
        `store_key`,
        `date_key`,
        `time_key`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by auto;
create table if not exists `dw`.`dim_customer` (
    `customer_key`          bigint generated always as identity,
    `customer_id`           bigint          not null,
    `first_name`            string          not null,
    `last_name`             string          not null,
    `date_of_brith`         date            not null,
    `gender`                string          not null,
    `_job_run_id`           bigint          not null,
    `_created_date`         timestamp       not null,
    `_created_by`           string          not null,
    `_updated_date`         timestamp       not null,
    `_updated_by`           string          not null,
    constraint `dim_customer_pk` primary key (
        `customer_key`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by auto;
create or replace function stage.cleanse_first_name(first_name string)
    returns string
    contains SQL
    comment 'Cleanses a persons first name'
    return regexp_replace(first_name, r'\s+', ' ');
create or replace function stage.cleanse_last_name(last_name string)
    returns string
    contains SQL
    comment 'Cleanses a persons first name'
    return regexp_replace(last_name, r'\s+', ' ');
create or replace view source.scotland_sales as

select *
from source._scotland_sales;
create or replace view source.product as

select *
from source._product;
create or replace view source.customer as

select
`customer_id`,
stage.cleanse_first_name(`first_name`) as `first_name`,
stage.cleanse_last_name(`last_name`) as `last_name`,
`date_of_brith`,
`gender`,
`_job_run_id`,
`_created_date`,
`_created_by`,
`_updated_date`,
`_updated_by`           
from source._customer;
create or replace view source.ireland_sales as

select *
from source._ireland_sales;
create or replace view source.wales_sales as

select *
from source._wales_sales;
create or replace view source.store as

select *
from source._store;
create or replace view source.england_sales as

select *
from source._england_sales;
create or replace view stage.dw_fact_sales as

select * from stage._dw_fact_sales;
create or replace view stage.dw_dim_product as

select * from stage._dw_dim_product;
create or replace view stage.dw_dim_customer as

select * from stage._dw_dim_customer;
create or replace view stage.dw_dim_store as

select * from stage._dw_dim_store;
CREATE OR REPLACE PROCEDURE dw.load_dim_product()
    LANGUAGE SQL
    SQL SECURITY INVOKER
    COMMENT 'Load product dimension table'
    AS BEGIN

        MERGE INTO dw.dim_product AS dst
        USING (
            select 
                `product_id`   ,
                `sku`          ,
                `name`         ,
                `sub_category` ,
                `category`     ,
                `_job_run_id`  ,
                `_created_date`,
                `_created_by`  ,
                `_updated_date`,
                `_updated_by`           
            from stage.dw_dim_product
        ) AS src
        ON src.product_id = src.product_id
        WHEN MATCHED THEN
        UPDATE SET
            `product_id`   = src.`product_id`   ,
            `sku`          = src.`sku`          ,
            `name`         = src.`name`         ,
            `sub_category` = src.`sub_category` ,
            `category`     = src.`category`     ,
            `_job_run_id`  = src.`_job_run_id`  ,
            `_created_date`= src.`_created_date`,
            `_created_by`  = src.`_created_by`  ,
            `_updated_date`= src.`_updated_date`,
            `_updated_by`  = src.`_updated_by`
        WHEN NOT MATCHED
        THEN INSERT (
            `product_id`   ,
            `sku`          ,
            `name`         ,
            `sub_category` ,
            `category`     ,
            `_job_run_id`  ,
            `_created_date`,
            `_created_by`  ,
            `_updated_date`,
            `_updated_by`  
        )
        VALUES (
            src.`product_id`   ,
            src.`sku`          ,
            src.`name`         ,
            src.`sub_category` ,
            src.`category`     ,
            src.`_job_run_id`  ,
            src.`_created_date`,
            src.`_created_by`  ,
            src.`_updated_date`,
            src.`_updated_by`  
        );



    END;
CREATE OR REPLACE PROCEDURE dw.load_dim_store()
    LANGUAGE SQL
    SQL SECURITY INVOKER
    COMMENT 'Load store dimension table'
    AS BEGIN

        MERGE INTO dw.dim_store AS dst
        USING (
            select 
                `store_id`        ,      
                `store_name`      ,      
                `address_line_1`  ,      
                `address_line_2`  ,      
                `address_line_3`  ,      
                `postcode`        ,      
                `county`          ,      
                `region`          ,      
                `country`         ,      
                `_job_run_id`     ,      
                `_created_date`   ,      
                `_created_by`     ,      
                `_updated_date`   ,      
                `_updated_by`           
            from stage.dw_dim_store
        ) AS src
        ON src.store_id = src.store_id
        WHEN MATCHED THEN
        UPDATE SET
            `store_id`       = src.`store_id`      ,      
            `store_name`     = src.`store_name`    ,      
            `address_line_1` = src.`address_line_1`,      
            `address_line_2` = src.`address_line_2`,      
            `address_line_3` = src.`address_line_3`,      
            `postcode`       = src.`postcode`      ,      
            `county`         = src.`county`        ,      
            `region`         = src.`region`        ,      
            `country`        = src.`country`       ,      
            `_job_run_id`    = src.`_job_run_id`   ,      
            `_created_date`  = src.`_created_date` ,      
            `_created_by`    = src.`_created_by`   ,      
            `_updated_date`  = src.`_updated_date` ,      
            `_updated_by`    = src.`_updated_by`   
        WHEN NOT MATCHED
        THEN INSERT (
            `store_id`      ,
            `store_name`    ,
            `address_line_1`,
            `address_line_2`,
            `address_line_3`,
            `postcode`      ,
            `county`        ,
            `region`        ,
            `country`       ,
            `_job_run_id`   ,
            `_created_date` ,
            `_created_by`   ,
            `_updated_date` ,
            `_updated_by`    
        )
        VALUES (
            src.`store_id`      ,
            src.`store_name`    ,
            src.`address_line_1`,
            src.`address_line_2`,
            src.`address_line_3`,
            src.`postcode`      ,
            src.`county`        ,
            src.`region`        ,
            src.`country`       ,
            src.`_job_run_id`   ,
            src.`_created_date` ,
            src.`_created_by`   ,
            src.`_updated_date` ,
            src.`_updated_by`    
        );



    END;
CREATE OR REPLACE PROCEDURE dw.load_dim_customer()
    LANGUAGE SQL
    SQL SECURITY INVOKER
    COMMENT 'Load customer dimension table'
    AS BEGIN
        SET first_name = stage.cleanse_first_name(" shaun ");
        SET last_name = stage.cleanse_last_name(" ryan ");


        MERGE INTO dw.dim_customer AS dst
        USING (
            select 
                `customer_id`  ,
                `first_name`   ,
                `last_name`    ,
                `date_of_brith`,
                `gender`       ,
                `_job_run_id`  ,
                `_created_date`,
                `_created_by`  ,
                `_updated_date`,
                `_updated_by`
            from stage.dw_dim_customer
        ) AS src
        ON src.customer_id = src.customer_id
        WHEN MATCHED THEN
        UPDATE SET
            `customer_id`  = src.`customer_id`  ,
            `first_name`   = src.`first_name`   ,
            `last_name`    = src.`last_name`    ,
            `date_of_brith`= src.`date_of_brith`,
            `gender`       = src.`gender`       ,
            `_job_run_id`  = src.`_job_run_id`  ,
            `_created_date`= src.`_created_date`,
            `_created_by`  = src.`_created_by`  ,
            `_updated_date`= src.`_updated_date`,
            `_updated_by`  = src.`_updated_by`
        WHEN NOT MATCHED
        THEN INSERT (
            `customer_id`  ,
            `first_name`   ,
            `last_name`    ,
            `date_of_brith`,
            `gender`       ,
            `_job_run_id`  ,
            `_created_date`,
            `_created_by`  ,
            `_updated_date`,
            `_updated_by`
        )
        VALUES (
            src.`customer_id`  ,
            src.`first_name`   ,
            src.`last_name`    ,
            src.`date_of_brith`,
            src.`gender`       ,
            src.`_job_run_id`  ,
            src.`_created_date`,
            src.`_created_by`  ,
            src.`_updated_date`,
            src.`_updated_by`
        );



    END;