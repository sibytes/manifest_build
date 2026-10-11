create or replace function stage.cleanse_last_name(last_name string)
    returns string
    contains SQL
    comment 'Cleanses a persons first name'
    return regexp_replace(last_name, r'\s+', ' ');