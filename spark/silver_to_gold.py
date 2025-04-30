import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Read args
SPARK_APP_NAME = sys.argv[1]
GCP_PROJECT_ID = sys.argv[2]
BUCKET_NAME = sys.argv[3]
silver = "prod_silver_layer"
gold = "prod_gold_layer"

# Get SparkSession
spark = SparkSession.builder \
    .appName(SPARK_APP_NAME) \
    .getOrCreate()

# Read customers, products, recommend table from GBQ
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

p1 = products_df.alias("p1")
p2 = products_df.alias("p2")
p3 = products_df.alias("p3")

# join product name
recommend_with_names = recommend_df \
    .join(p1, recommend_df["recommend_1"] == col("p1.ProductID"), "left") \
    .join(p2, recommend_df["recommend_2"] == col("p2.ProductID"), "left") \
    .join(p3, recommend_df["recommend_3"] == col("p3.ProductID"), "left") \
    .select(
        "CustomerID",
        col("p1.ProductName").alias("RecommendProduct1"),
        col("p2.ProductName").alias("RecommendProduct2"),
        col("p3.ProductName").alias("RecommendProduct3")
    ) \
    .distinct()

# Join customer name
final_df = recommend_with_names \
    .join(customers_df.select("CustomerID", "CustomerName"), on="CustomerID", how="left") \
    .select(
        "CustomerName",
        "RecommendProduct1",
        "RecommendProduct2",
        "RecommendProduct3"
    ) \
    .distinct()

# write the result into GBQ
final_df.write.format("bigquery") \
    .option("table", f"{GCP_PROJECT_ID}.{gold}.mart_recommend") \
    .option("temporaryGcsBucket", f"{BUCKET_NAME}") \
    .mode("overwrite") \
    .save()
