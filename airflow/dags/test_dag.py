import os
from datetime import datetime
os.environ['KAGGLE_CONFIG_DIR'] = "/home/airflow/.config/kaggle"

from airflow import DAG
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator

from helper.read_load_gcs import GCSBucket, GCBigQuery
from helper.variables import GCP_CREDENTIALS_FILE_PATH, GCP_PROJECT_ID, BUCKET_NAME, BUCKET_CLASS, BUCKET_LOCATION
from kaggle.api.kaggle_api_extended import KaggleApi

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

with DAG(dag_id="test",
         start_date=datetime(2023, 1, 1),
         schedule_interval=None,
         catchup=False) as dag:
    get = PythonOperator(
        task_id="get",
        python_callable=task_get
    )
    load_gcs_processed = PythonOperator(
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

task_get >> task_load_gcs