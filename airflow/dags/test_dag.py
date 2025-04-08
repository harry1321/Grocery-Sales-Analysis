from helper.test import *

from airflow.models import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator

default_args={
    "owner": 'Harry Yang',
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}
with DAG(
    dag_id="test_dag",
    default_args=default_args
) as dag:
    date = PythonOperator(
        task_id="date",
        python_callable=task_date
    )

    test = PythonOperator(
        task_id="test",
        python_callable=testf
    )


date >> test 