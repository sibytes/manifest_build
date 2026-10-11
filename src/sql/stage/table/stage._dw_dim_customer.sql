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
    constraint `_dw_dim_customer` primary key (
        `_job_run_id`,
        `customer_id`
    )
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name'
)
cluster by (auto)