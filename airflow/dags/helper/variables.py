import os
from pathlib import Path
import json
from airflow.models import Variable

# Should be using Airflow Variable to get these Global Vars.
# Which are already been setup in the docker-compose.yaml file
# ex: AWS_S3_BUCKET = Variable.get("AWS_S3_BUCKET")
# https://cloud.google.com/storage/docs/samples/storage-transfer-manager-upload-directory#storage_transfer_manager_upload_directory-python

# def load_variables_from_json(json_filepath=None):
#     """Loads Airflow variables from a JSON file.

#     :param json_filepath: The absolute or relative path to the JSON file.
#     """
#     if json_filepath is None:
#         json_filepath = Path(__file__).resolve().parent.parent.parent / 'variables.json'

#     try:
#         with open(json_filepath, 'r') as f:
#             variables_data = json.load(f)
#             for key, value in variables_data.items():
#                 # Airflow Variables store values as strings
#                 Variable.set(key, str(value))
#         print(f"Successfully loaded variables from {json_filepath} into Airflow.")
#     except FileNotFoundError:
#         print(f"Error: JSON file not found at {json_filepath}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
# load_variables_from_json()

GCP_CREDENTIALS_FILE_PATH = Variable.get("GCP_CREDENTIALS_FILE_PATH")
GCP_PROJECT_ID = Variable.get('GCP_PROJECT_ID')
BUCKET_NAME = Variable.get('BUCKET_NAME')
BUCKET_CLASS = Variable.get('BUCKET_CLASS')
BUCKET_LOCATION = Variable.get('BUCKET_LOCATION')
DATASET_NAME = Variable.get('DATASET_NAME')
DBT_ACCOUNT_ID = Variable.get('DBT_ACCOUNT_ID')
DBT_CONN_ID = Variable.get('DBT_CONN_ID')
DBT_JOBS_ID = Variable.get('DBT_JOBS_ID', deserialize_json=True)

SPARK_SCRIPT_PATHS = Variable.get('SPARK_SCRIPT_PATHS')
SPARK_APP_NAME = Variable.get('SPARK_APP_NAME', deserialize_json=True)
SPARK_CREDENTIAL_PATH = Variable.get('SPARK_CREDENTIAL_PATH')

# 如果沒有使用 secrets backend
# 從 Airflow Variable 中獲取 JSON 字串並解析成 Python 字典
# dbt_jobs_id_str = Variable.get('DBT_JOBS_ID')
# DBT_JOBS_ID = json.loads(dbt_jobs_id_str)

# script_paths = Variable.get('SPARK_SCRIPT_PATHS')
# SPARK_SCRIPT_PATHS = json.loads(script_paths)