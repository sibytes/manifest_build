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
cluster by auto