import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# 接收從外部傳入的參數
SPARK_APP_NAME = sys.argv[1]
GCP_PROJECT_ID = sys.argv[2]
BUCKET_NAME = sys.argv[3]
silver = "prod_silver_layer"
gold = "prod_gold_layer"

# 建立 SparkSession
spark = SparkSession.builder \
    .appName(SPARK_APP_NAME) \
    .getOrCreate()

# 讀取 customers, products, recommend 資料
customers_df = spark.read.format("bigquery") \
    .option("table", f"{GCP_PROJECT_ID}.{silver}.dim_customers") \
    .option("viewsEnabled", "true") \
    .load()
products_df = spark.read.format("bigquery") \
    .option("table", f"{GCP_PROJECT_ID}.{silver}.dim_products") \
    .option("viewsEnabled", "true") \
    .load()
recommend_df = spark.read.format("bigquery") \
    .option("table", f"{GCP_PROJECT_ID}.{silver}.stg_recommend") \
    .load()

# 使用別名避免重複 join 出錯
p1 = products_df.alias("p1")
p2 = products_df.alias("p2")
p3 = products_df.alias("p3")

# 加入推薦商品名稱
recommend_with_names = recommend_df \
    .join(p1, recommend_df["recommend_1"] == col("p1.ProductID"), "left") \
    .join(p2, recommend_df["recommend_2"] == col("p2.ProductID"), "left") \
    .join(p3, recommend_df["recommend_3"] == col("p3.ProductID"), "left") \
    .select(
        "CustomerID",
        col("p1.ProductName").alias("RecommendProduct1"),
        col("p2.ProductName").alias("RecommendProduct2"),
        col("p3.ProductName").alias("RecommendProduct3")
    )

# 加入顧客姓名
final_df = recommend_with_names \
    .join(customers_df.select("CustomerID", "CustomerName"), on="CustomerID", how="left") \
    .select(
        "CustomerName",
        "RecommendProduct1",
        "RecommendProduct2",
        "RecommendProduct3"
    )

# 將結果寫回 BigQuery 成為新表格
final_df.write.format("bigquery") \
    .option("table", f"{GCP_PROJECT_ID}.{gold}.mart_recommend") \
    .option("temporaryGcsBucket", f"{BUCKET_NAME}") \
    .mode("overwrite") \
    .save()
