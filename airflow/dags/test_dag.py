import os
from datetime import datetime

from airflow import DAG
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator

from helper.read_load_gcs import GCSBucket, GCBigQuery
from helper.variables import GCP_CREDENTIALS_FILE_PATH, GCP_PROJECT_ID, BUCKET_NAME, BUCKET_CLASS, BUCKET_LOCATION

def task_get(ti, dataset_name='andrexibiza/grocery-sales-dataset') -> None:
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


def task_load_gcs(ti) -> None:
    folder_path = '/opt/airflow/tmp'
    gcs = GCSBucket()
    gcs.upload_directory(source_directory=folder_path, prefix=f"raw")
    # 清理下載的資料夾 (可選)
    import shutil
    shutil.rmtree(folder_path)
    print("下載的資料已清理。")

with DAG(dag_id="test",
         start_date=datetime(2023, 1, 1),
         schedule_interval=None,
         catchup=False) as dag:
    get = PythonOperator(
        task_id="get",
        python_callable=task_get
    )
    load_gcs = PythonOperator(
        task_id="load_gcs_processed",
        python_callable=task_load_gcs,
        op_kwargs={"data_state":"processed"}
    )
    # run_dbt_job = DbtCloudRunJobOperator(
    #     task_id='run_dbt_job',
    #     job_id=70471823453361,  # 替換為你 dbt cloud 裡的 job id
    #     account_id=70471823453880,
    #     dbt_cloud_conn_id='dbt_cloud',
    #     wait_for_termination=True
    # )

get >> load_gcs