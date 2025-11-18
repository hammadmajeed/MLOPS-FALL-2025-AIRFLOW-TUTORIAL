"""
Daily Sales ETL Pipeline
Real-world use case: E-commerce daily sales aggregation
"""
"""
Daily Sales ETL Pipeline (TaskFlow API)
Real-world use case: E-commerce daily sales aggregation
"""
from airflow.decorators import dag, task
from airflow.hooks.postgres_hook import PostgresHook
from datetime import datetime, timedelta
import requests
import pandas as pd

@task()
def create_table():
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_sales_summary (
            run_date DATE NOT NULL,
            product_id INT NOT NULL,
            category TEXT NOT NULL,
            quantity INT,
            total_price NUMERIC,
            PRIMARY KEY (run_date, product_id)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@task()
def check_api():
    # Simulate API health check (replace with real endpoint)
    url = "http://localhost:5000/health"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("API health check failed!")

@task()
def extract_sales(run_date):
    # Simulate API call (replace with real endpoint)
    date = run_date.strftime('%Y-%m-%d')
    url = f"http://localhost:5000/sales?date={date}"
    response = requests.get(url)
    response.raise_for_status()
    sales_data = response.json()
    return sales_data

@task()
def transform_sales(sales_data):
    df = pd.DataFrame(sales_data)
    # Aggregate sales by product/category
    summary = df.groupby(['product_id', 'category']).agg({
        'quantity': 'sum',
        'total_price': 'sum'
    }).reset_index()
    summary_dict = summary.to_dict(orient='records')
    return summary_dict

@task()
def load_sales(summary, run_date):
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cur = conn.cursor()
    for row in summary:
        cur.execute("""
            INSERT INTO daily_sales_summary (run_date, product_id, category, quantity, total_price)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (run_date, product_id) DO UPDATE
            SET quantity = EXCLUDED.quantity, total_price = EXCLUDED.total_price;
        """, (
            run_date.strftime('%Y-%m-%d'),
            row['product_id'],
            row['category'],
            row['quantity'],
            row['total_price']
        ))
    conn.commit()
    cur.close()
    conn.close()

@dag(
    dag_id='daily_sales_etl',
    description='Daily ETL for e-commerce sales aggregation (TaskFlow API)',
    start_date=datetime(2025, 11, 1),
    schedule_interval='@daily',
    catchup=False,
    default_args={
        'owner': 'airflow',
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    },
    tags=['realworld', 'etl', 'sales'],
)
def sales_etl_workflow():
    run_date = datetime.now()
    create_table()
    check_api()
    sales_data = extract_sales(run_date)
    summary = transform_sales(sales_data)
    load_sales(summary, run_date)

dag = sales_etl_workflow()

