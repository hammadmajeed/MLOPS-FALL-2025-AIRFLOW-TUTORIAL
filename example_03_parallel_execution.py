"""
Example 3: Parallel Task Execution
Demonstrates: Parallel tasks, multiple upstream/downstream
"""
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='example_03_parallel_execution',
    default_args=default_args,
    description='Parallel task execution example',
    start_date=datetime(2025, 11, 1),
    schedule_interval='@hourly',
    catchup=False,
    tags=['example', 'parallel'],
) as dag:
    
    # Start task
    start = BashOperator(
        task_id='start',
        bash_command='echo "Starting parallel processing"',
    )
    
    # Three parallel tasks
    task_a = BashOperator(
        task_id='process_region_a',
        bash_command='echo "Processing Region A..." && sleep 2',
    )
    
    task_b = BashOperator(
        task_id='process_region_b',
        bash_command='echo "Processing Region B..." && sleep 2',
    )
    
    task_c = BashOperator(
        task_id='process_region_c',
        bash_command='echo "Processing Region C..." && sleep 2',
    )
    
    # Combine results
    combine = BashOperator(
        task_id='combine_results',
        bash_command='echo "Combining all region results"',
    )
    
    # Final report
    report = BashOperator(
        task_id='generate_report',
        bash_command='echo "Report generated successfully"',
    )
    
    # Task dependencies
    # All three parallel tasks start after 'start'
    start >> [task_a, task_b, task_c]
    
    # 'combine' waits for all three to complete
    [task_a, task_b, task_c] >> combine
    
    # Final report after combine
    combine >> report
