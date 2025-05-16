import sys
import logging

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, expr

from pyspark.ml.recommendation import ALS

# 接收從外部傳入的參數
SPARK_APP_NAME = sys.argv[1]
GCP_PROJECT_ID = sys.argv[2]
BUCKET_NAME = sys.argv[3]

spark = SparkSession.builder \
    .appName(SPARK_APP_NAME) \
    .getOrCreate()

# 計算每個用戶購買每個商品的次數
sales = spark.read.format("bigquery") \
            .option("table", "datacamp-nytaxi-dbt-2025.prod_silver_layer.stg_sales") \
            .load()
user_train = sales.filter((sales.SalesDate.isNotNull())) \
            .select("CustomerID", "ProductID") \
            .groupBy("CustomerID", "ProductID") \
            .agg(count("*").alias("frequency"))

# 設定 ALS 模型
als = ALS(
    userCol="CustomerID",
    itemCol="ProductID",
    ratingCol="frequency",
    coldStartStrategy="drop", # 處理新用戶或新商品的策略
    nonnegative=True,         # 確保隱因子非負
    implicitPrefs=True,       # 表明我們的評分是隱式的 (購買頻率)
    seed=425
)
# 訓練模型
als_model = als.fit(user_train)

# 設定要為每個用戶推薦的商品數量
num_recommendations = 3
# 為所有用戶生成推薦
user_recommendation = als_model.recommendForAllUsers(num_recommendations)
# 顯示推薦結果的前幾筆資料
# *[...]: 加上 * 就是把這個 list 中的每個元素作為 select() 的獨立引數傳入。
# expr(...): expr() 會產生一個 Spark SQL 表達式。
# *[expr(...)] 的作用是unpack一個 list of expressions，讓它們成為 select() 函式的多個引數
user_recs_flat = user_recommendation.select(
    col("CustomerID"),
    *[expr(f"recommendations[{i}].ProductID").alias(f"recommend_{i+1}") for i in range(num_recommendations)]
)

# 將數據寫入 BigQuery 時，需要使用 GCS Bucket 作為臨時的儲存空間來中轉數據。

user_recs_flat.write \
    .format("bigquery") \
    .option("table", f"{GCP_PROJECT_ID}.prod_silver_layer.fct_recommend") \
    .option("temporaryGcsBucket", f"{BUCKET_NAME}") \
    .mode("overwrite") \
    .save()

# 停止 SparkSession (當你完成所有操作後再取消註解)
# spark.stop()