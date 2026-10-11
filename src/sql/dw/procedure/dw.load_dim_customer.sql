CREATE OR REPLACE PROCEDURE dw.load_dim_customer()
    LANGUAGE SQL
    SQL SECURITY INVOKER
    COMMENT 'Load customer dimension table'
    AS BEGIN
        SET first_name = stage.cleanse_first_name(" shaun ");
        SET last_name = stage.cleanse_last_name(" ryan ");


        MERGE INTO dw.dim_customer AS dst
        USING (
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
        ) AS src
        ON src.customer_id = src.customer_id
        WHEN MATCHED THEN
        UPDATE SET
            `customer_id`  = src.`customer_id`  ,
            `first_name`   = src.`first_name`   ,
            `last_name`    = src.`last_name`    ,
            `date_of_brith`= src.`date_of_brith`,
            `gender`       = src.`gender`       ,
            `_job_run_id`  = src.`_job_run_id`  ,
            `_created_date`= src.`_created_date`,
            `_created_by`  = src.`_created_by`  ,
            `_updated_date`= src.`_updated_date`,
            `_updated_by`  = src.`_updated_by`
        WHEN NOT MATCHED
        THEN INSERT (
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
        )
        VALUES (
            src.`customer_id`  ,
            src.`first_name`   ,
            src.`last_name`    ,
            src.`date_of_brith`,
            src.`gender`       ,
            src.`_job_run_id`  ,
            src.`_created_date`,
            src.`_created_by`  ,
            src.`_updated_date`,
            src.`_updated_by`
        );



    END;