from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DecimalType, DateType, TimestampType
# 定義 schema
categories_schema = StructType([
    StructField("CategoryID", IntegerType(), True),
    StructField("CategoryName", StringType(), True)
])

cities_schema = StructType([
    StructField("CityID", IntegerType(), True),
    StructField("CityName", StringType(), True),
    StructField("Zipcode", DecimalType(5, 0), True),
    StructField("CountryID", IntegerType(), True)
])

countries_schema = StructType([
    StructField("CountryID", IntegerType(), True),
    StructField("CountryName", StringType(), True),
    StructField("CountryCode", StringType(), True)
])

customers_schema = StructType([
    StructField("CustomerID", IntegerType(), True),
    StructField("FirstName", StringType(), True),
    StructField("MiddleInitial", StringType(), True),
    StructField("LastName", StringType(), True),
    StructField("cityID", IntegerType(), True),
    StructField("Address", StringType(), True)
])

employees_schema = StructType([
    StructField("EmployeeID", IntegerType(), True),
    StructField("FirstName", StringType(), True),
    StructField("MiddleInitial", StringType(), True),
    StructField("LastName", StringType(), True),
    StructField("BirthDate", DateType(), True),
    StructField("Gender", StringType(), True),
    StructField("CityID", IntegerType(), True),
    StructField("HireDate", DateType(), True)
])

products_schema = StructType([
    StructField("ProductID", IntegerType(), True),
    StructField("ProductName", StringType(), True),
    StructField("Price", DecimalType(4, 0), True),
    StructField("CategoryID", IntegerType(), True),
    StructField("Class", StringType(), True),
    StructField("ModifyDate", DateType(), True),
    StructField("Resistant", StringType(), True),
    StructField("IsAllergic", StringType(), True),
    StructField("VitalityDays", DecimalType(3, 0), True)
])

sales_schema = StructType([
    StructField("SalesID", IntegerType(), True),
    StructField("SalesPersonID", IntegerType(), True),
    StructField("CustomerID", IntegerType(), True),
    StructField("ProductID", IntegerType(), True),
    StructField("Quantity", IntegerType(), True),
    StructField("Discount", DecimalType(10, 2), True),
    StructField("TotalPrice", DecimalType(10, 2), True),
    StructField("SalesDate", TimestampType(), True),
    StructField("TransactionNumber", StringType(), True)
])