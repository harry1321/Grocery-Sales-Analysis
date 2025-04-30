import os
from pathlib import Path
from datetime import datetime, timedelta

from helper.read_load_gcs import GCSBucket, GCBigQuery

def task_date(**kwargs):
    # Take 2021/05/30 as example the format should be date="20210530"
    execute_date = kwargs['logical_date']
    execute_date = execute_date.strftime('%Y%m%d')
    return {'date':"20240416"}

def task_get(ti,dataset_name='andrexibiza/grocery-sales-dataset') -> None:
    '''
    Get data from kaggle API.
    '''

    # Get kaggle crdentials
    import os
    import json
    from kaggle.api.kaggle_api_extended import KaggleApi
    kaggle_config_path = "/opt/airflow/dags/.kaggle/kaggle.json"
    if not os.path.exists(kaggle_config_path):
        raise FileNotFoundError(f"Kaggle config not found at {kaggle_config_path}")
    with open(kaggle_config_path) as f:
        creds = json.load(f)
    os.environ["KAGGLE_USERNAME"] = creds["username"]
    os.environ["KAGGLE_KEY"] = creds["key"]
    folder_path = '/opt/airflow/tmp'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    api = KaggleApi()
    api.authenticate()
    print(f"Downloading data from Kaggle：{dataset_name}...")
    api.dataset_download_files(dataset_name, path=folder_path, unzip=True)
    print("Kaggle dataset download completed！")
    file_names = os.listdir(folder_path)
    file_names = [f for f in file_names if os.path.isfile(os.path.join(folder_path, f))]
    return {'check_list': file_names}

def task_load_gcs(ti) -> None:
    folder_path = '/opt/airflow/tmp'
    gcs = GCSBucket()
    gcs.upload_directory(source_directory=folder_path, prefix=f"raw")
    # Clean up the tmp folder
    import shutil
    shutil.rmtree(folder_path)
    print("Removed all files in tmp.")

def task_check_gcs(ti) -> None:
    '''
    Check target data exsist in GCS or not.
    '''
    temp = ti.xcom_pull(task_ids="get")
    check_list = temp.get("check_list")

    gcs = GCSBucket()
    for item in check_list:
        gcs.check(blob_name=f"raw/{item}")

def task_load_bq(service:str, dataset_name:str, job_config, ti) -> None:
    '''
    Load categories.csv, cusomers.csv, employees.csv & products.csv to GCS for DBT modeling.
    '''
    gbq = GCBigQuery(dataset_name)
    blob_name = f"raw/{service}.csv"
    table_name = service
    gbq.load_from_blob(blob_name, table_name, job_config)

# from airflow.utils.state import State
# from airflow.utils.decorators import apply_defaults
# from airflow.exceptions import AirflowException
# from airflow.sensors.base import BaseSensorOperator
# class LivyBatchSensor(BaseSensorOperator):
#     '''
#     Self-defined sensor that will wait for Livy batch job is completed and then returns success.
#     '''

#     @apply_defaults
#     def __init__(self, livy_endpoint, batch_id, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.livy_endpoint = livy_endpoint
#         self.batch_id = batch_id

#     def poke(self, context):
#         status_url = f"{self.livy_endpoint}/batches/{self.batch_id}/state"
#         headers = {'Content-Type': 'application/json'}
#         response = requests.get(status_url, headers=headers)

#         if response.status_code != 200:
#             raise AirflowException(f"Failed to get Livy batch status: {response.text}")

#         batch_info = response.json()
#         state = batch_info.get('state')

#         if state == 'success':
#             return True
#         else:
#             return False
#         # if state in ('success', 'dead', 'killed', 'error'):
#         #     # extract Spark working Log
#         #     log_response = requests.get(f"{status_url}/log", headers=headers)
#         #     logs = log_response.json().get('log', [])
#         #     logs_combined = "\n".join(logs)
#         #     print(f"=== Livy Logs Start ===\n{logs_combined}\n=== Livy Logs End ===")

#         #     if state == 'success':
#         #         return True
#         #     else:
#         #         raise AirflowException(f"Spark job failed with state: {state}")

#         # return False

# import json
# import requests
# from airflow.models import Variable
# def task_submit_livy_batch(**kwargs):
#     '''
#     Submit a batch Spark job via Livy and push batch id as XCom to Airflow.
#     '''
#     LIVY_ENDPOINT = Variable.get('LIVY_ENDPOINT')
#     SPARK_APP_NAME = Variable.get('SPARK_APP_NAME')
#     SPARK_CREDENTIAL_PATH = Variable.get('CREDENTIAL_PATH')
#     SPARK_SCRIPT_PATH = Variable.get('RAW_TO_SILVER_PY_PATH')
#     GCP_PROJECT_ID = Variable.get('GCP_PROJECT_ID')
#     BUCKET_NAME = Variable.get('BUCKET_NAME')

#     headers = {'Content-Type': 'application/json'}
    
#     data = {
#         "file": SPARK_SCRIPT_PATH,
#         "name": "spark_gen_recommend",
#         "conf": {
#             # 或 yarn，視你的 Spark cluster 架構而定
#             "spark.master": "local[*]",
#             "spark.app.name": f"{SPARK_APP_NAME}",
#             "spark.hadoop.fs.AbstractFileSystem.gs.impl": "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
#             "spark.hadoop.fs.gs.impl": "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem",
#             "spark.hadoop.fs.gs.auth.service.account.json.keyfile": f"{SPARK_CREDENTIAL_PATH}",
#             "spark.hadoop.fs.gs.auth.service.account.enable": "true"
#         },
#         "args": [
#             SPARK_APP_NAME,
#             GCP_PROJECT_ID,
#             BUCKET_NAME
#         ],
#         "executorCores": 2,
#         "executorMemory": "2g",
#         "numExecutors": 2,
#     }

#     response = requests.post(
#         f"{LIVY_ENDPOINT}/batches",
#         data=json.dumps(data),
#         headers=headers
#     )

#     # 201 Created
#     # The request succeeded, and a new resource was created as a result. 
#     # This is typically the response sent after POST requests, or some PUT requests.
#     if response.status_code != 201:
#         raise Exception(f"Livy job submission failed: {response.text}")
    
#     batch_info = response.json()
#     batch_id = batch_info['id']
#     print(f"Batch submitted successfully, batch id: {batch_id}")

#     # 把 batch_id 傳到 XCom
#     kwargs['ti'].xcom_push(key='batch_id', value=batch_id)

"""
def task_branch(upstream_task, success_route, failed_route, **context):
    ti = context['dag_run'].get_task_instance(task_id=f'{upstream_task}')
    if ti.state == State.FAILED:
        return f'{failed_route}'
    else:
        return f'{success_route}'
"""