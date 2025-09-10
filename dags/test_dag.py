from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'hieu',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

def extract_data():
    print("📡 Extracting data... done")
    return "storm_data.json"

def save_local(ti, **kwargs):
    filename = ti.xcom_pull(task_ids='extract_task')
    print(f"💾 Saving {filename} to local folder")

def notify():
    print("✅ Pipeline finished!")

with DAG(
    dag_id='mini_test_dag',
    default_args=default_args,
    description='Mini DAG for testing Airflow setup',
    start_date=datetime(2025, 9, 1),
    schedule='@daily',   # Airflow 2.7+
    catchup=False,
    tags=['test'],
) as dag:

    t1 = PythonOperator(
        task_id='extract_task',
        python_callable=extract_data,
        do_xcom_push=True,  
    )

    t2 = PythonOperator(
        task_id='save_task',
        python_callable=save_local,
    )

    t3 = PythonOperator(
        task_id='notify_task',
        python_callable=notify,
    )

    t1 >> t2 >> t3