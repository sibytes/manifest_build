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
    constraint `_product` primary key (
        `_job_run_id`,
        `product_id`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by (auto)