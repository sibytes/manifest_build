create or replace view source.customer as

select
`customer_id`,
stage.cleanse_first_name(`first_name`) as `first_name`,
stage.cleanse_last_name(`last_name`) as `last_name`,
`date_of_brith`,
`gender`,
`_job_run_id`,
`_created_date`,
`_created_by`,
`_updated_date`,
`_updated_by`           
from source._customer;