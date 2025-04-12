SELECT
    p.ProductID,
    p.ProductName,
    ROUND(COALESCE(p.Price,0),4) AS Price,
    ca.CategoryName,
    p.Class,
    p.Resistant,
    p.IsAllergic,
    p.VitalityDays
FROM {{source("raw_data","products")}} AS p
JOIN {{ref("categories")}} AS ca
    ON ca.CategoryID = p.CategoryID

-- dbt build --select <model.sql> --vars '{'is_test_run: true}'
{% if var('is_test_run', default=false) %}

  limit 100

{% endif %}