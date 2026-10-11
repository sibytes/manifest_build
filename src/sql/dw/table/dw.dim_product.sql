create table if not exists `dw`.`dim_product` (
    `product_key`          bigint generated always as identity,
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
        `product_key`,
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by (auto)

