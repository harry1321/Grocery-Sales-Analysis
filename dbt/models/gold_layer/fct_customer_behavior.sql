-- models/marts/fct_customer_sales_behavior.sql

WITH sales_data AS (

    SELECT
        s.CustomerID,
        c.FullName AS CustomerName,
        r.CcityName AS City,
        r.CountryName AS Country,
        s.TransactionNumber,
        s.TotalPrice,
        s.Quantity,
        s.SalesDate
    FROM {{ ref('stg_sales') }} s
    LEFT JOIN {{ ref('stg_customers') }} c ON s.CustomerID = c.CustomerID
    LEFT JOIN {{ ref('dim_regions') }} r ON c.CityID = ci.CityID

),

aggregated AS (

    SELECT
        CustomerID,
        CustomerName,
        City,
        Country,
        COUNT(DISTINCT TransactionNumber) AS TotalOrders,
        SUM(TotalPrice) AS TotalSpent,
        ROUND(AVG(TotalPrice), 2) AS AverageOrderValue,
        ROUND(SUM(Quantity) * 1.0 / COUNT(DISTINCT TransactionNumber), 2) AS AverageBasketSize,
        MIN(SalesDate) AS FirstPurchaseDate,
        MAX(SalesDate) AS LastPurchaseDate,
        CASE
            WHEN COUNT(DISTINCT TransactionNumber) > 1 THEN true
            ELSE false
        END AS IsRepeatCustomer

    FROM sales_data
    GROUP BY CustomerID, CustomerName, CountryName

)

SELECT *
FROM aggregated

-- dbt build --select <model.sql> --vars '{'is_test_run: true}'
{% if var('is_test_run', default=false) %}

  limit 100

{% endif %}