CREATE OR REPLACE PROCEDURE dw.load_dim_store()
    LANGUAGE SQL
    SQL SECURITY INVOKER
    COMMENT 'Load store dimension table'
    AS BEGIN

        MERGE INTO dw.dim_store AS dst
        USING (
            select 
                `store_id`        ,      
                `store_name`      ,      
                `address_line_1`  ,      
                `address_line_2`  ,      
                `address_line_3`  ,      
                `postcode`        ,      
                `county`          ,      
                `region`          ,      
                `country`         ,      
                `_job_run_id`     ,      
                `_created_date`   ,      
                `_created_by`     ,      
                `_updated_date`   ,      
                `_updated_by`           
            from stage.dw_dim_store
        ) AS src
        ON src.store_id = src.store_id
        WHEN MATCHED THEN
        UPDATE SET
            `store_id`       = src.`store_id`      ,      
            `store_name`     = src.`store_name`    ,      
            `address_line_1` = src.`address_line_1`,      
            `address_line_2` = src.`address_line_2`,      
            `address_line_3` = src.`address_line_3`,      
            `postcode`       = src.`postcode`      ,      
            `county`         = src.`county`        ,      
            `region`         = src.`region`        ,      
            `country`        = src.`country`       ,      
            `_job_run_id`    = src.`_job_run_id`   ,      
            `_created_date`  = src.`_created_date` ,      
            `_created_by`    = src.`_created_by`   ,      
            `_updated_date`  = src.`_updated_date` ,      
            `_updated_by`    = src.`_updated_by`   
        WHEN NOT MATCHED
        THEN INSERT (
            `store_id`      ,
            `store_name`    ,
            `address_line_1`,
            `address_line_2`,
            `address_line_3`,
            `postcode`      ,
            `county`        ,
            `region`        ,
            `country`       ,
            `_job_run_id`   ,
            `_created_date` ,
            `_created_by`   ,
            `_updated_date` ,
            `_updated_by`    
        )
        VALUES (
            src.`store_id`      ,
            src.`store_name`    ,
            src.`address_line_1`,
            src.`address_line_2`,
            src.`address_line_3`,
            src.`postcode`      ,
            src.`county`        ,
            src.`region`        ,
            src.`country`       ,
            src.`_job_run_id`   ,
            src.`_created_date` ,
            src.`_created_by`   ,
            src.`_updated_date` ,
            src.`_updated_by`    
        );



    END;