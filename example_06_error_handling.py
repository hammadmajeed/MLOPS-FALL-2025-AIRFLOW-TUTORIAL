"""
Example 6: Error Handling and Retries
Demonstrates: Retries, retry_delay, on_failure_callback, error handling
"""
from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
from datetime import datetime, timedelta
import random

def task_failure_alert(context):
    """
    Callback function called when a task fails.
    """
    task_instance = context['task_instance']
    dag_id = context['dag'].dag_id
    task_id = task_instance.task_id
    execution_date = context['execution_date']
    
    print(f"❌ ALERT: Task Failed!")
    print(f"   DAG: {dag_id}")
    print(f"   Task: {task_id}")
    print(f"   Execution Date: {execution_date}")
    print(f"   Try Number: {task_instance.try_number}")

@dag(
    dag_id='example_06_error_handling',
    description='Error handling and retry strategies',
    start_date=datetime(2025, 11, 1),
    schedule_interval=None,
    catchup=False,
    tags=['example', 'error-handling', 'advanced'],
    default_args={
        'retries': 2,
        'retry_delay': timedelta(seconds=10),
        'on_failure_callback': task_failure_alert,
    },
)
def error_handling_example():
    """
    Demonstrates different error handling patterns
    """
    
    @task
    def reliable_task():
        """Task that always succeeds"""
        print("✓ This task always works")
        return "success"
    
    @task(retries=3, retry_delay=timedelta(seconds=5))
    def flaky_task():
        """
        Task that randomly fails to demonstrate retries.
        Has 50% chance of failure.
        """
        # Simulate randomness
        if random.random() < 0.5:
            print("❌ Task failed! Will retry...")
            raise AirflowException("Simulated failure")
        
        print("✓ Task succeeded!")
        return "success"
    
    @task
    def handle_errors_gracefully():
        """
        Task that handles errors internally without failing
        """
        try:
            # Simulate risky operation
            result = risky_operation()
            print(f"✓ Operation succeeded: {result}")
            return result
        except Exception as e:
            # Log error but don't fail the task
            print(f"⚠️  Warning: Operation failed with error: {e}")
            print("   Continuing with fallback value")
            return "fallback_value"
    
    def risky_operation():
        """Simulated operation that might fail"""
        if random.random() < 0.3:
            raise Exception("Random failure")
        return "operation_result"
    
    @task
    def cleanup():
        """
        Cleanup task that always runs (even if upstream fails).
        In real scenario, use trigger_rule='all_done'
        """
        print("🧹 Performing cleanup operations")
        return "cleaned"
    
    # Define task flow
    start = reliable_task()
    result1 = flaky_task()
    result2 = handle_errors_gracefully()
    clean = cleanup()
    
    start >> [result1, result2] >> clean

# Instantiate
dag_instance = error_handling_example()
