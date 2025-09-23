from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path



from src.extract_xweather import fetch_xweather_storms  
from src.cleaning import transform  
from src.load import save_to_postgres_dag  


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def extract_task(limit: int = 50, **context):
    
    output_path = fetch_xweather_storms(limit=limit)
    if not output_path:
        raise RuntimeError("Extract returned no file path")
    return output_path


def transform_task(json_path: str, **context):
   
    storm_csv, track_csv = transform(json_path)

    processed_dir = Path(__file__).resolve().parent / "src" / "data" / "processed"
    return {
        "storm_csv": str((processed_dir / "storm.csv").as_posix()),
        "track_csv": str((processed_dir / "track.csv").as_posix()),
        "forecast_csv": str((processed_dir / "forecast.csv").as_posix()),
    }


def load_task(ti, **context):
    x = ti.xcom_pull(task_ids="transform")
    storm_csv = x.get("storm_csv") if isinstance(x, dict) else None
    track_csv = x.get("track_csv") if isinstance(x, dict) else None
    forecast_csv = x.get("forecast_csv") if isinstance(x, dict) else None
    ok = save_to_postgres_dag(storm_csv, track_csv, forecast_csv)
    if not ok:
        raise RuntimeError("Load to Postgres failed")


with DAG(
    dag_id="xweather_etl",
    default_args=default_args,
    description="Extract Xweather storms, transform to CSV, and load to Postgres",
    schedule="0 7 * * *",  # daily at 07:00 UTC
    start_date=datetime(2025, 9, 1),
    catchup=False,
    max_active_runs=1,
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_task,
        op_kwargs={"limit": int(os.environ.get("XWEATHER_LIMIT", 50))},
    )

    transform_op = PythonOperator(
        task_id="transform",
        python_callable=transform_task,
        op_kwargs={
            "json_path": "{{ ti.xcom_pull(task_ids='extract') }}",
        },
    )

    load = PythonOperator(
        task_id="load",
        python_callable=load_task,
    )

    extract >> transform_op >> load
