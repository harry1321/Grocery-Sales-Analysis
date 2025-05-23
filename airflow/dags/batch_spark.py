from datetime import datetime,timedelta

from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.livy.operators.livy import LivyOperator


from helper.task_functions import task_date
from helper.variables import GCP_CREDENTIALS_FILE_PATH, GCP_PROJECT_ID
from helper.variables import BUCKET_NAME
from helper.variables import SPARK_SCRIPT_PATHS, SPARK_APP_NAME, SPARK_CREDENTIAL_PATH

default_args={
    "owner": 'Harry Yang',
    # 'start_date': datetime(2100, 4, 25),
    # 'end_date': datetime(2024, 4, 21),
    # 'schedule_interval': '0 5 * * *',
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG(
    dag_id="batch_spark",
    default_args=default_args,
    catchup=False
)

with dag:
    date = PythonOperator(
        task_id="date",
        python_callable=task_date
    )

    spark_rfm_model = LivyOperator(
        task_id="spark_rfm_model",
        file=SPARK_SCRIPT_PATHS['rfm'],
        conf={
            "spark.master": "local[*]",
            "spark.app.name": "spark_rfm_model",
            "spark.hadoop.fs.AbstractFileSystem.gs.impl": "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
            "spark.hadoop.fs.gs.impl": "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem",
            "spark.hadoop.fs.gs.auth.service.account.json.keyfile": SPARK_CREDENTIAL_PATH,
            "spark.hadoop.fs.gs.auth.service.account.enable": "true",
        },
        args=[
            "spark_rfm_model",
            GCP_PROJECT_ID,
            BUCKET_NAME
        ],
        executor_cores=2,
        executor_memory="4g",
        num_executors=2,
        livy_conn_id="livy",  # 在 Airflow Connections 設定你的 Livy endpoint
        polling_interval=60,
        deferrable=True
    )

    spark_raw_silver = LivyOperator(
        task_id="spark_raw_silver",
        file=SPARK_SCRIPT_PATHS['silver'],
        conf={
            "spark.master": "local[*]",
            "spark.app.name": "spark_raw_silver",
            "spark.hadoop.fs.AbstractFileSystem.gs.impl": "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
            "spark.hadoop.fs.gs.impl": "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem",
            "spark.hadoop.fs.gs.auth.service.account.json.keyfile": SPARK_CREDENTIAL_PATH,
            "spark.hadoop.fs.gs.auth.service.account.enable": "true",
        },
        args=[
            "spark_raw_silver",
            GCP_PROJECT_ID,
            BUCKET_NAME
        ],
        executor_cores=2,
        executor_memory="4g",
        num_executors=2,
        livy_conn_id="livy",  # 在 Airflow Connections 設定你的 Livy endpoint
        polling_interval=60,
        deferrable=True
    )

    spark_silver_gold = LivyOperator(
        task_id="spark_silver_gold",
        file=SPARK_SCRIPT_PATHS['gold'],
        conf={
            "spark.master": "local[*]",
            "spark.app.name": "spark_silver_gold",
            "spark.hadoop.fs.AbstractFileSystem.gs.impl": "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
            "spark.hadoop.fs.gs.impl": "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem",
            "spark.hadoop.fs.gs.auth.service.account.json.keyfile": SPARK_CREDENTIAL_PATH,
            "spark.hadoop.fs.gs.auth.service.account.enable": "true",
        },
        args=[
            "spark_silver_gold",
            GCP_PROJECT_ID,
            BUCKET_NAME
        ],
        executor_cores=2,
        executor_memory="4g",
        num_executors=2,
        livy_conn_id="livy",  # 在 Airflow Connections 設定你的 Livy endpoint
        polling_interval=60,
        deferrable=True
    )

date >> spark_rfm_model >> spark_raw_silver >> spark_silver_gold
