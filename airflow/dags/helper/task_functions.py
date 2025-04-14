import os
from pathlib import Path
from datetime import datetime, timedelta

from airflow.utils.state import State

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

# def task_branch(success_route, failed_route, ti) -> None:
#     temp = ti.xcom_pull(task_ids="clean")
#     if temp.get("error_ratio") > 1:
#         print(f"Did not pass data quality test with data error ratio {temp.get('error_ratio')}")
#         return f"{failed_route}"
#     else:
#         print(f"Did not pass data quality test with data error ratio {temp.get('error_ratio')}")
#         return f"{success_route}"

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

def task_check_gcs(data_state, ti) -> None:
    '''
    Check target table exsist in GBQ or not.
    '''

def task_dbt_source_freshness(ti) -> None:
    '''
    Check data freshness, if no new data is added then do nothing.
    '''


def task_dbt_seed(ti) -> None:
    '''
    Create table from seeds data.
    '''

def task_dbt_build_all(ti) -> None:
    '''
    Build all models.
    '''
    pass

def task_dbt_build_gold(ti) -> None:
    '''
    Build models that are relative to gold layer tables.
    '''
    pass

"""
def task_branch(upstream_task, success_route, failed_route, **context):
    ti = context['dag_run'].get_task_instance(task_id=f'{upstream_task}')
    if ti.state == State.FAILED:
        return f'{failed_route}'
    else:
        return f'{success_route}'
"""