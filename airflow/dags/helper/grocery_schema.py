from google.cloud import bigquery
from google.cloud.bigquery import SchemaField

dataset_schema = {}
sales_dtypes = {
    'SalesID': 'INTEGER',
    'SalesPersonID': 'INTEGER',
    'CustomerID': 'INTEGER',
    'ProductID': 'INTEGER',
    'Quantity': 'INTEGER',
    'Discount': 'FLOAT',
    'TotalPrice': 'FLOAT',
    'SalesDate': 'TIMESTAMP',
    'TransactionNumber': 'STRING'
}
schema = []
for k,v in sales_dtypes.items():
    schema.append(bigquery.SchemaField(k,v))
dataset_schema['sales'] = schema


customers_dtypes = {
    'CustomerID': 'INTEGER',
    'FirstName': 'STRING',
    'MiddleInitial': 'STRING',
    'LastName': 'STRING',
    'CityID': 'INTEGER',
    'Address': 'STRING'
}
schema = []
for k,v in customers_dtypes.items():
    schema.append(bigquery.SchemaField(k,v))
dataset_schema['customers'] = schema

employees_dtypes = {
    'EmployeeID': 'INTEGER',
    'FirstName': 'STRING',
    'MiddleInitial': 'STRING',
    'LastName': 'STRING',
    'BirthDate': 'TIMESTAMP',
    'Gender': 'STRING',
    'CityID': 'INTEGER',
    'HireDate': 'TIMESTAMP'
}
schema = []
for k,v in employees_dtypes.items():
    schema.append(bigquery.SchemaField(k,v))
dataset_schema['employees'] = schema

products_dtypes = {
    'ProductID': 'INTEGER',
    'ProductName': 'STRING',
    'Price': 'FLOAT',
    'CategoryID': 'INTEGER',
    'Class': 'STRING',
    'ModifyDate': 'TIMESTAMP',
    'Resistant': 'STRING',
    'IsAllergic': 'STRING',
    'VitalityDays': 'FLOAT'
}
schema = []
for k,v in products_dtypes.items():
    schema.append(bigquery.SchemaField(k,v))
dataset_schema['products'] = schema

categories_dtypes = {
    'CategoryID': 'INTEGER',
    'CategoryName': 'STRING'
}
schema = []
for k,v in categories_dtypes.items():
    schema.append(bigquery.SchemaField(k,v))
dataset_schema['categories'] = schema

cities_dtypes = {
    'CityID': 'INTEGER',
    'CityName': 'STRING',
    'Zipcode': 'INTEGER',
    'CountryID': 'INTEGER'
}
schema = []
for k,v in cities_dtypes.items():
    schema.append(bigquery.SchemaField(k,v))
dataset_schema['cities'] = schema

countries_dtypes = {
    'CountryID': 'INTEGER',
    'CountryName': 'STRING',
    'CountryCode': 'STRING'
}
schema = []
for k,v in countries_dtypes.items():
    schema.append(bigquery.SchemaField(k,v))
dataset_schema['countries'] = schema