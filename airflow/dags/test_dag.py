from airflow import DAG
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator
from datetime import datetime

with DAG(dag_id="test_dbt_cloud",
         start_date=datetime(2023, 1, 1),
         schedule_interval=None,
         catchup=False) as dag:

    run_dbt_job = DbtCloudRunJobOperator(
        task_id='run_dbt_job',
        job_id=70403104280461,  # 替換為你 dbt cloud 裡的 job id
        account_id=70403103933537,
        dbt_cloud_conn_id='dbt_cloud',
        wait_for_termination=True
    )

run_dbt_job