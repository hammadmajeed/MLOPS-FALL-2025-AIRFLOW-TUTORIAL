"""
Example 4: Conditional Branching
Demonstrates: BranchPythonOperator, conditional logic, trigger rules
"""
from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

def decide_branch(**context):
    """
    Decide which branch to execute based on current hour.
    Returns the task_id to execute.
    """
    hour = datetime.now().hour
    
    print(f"Current hour: {hour}")
    
    if hour < 12:
        print("Executing morning branch")
        return 'morning_process'
    elif hour < 18:
        print("Executing afternoon branch")
        return 'afternoon_process'
    else:
        print("Executing evening branch")
        return 'evening_process'

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='example_04_branching',
    default_args=default_args,
    description='Conditional branching example',
    start_date=datetime(2025, 11, 1),
    schedule_interval='@hourly',
    catchup=False,
    tags=['example', 'branching', 'intermediate'],
) as dag:
    
    # Start task
    start = BashOperator(
        task_id='start',
        bash_command='echo "Checking time of day..."',
    )
    
    # Branch decision
    branch_task = BranchPythonOperator(
        task_id='check_time_of_day',
        python_callable=decide_branch,
    )
    
    # Morning branch
    morning = BashOperator(
        task_id='morning_process',
        bash_command='echo "Good morning! Running morning tasks..."',
    )
    
    # Afternoon branch
    afternoon = BashOperator(
        task_id='afternoon_process',
        bash_command='echo "Good afternoon! Running afternoon tasks..."',
    )
    
    # Evening branch
    evening = BashOperator(
        task_id='evening_process',
        bash_command='echo "Good evening! Running evening tasks..."',
    )
    
    # Join task - runs regardless of which branch executed
    join = BashOperator(
        task_id='send_notification',
        bash_command='echo "Sending completion notification"',
        trigger_rule='none_failed_min_one_success',  # Runs if at least one upstream succeeded
    )
    
    # Task dependencies
    start >> branch_task
    branch_task >> [morning, afternoon, evening]
    [morning, afternoon, evening] >> join
