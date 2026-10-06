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
    constraint `_england_sales` primary key (
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
cluster by (auto)