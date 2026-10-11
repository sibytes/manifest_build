CREATE OR REPLACE PROCEDURE dw.load_dim_customer()
    LANGUAGE SQL
    SQL SECURITY INVOKER
    COMMENT 'Load customer dimension table'
    AS BEGIN
        SET first_name = stage.cleanse_first_name(" shaun ");
        SET last_name = stage.cleanse_last_name(" ryan ");

        select 
            `customer_id`  ,
            `first_name`   ,
            `last_name`    ,
            `date_of_brith`,
            `gender`       ,
            `_job_run_id`  ,
            `_created_date`,
            `_created_by`  ,
            `_updated_date`,
            `_updated_by`
        from stage.dw_dim_customer

    END;