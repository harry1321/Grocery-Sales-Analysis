import os
from datetime import datetime

from airflow import DAG
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from google.cloud import bigquery
from helper.read_load_gcs import GCSBucket, GCBigQuery
from helper.variables import GCP_CREDENTIALS_FILE_PATH, GCP_PROJECT_ID, BUCKET_NAME, BUCKET_CLASS, BUCKET_LOCATION
from helper.grocery_schema import dataset_schema

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
    file_names = os.listdir(folder_path)
    for f in file_names:
        print(file_names)
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
        python_callable=task_load_gcs
    )
    check_gcs = PythonOperator(
        task_id="check_gcs",
        python_callable=task_check_gcs
    )
    load_bq = PythonOperator(
        task_id="load_bq",
        python_callable=task_load_bq,
        op_kwargs={
            "service":"sales", 
            "dataset_name":"test", 
            "job_config":bigquery.LoadJobConfig(
                        source_format=bigquery.SourceFormat.CSV,
                        skip_leading_rows=1,
                        schema=dataset_schema["sales"],
                        create_disposition="CREATE_IF_NEEDED",
                        write_disposition="WRITE_APPEND"
            )
        }
    )
    # run_dbt_job = DbtCloudRunJobOperator(
    #     task_id='run_dbt_job',
    #     job_id=70471823453361,  # 替換為你 dbt cloud 裡的 job id
    #     account_id=70471823453880,
    #     dbt_cloud_conn_id='dbt_cloud',
    #     wait_for_termination=True
    # )

get >> load_gcs >> check_gcs >> load_bq