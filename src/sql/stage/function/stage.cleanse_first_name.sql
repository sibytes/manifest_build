create function stage.cleanse_first_name(first_name string)
    returns string
    contains SQL
    comment 'Cleanses a persons first name'
    return regexp_replace(first_name, r'\s+', ' ');