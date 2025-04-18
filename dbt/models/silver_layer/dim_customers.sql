SELECT
    cus.CustomerID,
    CONCAT(cus.FirstName,' ',cus.LastName,'-',cus.CustomerID) AS CustomerName,
    ci.CityName,
    co.CountryName,
    cus.Address
FROM {{source("raw_data","customers")}} AS cus
JOIN {{ref("cities")}} AS ci 
    ON ci.CityID = cus.CityID
JOIN {{ref("countries")}} AS co
    ON co.CountryID = ci.CountryID

-- dbt build --select <model.sql> --vars '{'is_test_run: true}'
{% if var('is_test_run', default=false) %}

  limit 100

{% endif %}