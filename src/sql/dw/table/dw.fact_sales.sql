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
cluster by (auto)