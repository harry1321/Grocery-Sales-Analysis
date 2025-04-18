-- models/marts/fct_employee_performance.sql

WITH sales_data AS (

    SELECT
        e.EmployeeName,
        e.CityName AS City,
        e.CountryName AS Country,
        s.TransactionNumber,
        s.Quantity,
        (s.Quantity*p.Price*(1-s.Discount)) AS TotalPrice,
        s.Discount,
        s.SalesDate
    FROM {{ ref('stg_sales') }} s
    LEFT JOIN {{ ref('dim_employees') }} e 
        ON s.SalesPersonID = e.EmployeeID
    LEFT JOIN {{ ref('dim_products') }} p 
        ON p.ProductID = s.ProductID
),

aggregated AS (

    SELECT
        EmployeeName,
        City,
        Country,
        COUNT(DISTINCT TransactionNumber) AS TotalSales,
        SUM(TotalPrice) AS TotalSaleRev,
        MIN(SalesDate) AS FirstSaleDate,
        MAX(SalesDate) AS LastSaleDate,
        CASE
            WHEN COUNT(DISTINCT TransactionNumber) > 1 THEN true
            ELSE false
        END AS IsRepeatEmployee

    FROM sales_data
    GROUP BY EmployeeName, City, Country

)

SELECT *
FROM aggregated

-- dbt build --select <model.sql> --vars '{'is_test_run: true}'
{% if var('is_test_run', default=false) %}

  limit 100

{% endif %}