# dags/stock_market_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.dates import days_ago

import sys
sys.path.insert(0, '/opt/airflow/scripts')

from fetch_and_store import run_stock_pipeline

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'email_on_failure': True,
    'email_on_retry': False,
    'email': ['your_receiving_email@example.com'], # Replace with your email
}
# Define the DAG
with DAG(
    dag_id='stock_market_data_pipeline',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval='@daily',
    catchup=False,
    tags=['stock-market', 'data-pipeline'],
    doc_md="""
    Stock Market Data Pipeline
    This DAG fetches daily stock market data, stores it in PostgreSQL,
    and sends an email alert if any task fails.
    """
) as dag:
# Create the stock_data table if it does not exist
    create_stock_table = PostgresOperator(
        task_id='create_stock_table_if_not_exists',
        postgres_conn_id='stock_db',
        sql="""
            CREATE TABLE IF NOT EXISTS stock_data (
                symbol VARCHAR(10) NOT NULL,
                trade_date DATE NOT NULL,
                open_price NUMERIC,
                high_price NUMERIC,
                low_price NUMERIC,
                close_price NUMERIC,
                volume BIGINT,
                PRIMARY KEY (symbol, trade_date)
            );
        """
    )

    fetch_and_store_data = PythonOperator(
        task_id='fetch_and_store_stock_data',
        python_callable=run_stock_pipeline,
        op_kwargs={'symbol': 'AAPL'} 
    )

    create_stock_table >> fetch_and_store_data
