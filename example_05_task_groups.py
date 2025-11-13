"""
Example 5: Task Groups for Organization
Demonstrates: TaskGroup, nested tasks, visual organization
"""
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='example_05_task_groups',
    default_args=default_args,
    description='Task groups for better organization',
    start_date=datetime(2025, 11, 1),
    schedule_interval='@daily',
    catchup=False,
    tags=['example', 'task-groups'],
) as dag:
    
    start = BashOperator(
        task_id='start',
        bash_command='echo "Starting ETL pipeline"',
    )
    
    # Group 1: Data Ingestion
    with TaskGroup('data_ingestion', tooltip="Ingest data from multiple sources") as ingestion:
        ingest_api = BashOperator(
            task_id='ingest_from_api',
            bash_command='echo "Ingesting from API"',
        )
        
        ingest_db = BashOperator(
            task_id='ingest_from_database',
            bash_command='echo "Ingesting from database"',
        )
        
        ingest_file = BashOperator(
            task_id='ingest_from_files',
            bash_command='echo "Ingesting from files"',
        )
        
        # Parallel ingestion
        [ingest_api, ingest_db, ingest_file]
    
    # Group 2: Data Processing
    with TaskGroup('data_processing', tooltip="Process and transform data") as processing:
        clean = BashOperator(
            task_id='clean_data',
            bash_command='echo "Cleaning data"',
        )
        
        transform = BashOperator(
            task_id='transform_data',
            bash_command='echo "Transforming data"',
        )
        
        validate = BashOperator(
            task_id='validate_data',
            bash_command='echo "Validating data"',
        )
        
        # Sequential processing
        clean >> transform >> validate
    
    # Group 3: Data Output
    with TaskGroup('data_output', tooltip="Export data to destinations") as output:
        export_warehouse = BashOperator(
            task_id='export_to_warehouse',
            bash_command='echo "Exporting to warehouse"',
        )
        
        export_lake = BashOperator(
            task_id='export_to_lake',
            bash_command='echo "Exporting to data lake"',
        )
        
        export_api = BashOperator(
            task_id='export_to_api',
            bash_command='echo "Exporting to API"',
        )
        
        # Parallel export
        [export_warehouse, export_lake, export_api]
    
    end = BashOperator(
        task_id='end',
        bash_command='echo "Pipeline completed successfully"',
    )
    
    # Define flow between groups
    start >> ingestion >> processing >> output >> end
