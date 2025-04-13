from pathlib import Path
from datetime import datetime, timedelta

from airflow.utils.state import State

from tasks.read_load_gcs import GCSBucket, GCBigQuery

from kaggle.api.kaggle_api_extended import KaggleApi

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


def task_get(ti,dataset_name) -> None:
    '''
    Get data from kaggle API.
    '''
    api = KaggleApi()
    api.authenticate()
    print(f"正在下載 Kaggle 資料集：{dataset_name}...")
    api.dataset_download_files(dataset_name, path='/opt/airflow/data/', unzip=True)
    print("Kaggle 資料集下載完成！")

def task_load_gcs(data_state,ti) -> None:
    gcs = GCSBucket()
    gcs.upload_directory(source_directory=f"/opt/airflow/data/", prefix=f"raw")
    # 清理下載的資料夾 (可選)
    import shutil
    shutil.rmtree('/opt/airflow/data/')
    print("下載的資料已清理。")

# def task_branch(success_route, failed_route, ti) -> None:
#     temp = ti.xcom_pull(task_ids="clean")
#     if temp.get("error_ratio") > 1:
#         print(f"Did not pass data quality test with data error ratio {temp.get('error_ratio')}")
#         return f"{failed_route}"
#     else:
#         print(f"Did not pass data quality test with data error ratio {temp.get('error_ratio')}")
#         return f"{success_route}"

def task_check_gcs(data_state, ti) -> None:
    '''
    Check target data exsist in GCS or not.
    '''
    temp = ti.xcom_pull(task_ids="date")
    date = temp.get("date")
    check_list = [f"{date}_flow_vd_5min.csv", f"{date}_speed_vd_5min.csv", f"{date}_occ_vd_5min.csv"]
    gcs = GCSBucket()
    for item in check_list:
        gcs.check(blob_name=f"{data_state}/{date}/{item}")

def task_load_bq(dataset_name, table_name, bucket_name, ti) -> None:
    '''

    '''
    temp = ti.xcom_pull(task_ids="date")
    date = temp.get("date")
    gbq = GCBigQuery(dataset_name)
    gbq.load_from_bucket(table_name=table_name, bucket_name=bucket_name, prefix=f"processed/{date}/")

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