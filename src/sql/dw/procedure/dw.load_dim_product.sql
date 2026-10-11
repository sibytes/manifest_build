CREATE OR REPLACE PROCEDURE dw.load_dim_product()
    LANGUAGE SQL
    SQL SECURITY INVOKER
    COMMENT 'Load product dimension table'
    AS BEGIN

        MERGE INTO dw.dim_product AS dst
        USING (
            select 
                `product_id`   ,
                `sku`          ,
                `name`         ,
                `sub_category` ,
                `category`     ,
                `_job_run_id`  ,
                `_created_date`,
                `_created_by`  ,
                `_updated_date`,
                `_updated_by`           
            from stage.dw_dim_product
        ) AS src
        ON src.product_id = src.product_id
        WHEN MATCHED THEN
        UPDATE SET
            `product_id`   = src.`product_id`   ,
            `sku`          = src.`sku`          ,
            `name`         = src.`name`         ,
            `sub_category` = src.`sub_category` ,
            `category`     = src.`category`     ,
            `_job_run_id`  = src.`_job_run_id`  ,
            `_created_date`= src.`_created_date`,
            `_created_by`  = src.`_created_by`  ,
            `_updated_date`= src.`_updated_date`,
            `_updated_by`  = src.`_updated_by`
        WHEN NOT MATCHED
        THEN INSERT (
            `product_id`   ,
            `sku`          ,
            `name`         ,
            `sub_category` ,
            `category`     ,
            `_job_run_id`  ,
            `_created_date`,
            `_created_by`  ,
            `_updated_date`,
            `_updated_by`  
        )
        VALUES (
            src.`product_id`   ,
            src.`sku`          ,
            src.`name`         ,
            src.`sub_category` ,
            src.`category`     ,
            src.`_job_run_id`  ,
            src.`_created_date`,
            src.`_created_by`  ,
            src.`_updated_date`,
            src.`_updated_by`  
        );



    END;