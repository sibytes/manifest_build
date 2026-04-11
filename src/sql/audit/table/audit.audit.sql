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
)