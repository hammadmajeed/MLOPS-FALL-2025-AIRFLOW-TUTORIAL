"""
Example 2: TaskFlow API with Data Passing
Demonstrates: @task decorator, automatic XCom, type hints
"""
from airflow.decorators import dag, task
from datetime import datetime
from typing import Dict, List

@dag(
    dag_id='example_02_taskflow_xcom',
    description='TaskFlow API with automatic data passing',
    start_date=datetime(2025, 11, 1),
    schedule_interval=None,
    catchup=False,
    tags=['example', 'taskflow', 'intermediate'],
)
def taskflow_example():
    """
    Example showing how TaskFlow API automatically handles XCom
    """
    
    @task
    def extract() -> Dict[str, any]:
        """
        Extract data from source.
        Return value is automatically pushed to XCom.
        """
        data = {
            'users': ['Alice', 'Bob', 'Charlie'],
            'count': 3,
            'timestamp': str(datetime.now())
        }
        print(f"Extracted {data['count']} users")
        return data
    
    @task
    def transform(data: Dict) -> List[str]:
        """
        Transform data.
        Input parameter automatically pulls from XCom.
        """
        # Convert names to uppercase
        transformed = [name.upper() for name in data['users']]
        print(f"Transformed: {transformed}")
        return transformed
    
    @task
    def load(names: List[str]) -> int:
        """
        Load data to destination.
        Returns count of loaded items.
        """
        print(f"Loading {len(names)} names to database")
        for name in names:
            print(f"  - {name}")
        return len(names)
    
    @task
    def report(count: int):
        """
        Generate final report.
        """
        print(f"✓ Pipeline complete: {count} records processed")
    
    # Define data flow - values pass automatically
    raw_data = extract()
    transformed_data = transform(raw_data)
    load_count = load(transformed_data)
    report(load_count)

# Instantiate the DAG
dag_instance = taskflow_example()
