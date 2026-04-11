create table if not exists `audit`.`version` (
    `version`       string      not null,
    `git_version`   string      not null,
    `catalog`       string      not null,
    `component`     bigint      not null,
    `change_set`    date        not null,
    `path`          string      not null,
    `created_date`  timestamp   not null,
    `created_by`    string      not null,
    constraint `version_pk` primary key (`version`)
)
using delta
tblproperties (
  'delta.columnMapping.mode' = 'name',
  'delta.appendOnly' = 'true'
)