from datetime import datetime,timedelta

from airflow.models import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator
from airflow.providers.apache.livy.operators.livy import LivyOperator
from airflow.utils.task_group import TaskGroup

from google.cloud import bigquery

from helper.task_functions import task_date, task_get, task_load_gcs, task_check_gcs, task_load_bq
from helper.variables import GCP_CREDENTIALS_FILE_PATH, GCP_PROJECT_ID
from helper.variables import BUCKET_NAME, BUCKET_CLASS, BUCKET_LOCATION, DATASET_NAME
from helper.variables import DBT_ACCOUNT_ID, DBT_CONN_ID, DBT_JOBS_ID
from helper.variables import SPARK_SCRIPT_PATHS, SPARK_APP_NAME, SPARK_CREDENTIAL_PATH

# Import your data schema
from helper.grocery_schema import dataset_schema

default_args={
    "owner": 'Harry Yang',
    # 'start_date': datetime(2100, 4, 25),
    # 'end_date': datetime(2024, 4, 21),
    # 'schedule_interval': '0 5 * * *',
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG(
    dag_id="batch_data_etl",
    default_args=default_args,
    catchup=False
)

with dag:
    date = PythonOperator(
        task_id="date",
        python_callable=task_date
    )

    get = PythonOperator(
        task_id="get",
        python_callable=task_get,
        # Downloading data from kaggle dataset, a dataset name parameter is needed.
        op_kwargs={"dataset_name":'andrexibiza/grocery-sales-dataset'}
    )

    load_gcs = PythonOperator(
        task_id="load_gcs",
        python_callable=task_load_gcs,
    )

    check_gcs = PythonOperator(
        task_id="check_gcs",
        python_callable=task_check_gcs
    )

    with TaskGroup('Load_to_GBQ') as load_gbq:
        services = [
            "sales", 
            "customers", 
            "employees",
            "products"
        ]
        for service in services:
            PythonOperator(
                task_id=f"load_{service}_toGBQ",
                python_callable=task_load_bq,
                op_kwargs={
                    "service":f"{service}", 
                    "dataset_name":f"{DATASET_NAME}", 
                    "job_config":bigquery.LoadJobConfig(
                                source_format=bigquery.SourceFormat.CSV,
                                skip_leading_rows=1,
                                schema=dataset_schema[f"{service}"],
                                create_disposition="CREATE_IF_NEEDED",
                                write_disposition="WRITE_APPEND"
                    )
                }
            )

    check_dbt_con = DbtCloudRunJobOperator(
        task_id='check_dbt_con',
        job_id= DBT_JOBS_ID['check_dbt_con'],
        account_id= DBT_ACCOUNT_ID,
        dbt_cloud_conn_id=DBT_CONN_ID,
        wait_for_termination=True
    )

    create_dbt_seed = DbtCloudRunJobOperator(
        task_id='create_dbt_seed',
        job_id= DBT_JOBS_ID['create_dbt_seed'],
        account_id= DBT_ACCOUNT_ID,
        dbt_cloud_conn_id=DBT_CONN_ID,
        wait_for_termination=True
    )

    with TaskGroup('silver_layer') as build_staing_model:
        models = [
            "build_stg_models",
            "build_dim_models"
        ]
        for model in models:
            DbtCloudRunJobOperator(
                task_id=f'{model}',
                job_id=DBT_JOBS_ID[f'{model}'],
                account_id=DBT_ACCOUNT_ID,
                dbt_cloud_conn_id=DBT_CONN_ID,
                wait_for_termination=True
            )

    with TaskGroup('gold_layer') as build_mart_model:
        models = [
            "build_fct_sales_summary",
            "build_fct_employee_performance",
            "build_fct_customer_behavior"
        ]
        for model in models:
            DbtCloudRunJobOperator(
                task_id=f'{model}',
                job_id=DBT_JOBS_ID[f'{model}'],
                account_id=DBT_ACCOUNT_ID,
                dbt_cloud_conn_id=DBT_CONN_ID,
                wait_for_termination=True
            )

    spark_raw_silver = LivyOperator(
        task_id="spark_raw_silver",
        file=SPARK_SCRIPT_PATHS['silver'],
        name="spark_gen_recommend",
        conf={
            "spark.master": "local[*]",
            "spark.app.name": SPARK_APP_NAME,
            "spark.hadoop.fs.AbstractFileSystem.gs.impl": "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
            "spark.hadoop.fs.gs.impl": "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem",
            "spark.hadoop.fs.gs.auth.service.account.json.keyfile": SPARK_CREDENTIAL_PATH,
            "spark.hadoop.fs.gs.auth.service.account.enable": "true",
        },
        args=[
            SPARK_APP_NAME,
            GCP_PROJECT_ID,
            BUCKET_NAME
        ],
        executor_cores=2,
        executor_memory="2g",
        num_executors=2,
        livy_conn_id="livy",  # 在 Airflow Connections 設定你的 Livy endpoint
        polling_interval=30,
        timeout=1800,
        deferrable=True  # 這裡是重點：啟用 deferrable mode
    )

    build_recommend = DbtCloudRunJobOperator(
        task_id="build_recommend",
        job_id=DBT_JOBS_ID["recommend"],
        account_id=DBT_ACCOUNT_ID,
        dbt_cloud_conn_id=DBT_CONN_ID,
        wait_for_termination=True
    )

date >> get >> load_gcs >> check_gcs >> load_gbq >> check_dbt_con >> create_dbt_seed >> build_staing_model >> [build_mart_model,spark_raw_silver]
spark_raw_silver >> build_recommend
