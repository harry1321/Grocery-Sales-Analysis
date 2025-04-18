-- models/gold_layer/fct_customer_sales_behavior.sql

WITH sales_data AS (

    SELECT
        s.CustomerID,
        --c.CustomerName,
        s.TransactionNumber,
        p.CategoryName,
        s.Quantity,
        (s.Quantity*p.Price*(1-s.Discount)) AS TotalPrice,
        s.Discount,
        CASE
            WHEN s.Discount > 0 THEN 1
            ELSE 0
        END AS DiscountOrNot,
        CAST(SalesDate AS DATE) AS PurchaseDate

    FROM {{ ref('stg_sales') }} s
    LEFT JOIN {{ ref('dim_products') }} p 
        ON p.ProductID = s.ProductID

),
customer_category_counts AS (
    SELECT
        CustomerID,
        --CustomerName,
        CategoryName,
        COUNT(*) AS purchase_count
    FROM sales_data
    GROUP BY CustomerID, CategoryName
),

customer_category_preference AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY CustomerID
            ORDER BY purchase_count DESC
        ) AS rn
    FROM customer_category_counts
),

-- customer_purchase_dates AS (
--     SELECT
--         CustomerID,
--         LAG(PurchaseDate, 1, NULL) OVER 
--         (
--             PARTITION BY CustomerID
--             ORDER BY PurchaseDate
--         ) AS PreviousPurchaseDate
--     FROM sales_data
-- ),

weekly_activity AS (
    SELECT
        CustomerID,
        DATE_TRUNC(PurchaseDate, WEEK) AS PurchaseWeek,
        COUNT(TransactionNumber) AS WeeklyOrders,
        SUM(TotalPrice) AS WeeklySpend
    FROM sales_data
    GROUP BY CustomerID, PurchaseWeek
),

aggregated AS (

    SELECT
        sd.CustomerID,

        COUNT(DISTINCT sd.TransactionNumber) AS TotalOrders,
        SUM(sd.TotalPrice) AS TotalSpent,
        ROUND(AVG(sd.TotalPrice), 2) AS AverageOrderValue,
        ROUND(AVG(sd.Quantity), 2) AS AverageBasketSize,
        
        ROUND(SUM(sd.DiscountOrNot) * 1.0 / COUNT(DISTINCT sd.TransactionNumber),2) AS DiscountRate,
        ROUND((SUM(CASE WHEN sd.Discount > 0 THEN sd.TotalPrice ELSE 0 END) * 1.0) / SUM(sd.TotalPrice),2) AS DiscountAmountRate,
        
        MAX(CASE WHEN ccp.rn = 1 THEN ccp.CategoryName ELSE NULL END) AS MostFrequentCategory,

        -- AVG(DATE_DIFF(sd.PurchaseDate, cpd.PreviousPurchaseDate, DAY)) AS AveragePurchaseInterval,

        ROUND(AVG(wk.WeeklyOrders),2) AS AverageWeeklyOrders,
        ROUND(AVG(wk.WeeklySpend),2) AS AverageWeeklySpend,

        MIN(sd.PurchaseDate) AS FirstPurchaseDate,
        MAX(sd.PurchaseDate) AS LastPurchaseDate,
        CASE
            WHEN COUNT(DISTINCT sd.TransactionNumber) > 1 THEN true
            ELSE false
        END AS IsRepeatCustomer

    FROM sales_data sd

    LEFt JOIN customer_category_preference ccp ON sd.CustomerID = ccp.CustomerID
    LEFT JOIN weekly_activity wk ON sd.CustomerID = wk.CustomerID
    --LEFT JOIN customer_purchase_dates cpd ON sd.CustomerID = cpd.CustomerID
    GROUP BY sd.CustomerID

)

SELECT dim_c.CustomerName, a.* EXCEPT (a.CustomerID)
FROM aggregated a
LEFT JOIN {{ ref("dim_customers") }} dim_c ON dim_c.CustomerID = a.CustomerID

-- dbt build --select <model.sql> --vars '{'is_test_run: true}'
{% if var('is_test_run', default=false) %}

  limit 100

{% endif %}