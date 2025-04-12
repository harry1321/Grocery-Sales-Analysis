-- models/gold_layer/fct_customer_sales_behavior.sql

WITH sales_data AS (

    SELECT
        c.CustomerName,
        c.CityName AS City,
        c.CountryName AS Country,
        s.TransactionNumber,
        s.Quantity,
        (s.Quantity*p.Price*s.Discount) AS TotalPrice,
        s.Discount,
        s.SalesDate

    FROM {{ ref('stg_sales') }} s
    LEFT JOIN {{ ref('dim_customers') }} c 
        ON s.CustomerID = c.CustomerID
    LEFT JOIN {{ ref('dim_products') }} p 
        ON p.ProductID = s.ProductID

),

aggregated AS (

    SELECT
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
    GROUP BY CustomerName, City, Country

)

SELECT *
FROM aggregated

-- dbt build --select <model.sql> --vars '{'is_test_run: true}'
{% if var('is_test_run', default=false) %}

  limit 100

{% endif %}