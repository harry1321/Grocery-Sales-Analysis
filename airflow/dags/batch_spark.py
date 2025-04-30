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

    spark_silver_gold = LivyOperator(
        task_id="spark_silver_gold",
        file=SPARK_SCRIPT_PATHS['gold'],
        name=SPARK_APP_NAME,
        conf={
            "spark.master": "local[*]",
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

date >> spark_raw_silver >> spark_silver_gold
