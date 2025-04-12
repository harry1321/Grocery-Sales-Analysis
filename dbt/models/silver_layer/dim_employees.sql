SELECT
    e.EmployeeID,
    CONCAT(e.FirstName,' ',e.LastName) AS EmployeeName,
    CASE 
        WHEN e.Gender='M' THEN 'Male'
        WHEN e.Gender='F' THEN 'Female'
        ELSE NULL 
    END AS Gender,
    CAST(e.HireDate AS DATE) AS HireDate,
    DATE_DIFF(CURRENT_DATE(), DATE(e.BirthDate), YEAR) AS Age,
    ci.CityName,
    co.CountryName
FROM {{source("raw_data","employees")}} AS e
JOIN {{ ref("cities") }} AS ci
    ON ci.CityID = e.CityID
JOIN {{ref("countries")}} AS co
    ON co.CountryID = ci.CountryID

-- dbt build --select <model.sql> --vars '{'is_test_run: true}'
{% if var('is_test_run', default=false) %}

  limit 100

{% endif %}