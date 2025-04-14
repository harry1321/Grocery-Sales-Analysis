from google.cloud import bigquery
from google.cloud.bigquery import SchemaField

dataset_schema = {}
sales = {
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
for k,v in sales.items():
    schema.append(bigquery.SchemaField(k,v))
dataset_schema['sales'] = schema


customers = {
    'CustomerID': 'INTEGER',
    'FirstName': 'STRING',
    'MiddleInitial': 'STRING',
    'LastName': 'STRING',
    'CityID': 'INTEGER',
    'Address': 'STRING'
}
schema = []
for k,v in customers.items():
    schema.append(bigquery.SchemaField(k,v))
dataset_schema['customers'] = schema

employees = {
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
for k,v in employees.items():
    schema.append(bigquery.SchemaField(k,v))
dataset_schema['employees'] = schema

products = {
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
for k,v in products.items():
    schema.append(bigquery.SchemaField(k,v))
dataset_schema['products'] = schema

categories = {
    'CategoryID': 'INTEGER',
    'CategoryName': 'STRING'
}
schema = []
for k,v in categories.items():
    schema.append(bigquery.SchemaField(k,v))
dataset_schema['categories'] = schema

cities = {
    'CityID': 'INTEGER',
    'CityName': 'STRING',
    'Zipcode': 'INTEGER',
    'CountryID': 'INTEGER'
}
schema = []
for k,v in cities.items():
    schema.append(bigquery.SchemaField(k,v))
dataset_schema['cities'] = schema

countries = {
    'CountryID': 'INTEGER',
    'CountryName': 'STRING',
    'CountryCode': 'STRING'
}
schema = []
for k,v in countries.items():
    schema.append(bigquery.SchemaField(k,v))
dataset_schema['countries'] = schema