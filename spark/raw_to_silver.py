import os
import logging
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat_ws, year, month, dayofmonth, dayofweek

from raw_data_schema import categories_schema, cities_schema, countries_schema, customers_schema, employees_schema, products_schema, sales_schema

# 使用 pathlib 來指定 storage.json 的絕對路徑
storage_json_path = Path(__file__).resolve().parent / 'secrets' / 'storage.json'
# 將金鑰路徑設置為環境變數
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(storage_json_path)

# 設定 logger，寫入外部檔案
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s - %(message)s',
    handlers=[
        logging.FileHandler("etl_log.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GrocerySalesETL")

# 設定資料來源與輸出位置
input_path = "gs://decamp_project_sample/raw_data/"
output_path = "gs://decamp_project_sample/cleaned/"

# 載入資料集（加上例外處理與日誌）
def read_csv_with_schema(file_name, schema):
    try:
        df = spark.read.csv(input_path + file_name, header=True, schema=schema)
        logger.info(f"Successfully read: {file_name}")
        return df
    except Exception as e:
        logger.error(f"Failed to read {file_name}: {str(e)}")
        return None

# 初始化 SparkSession
spark = SparkSession.builder \
    .appName("Grocery Sales ETL") \
    .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", "/path/to/secrets/storage.json") \
    .getOrCreate()

logger.info("SparkSession initialized")

# 載入資料集
logger.info("Reading CSV files with predefined schemas")
categories = read_csv_with_schema("categories.csv", categories_schema)
cities = read_csv_with_schema("cities.csv", cities_schema)
countries = read_csv_with_schema("countries.csv", countries_schema)
customers = read_csv_with_schema("customers.csv", customers_schema)
employees = read_csv_with_schema("employees.csv", employees_schema)
products = read_csv_with_schema("products.csv", products_schema)
sales = read_csv_with_schema("sales.csv", sales_schema)

# 確保所有資料都有成功載入
if None in [categories, cities, countries, customers, employees, products, sales]:
    logger.error("One or more datasets failed to load. ETL process terminated.")
    spark.stop()
    exit(1)

logger.info("Joining customer data with city and country")
customers_full = customers \
    .join(cities, customers.cityID == cities.CityID, "left") \
    .join(countries, cities.CountryID == countries.CountryID, "left") \
    .withColumn("CustomerFullName", concat_ws(" ", "FirstName", "MiddleInitial", "LastName")) \
    .withColumn("Region", concat_ws(" - ", "CountryName", "CityName")) \
    .select("CustomerID", "CustomerFullName", "CityName", "CountryName", "Region")

logger.info("Joining employee data with city")
employees_full = employees \
    .join(cities, employees.CityID == cities.CityID, "left") \
    .withColumn("EmployeeFullName", concat_ws(" ", "FirstName", "MiddleInitial", "LastName")) \
    .select("EmployeeID", "EmployeeFullName", "CityName")

logger.info("Joining product data with categories")
products_full = products \
    .join(categories, products.CategoryID == categories.CategoryID, "left") \
    .select("ProductID", "ProductName", "Price", "Class", "Resistant", "IsAllergic", "VitalityDays", "CategoryName")

logger.info("Building enriched sales table")
sales_enriched = sales \
    .join(customers_full, "CustomerID", "left") \
    .join(employees_full, sales.SalesPersonID == employees_full.EmployeeID, "left") \
    .join(products_full, "ProductID", "left") \
    .withColumn("GrossRevenue", col("Quantity") * col("Price")) \
    .withColumn("DiscountAmount", col("GrossRevenue") - col("TotalPrice")) \
    .withColumn("Year", year("SalesDate")) \
    .withColumn("Month", month("SalesDate")) \
    .withColumn("Day", dayofmonth("SalesDate")) \
    .withColumn("Weekday", dayofweek("SalesDate")) \
    .select(
        "SalesID", "TransactionNumber", "SalesDate", "Year", "Month", "Day", "Weekday",
        "CustomerID", "CustomerFullName", "Region", "CountryName", "CityName",
        "SalesPersonID", "EmployeeFullName",
        "ProductID", "ProductName", "CategoryName", "Class", "Resistant", "IsAllergic", "VitalityDays",
        "Quantity", "Price", "GrossRevenue", "Discount", "DiscountAmount", "TotalPrice"
    )

logger.info("Writing enriched data to GCS as Parquet")
sales_enriched.write.mode("overwrite").parquet(output_path + "sales_fact_cleaned.parquet")

logger.info("ETL Completed and Saved to GCS.")
