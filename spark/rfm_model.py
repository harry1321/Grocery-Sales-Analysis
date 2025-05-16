import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, max as spark_max, datediff, countDistinct, sum as spark_sum, lit, when

from pyspark.ml.feature import VectorAssembler, RobustScaler
from pyspark.ml.clustering import KMeans

# Read args
SPARK_APP_NAME = sys.argv[1]
GCP_PROJECT_ID = sys.argv[2]
BUCKET_NAME = sys.argv[3]
gold = "prod_gold_layer"

# Get SparkSession
spark = SparkSession.builder \
    .appName(SPARK_APP_NAME) \
    .getOrCreate()

# Read data from GBQ
df_sales = spark.read.format("bigquery") \
    .option("table", "datacamp-nytaxi-dbt-2025.prod_grocery_data.sales") \
    .load()

df_products = spark.read.format("bigquery") \
    .option("table", "datacamp-nytaxi-dbt-2025.prod_grocery_data.products") \
    .option("viewsEnabled", "true") \
    .load()

# Remove NULL values
df_sales = df_sales.dropna()

# Calculate RFM score
df_sales = df_sales.select("SalesID", "CustomerID", "ProductID", "Quantity", "Discount", "SalesDate") \
    .join(df_products.select("ProductID", "Price"), on="ProductID", how="inner")

df_sales = df_sales.withColumn("TotalPrice", col("Price") * col("Discount") * col("Quantity"))
last_date = df_sales.select(spark_max("SalesDate")).collect()[0][0]

df_recency = df_sales.filter(col("Quantity") > 0) \
    .groupBy("CustomerID") \
    .agg(spark_max("SalesDate").alias("LastPurchaseTime")) \
    .withColumn("Recency", datediff(lit(last_date), col("LastPurchaseTime")))

df_frequency = df_sales.filter(col("Quantity") > 0) \
    .groupBy("CustomerID") \
    .agg(countDistinct("SalesID").alias("Frequency"))

df_monetary = df_sales.groupBy("CustomerID") \
    .agg(spark_sum("TotalPrice").alias("Monetary"))

df_rfm = df_recency.select("CustomerID", "Recency") \
    .join(df_frequency, on="CustomerID") \
    .join(df_monetary, on="CustomerID")

# Standarization with RobustScaler
assembler = VectorAssembler(inputCols=["Recency", "Frequency", "Monetary"], outputCol="features_raw")
df_rfm_assembled = assembler.transform(df_rfm)

scaler = RobustScaler(inputCol="features_raw", outputCol="features")
scaler_model = scaler.fit(df_rfm_assembled)
df_rfm_scaled = scaler_model.transform(df_rfm_assembled)

# Clustering with 4 clusters using K-means
kmeans = KMeans(k=4, seed=42, featuresCol="features", predictionCol="Cluster")
model = kmeans.fit(df_rfm_scaled)
df_clustered = model.transform(df_rfm_scaled)


# Convert cluster number to segmentation label
df_result = df_clustered.select("CustomerID", "Recency", "Frequency", "Monetary", "Cluster") \
    .withColumn(
    "Segmentation",
    when(df_clustered.Cluster == 0, "Champ")
    .when(df_clustered.Cluster == 1, "Potential Loyalist")
    .when(df_clustered.Cluster == 2, "Needs Attention")
    .when(df_clustered.Cluster == 3, "Promising")
    .otherwise("Unknown")
)

# write result to GBQ
df_result.write.format("bigquery") \
    .option("table", f"datacamp-nytaxi-dbt-2025.prod_gold_layer.fct_rfm_cluster") \
    .option("temporaryGcsBucket", f"decamp_project_sample") \
    .mode("overwrite") \
    .save()