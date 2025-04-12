SELECT
    s.SalesID,
    s.SalesYear,
    s.SalesMonth,
    s.SalesDate,
    s.SalesTime,
    c.CustomerName,
    p.ProductName,
    p.CategoryName,
    c.CityName,
    c.CountryName,
    s.Quantity,
    p.Price,
    s.Discount,
    ROUND(s.Quantity*p.Price) AS GrossRevenue,
    ROUND(s.Quantity*p.Price*s.Discount) AS NetRevenue

FROM {{ ref("stg_sales") }} AS s
JOIN {{ ref("dim_customers") }} AS c 
    ON s.CustomerID = c.CustomerID
JOIN {{ ref("dim_products") }} AS p
    ON p.ProductID = s.ProductID

-- dbt build --select <model.sql> --vars '{'is_test_run: true}'
{% if var('is_test_run', default=false) %}

  limit 100

{% endif %}