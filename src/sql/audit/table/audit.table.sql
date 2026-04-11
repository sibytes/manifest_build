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
)