SELECT
    SalesID,
    SalesPersonID,
    CustomerID,
    ProductID,
    CAST(COALESCE(Quantity,0) AS DECIMAL(10,2)) AS Quantity,
    CAST(COALESCE(Discount,0) AS DECIMAL(10,2)) AS Discount,
    EXTRACT(YEAR from SalesDate) AS SalesYear,
    EXTRACT(MONTH from SalesDate) AS SalesMonth,
    EXTRACT(DAY from SalesDate) AS SalesDay,
    EXTRACT(HOUR from SalesDate) AS SalesTime,
    TransactionNumber
FROM {{source("raw_data","sales")}}

-- dbt build --select <model.sql> --vars '{'is_test_run: true}'
{% if var('is_test_run', default=false) %}

  limit 100

{% endif %}