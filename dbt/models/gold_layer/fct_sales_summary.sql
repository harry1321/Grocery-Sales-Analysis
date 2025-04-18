SELECT
    s.SalesID,
    s.SalesDate,
    EXTRACT(YEAR from s.SalesDate) AS SalesYear,
    EXTRACT(MONTH from s.SalesDate) AS SalesMonth,
    EXTRACT(DAY from s.SalesDate) AS SalesDay,
    EXTRACT(HOUR from s.SalesDate) AS SalesTime,
    e.EmployeeName AS Employee,
    c.CustomerName AS Customer,
    p.ProductName,
    p.CategoryName,
    c.CityName,
    c.CountryName,
    s.Quantity,
    p.Price,
    s.Discount,
    ROUND(s.Quantity*p.Price) AS GrossRevenue,
    ROUND(s.Quantity*p.Price*(1-s.Discount)) AS NetRevenue

FROM {{ ref("stg_sales") }} AS s
JOIN {{ ref("dim_customers") }} AS c 
    ON s.CustomerID = c.CustomerID
JOIN {{ ref("dim_employees") }} AS e 
    ON s.SalesPersonID = e.EmployeeID
JOIN {{ ref("dim_products") }} AS p
    ON p.ProductID = s.ProductID

-- dbt build --select <model.sql> --vars '{'is_test_run: true}'
{% if var('is_test_run', default=false) %}

  limit 100

{% endif %}