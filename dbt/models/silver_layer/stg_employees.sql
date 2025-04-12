SELECT
    EmployeeID,
    CONCAT(FirstName,LastName) AS EmployeeName,
    CASE 
        WHEN Gender='M' THEN 'Male'
        WHEN Gender='F' THEN 'Female'
        ELSE NULL AS Gender,
    CAST(HireDate, DATE) AS HireDate,
    CityID
FROM {{source("raw_data","employees")}}

-- dbt build --select <model.sql> --vars '{'is_test_run: true}'
{% if var('is_test_run', default=false) %}

  limit 100

{% endif %}