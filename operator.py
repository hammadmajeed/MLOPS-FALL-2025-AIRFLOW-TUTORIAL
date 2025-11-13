from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator

def extract():
    print("Extracting")

def transform():
    print("Transform")

def load():
    print("Loading")


with DAG(dag_id="mlops_worklfow_practice") as dag:
    task_1 = PythonOperator(
        task_id='Extraction',
        python_callable=extract

    )

    task_2 = BashOperator(
        task_id='Sleep',
        bash_command='sleep 5'
    )

    task_3 = PythonOperator(
        task_id="Transformation",
        python_callable=transform
    )

    task_4 = PythonOperator(
        task_id="Loading",
        python_callable=load
    )

    task_5 = BashOperator(
        task_id="Success",
        bash_command='echo "Workflow Succeeded"'
    )

    task_1 >> task_2 >> task_3 >> task_4 >> task_5