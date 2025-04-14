import os
from pathlib import Path
from datetime import datetime, timedelta

from airflow.utils.state import State

from helper.read_load_gcs import GCSBucket, GCBigQuery

'''
# XCom pull file namein gcs, push file name in gcs and date
task_check_gcs = GCSObjectExistenceSensor(
    bucket=BUCKET_NAME,
    object=PATH_TO_UPLOAD_FILE,
    mode='poke',
    soft_fail=True,
    task_id="task_check_gcs"
)
'''

def task_date(**kwargs):
    # 以2021/05/30為例 格式為 date="20210530"
    execute_date = kwargs['logical_date']
    execute_date = execute_date.strftime('%Y%m%d')
    return {'date':"20240416"}


def task_get(ti,dataset_name='andrexibiza/grocery-sales-dataset') -> None:
    '''
    Get data from kaggle API.
    '''
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
    print(f"正在下載 Kaggle 資料集：{dataset_name}...")
    api.dataset_download_files(dataset_name, path=folder_path, unzip=True)
    print("Kaggle 資料集下載完成！")
    file_names = os.listdir(folder_path)
    file_names = [f for f in file_names if os.path.isfile(os.path.join(folder_path, f))]
    return {'check_list': file_names}

def task_load_gcs(ti) -> None:
    folder_path = '/opt/airflow/tmp'
    gcs = GCSBucket()
    gcs.upload_directory(source_directory=folder_path, prefix=f"raw")
    # 清理下載的資料夾 (可選)
    import shutil
    shutil.rmtree(folder_path)
    print("下載的資料已清理。")

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
    check_list = temp.get("file_names")

    gcs = GCSBucket()
    for item in check_list:
        gcs.check(blob_name=f"raw/{item}")

def task_load_bq(service:str, dataset_name:str, job_config, ti) -> None:
    '''

    '''
    temp = ti.xcom_pull(task_ids="get")
    check_list = temp.get("file_names")
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