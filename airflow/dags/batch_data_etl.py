from Github.Retail-Promo-Analysis.airflow.dags.helper.task_functions import task_get
from datetime import datetime,timedelta

from airflow.models import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator
from airflow.utils.task_group import TaskGroup
from airflow.operators.empty import EmptyOperator

from tasks.task_functions import task_date, task_get, task_clean, task_load_gcs, task_branch, task_load_bq
from tasks.variables import GCP_CREDENTIALS_FILE_PATH, GCP_PROJECT_ID, BUCKET_NAME, BUCKET_CLASS, BUCKET_LOCATION

default_args={
    "owner": 'Harry Yang',
    'start_date': datetime(2100, 4, 25),
    #'end_date': datetime(2024, 4, 21),
    'schedule_interval': '0 5 * * *',
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}
default_args={
    "owner": 'Harry Yang',
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
        python_callable=task_get
    )

    # clean = PythonOperator(
    #     task_id="clean",
    #     python_callable=task_clean
    # )
    
    # branch = BranchPythonOperator(
    #     task_id="branch",
    #     python_callable=task_branch,
    #     op_kwargs={"success_route":"load_gcs_processed", "failed_route":"load_gcs_unprocessed"}
    # )

    load_gcs_processed = PythonOperator(
        task_id="load_gcs_processed",
        python_callable=task_load_gcs,
        op_kwargs={"data_state":"processed"}
    )
    
    # load_gcs_unprocessed = PythonOperator(
    #     task_id='load_gcs_unprocessed',
    #     python_callable=task_load_gcs,
    #     op_kwargs={"data_state":"unprocessed"}
    # )

    load_bq = PythonOperator(
        task_id="load_bq",
        python_callable=task_load_bq,
        op_kwargs={"dataset_name":"test", "table_name":"test", "bucket_name":f"{BUCKET_NAME}"}
    )

    check_dbt_con = DbtCloudRunJobOperator(
        task_id='check_dbt_con',
        job_id= dbt_jobs['check_dbt_con'], # 替換為你 dbt cloud 裡的 job id
        account_id= DBT_ACCOUNT_ID, # 70471823453880
        dbt_cloud_conn_id=DBT_CONN_ID, #'dbt_cloud'
        wait_for_termination=True
    )

    create_dbt_seed = DbtCloudRunJobOperator(
        task_id='create_dbt_seed',
        job_id= dbt_jobs['create_dbt_seed'], # 替換為你 dbt cloud 裡的 job id
        account_id= DBT_ACCOUNT_ID, # 70471823453880
        dbt_cloud_conn_id=DBT_CONN_ID, #'dbt_cloud'
        wait_for_termination=True
    )

    create_dbt_seed = DbtCloudRunJobOperator(
        task_id='create_dbt_seed',
        job_id= dbt_jobs['create_dbt_seed'], # 替換為你 dbt cloud 裡的 job id
        account_id= DBT_ACCOUNT_ID, # 70471823453880
        dbt_cloud_conn_id=DBT_CONN_ID, #'dbt_cloud'
        wait_for_termination=True
    )

    """
    end = EmptyOperator(
        task_id='end'
    )

    hold = EmptyOperator(
        task_id='hold'
    )
    """
    with TaskGroup('gold_layer') as modeling_data :
        models = [
            'crm_cust_info',
            'crm_prd_info',
            'crm_salse_details',
            'erp_cust',
            'erp_customer_loc',
            'ERP_PX_CAT'
        ]
        dbt_tasks = []
        for model in models:
            dbt_task = DbtCloudRunJobOperator(
                            task_id=f'{model}',
                            job_id= dbt_jobs[f'{model}'], # 替換為你 dbt cloud 裡的 job id
                            account_id= DBT_ACCOUNT_ID, # 70471823453880
                            dbt_cloud_conn_id=DBT_CONN_ID, #'dbt_cloud'
                            wait_for_termination=True
                        )
#date >> gen >> clean >> branch >> [end, hold]
date >> get >> load_gcs_processed >> load_bq
