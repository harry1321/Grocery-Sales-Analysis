import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# 接收從外部傳入的參數
SPARK_APP_NAME = sys.argv[1]
GCP_PROJECT_ID = sys.argv[2]
silver = "prod_silver_layer"
gold = "prod_gold_layer"

# 建立 SparkSession
spark = SparkSession.builder \
    .appName(SPARK_APP_NAME) \
    .getOrCreate()

# 讀取 customers, products, recommend 資料
customers_df = spark.read.format("bigquery").option("table", f"{GCP_PROJECT_ID}.{silver}.dim_customers").load()
products_df = spark.read.format("bigquery").option("table", f"{GCP_PROJECT_ID}.{silver}.dim_products").load()
recommend_df = spark.read.format("bigquery").option("table", f"{GCP_PROJECT_ID}.{silver}.stg_recommend").load()

# 為每個推薦 ID 加入產品名稱
recommend_with_names = recommend_df \
    .join(products_df.select(col("ProductID").alias("pid1"), col("ProductName").alias("ReommendProduct1")),
          recommend_df["recommend_ProductID_1"] == col("pid1"), "left") \
    .join(products_df.select(col("ProductID").alias("pid2"), col("ProductName").alias("ReommendProduct2")),
          recommend_df["recommend_ProductID_2"] == col("pid2"), "left") \
    .join(products_df.select(col("ProductID").alias("pid3"), col("ProductName").alias("ReommendProduct3")),
          recommend_df["recommend_ProductID_3"] == col("pid3"), "left")

# 加入顧客姓名
final_df = recommend_with_names \
    .join(customers_df.select("CustomerID", "CustomerNam"), on="CustomerID", how="left") \
    .select(
        "CustomerName",
        "ReommendProduct1",
        "ReommendProduct2",
        "ReommendProduct3"
    )

# 將結果寫回 BigQuery 成為新表格
final_df.write.format("bigquery") \
    .option("table", f"{GCP_PROJECT_ID}.{gold}.mart_recommend") \
    .mode("overwrite") \
    .save()
