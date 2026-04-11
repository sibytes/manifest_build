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
)