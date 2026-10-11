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
        `customer_key`,
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by (auto)

