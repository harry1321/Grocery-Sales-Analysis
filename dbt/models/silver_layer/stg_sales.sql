{{ config(
    materialized='incremental',
    unique_key='SalesID',
    partition_by={
        "field": "SalesDay",
        "data_type": "date"
    },
    cluster_by=['CustomerID', 'ProductID']
) }}

SELECT
    SalesID,
    SalesPersonID,
    CustomerID,
    ProductID,
    ROUND(COALESCE(Quantity,0),2) AS Quantity,
    ROUND(COALESCE(Discount,0),2) AS Discount,
    SalesDate,
    CAST(SalesDate AS DATE) AS SalesDay,
    TransactionNumber
FROM {{source("raw_data","sales")}}
WHERE
    SalesDate IS NOT NULL
-- dbt build --select <model.sql> --vars '{'is_test_run: true}'
{% if var('is_test_run', default=false) %}

  limit 100

{% endif %}