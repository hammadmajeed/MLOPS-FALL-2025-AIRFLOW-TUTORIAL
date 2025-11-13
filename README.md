# Complete Apache Airflow Tutorial

## Table of Contents
1. [Introduction to Airflow](#introduction-to-airflow)
2. [Core Concepts](#core-concepts)
3. [DAG Fundamentals](#dag-fundamentals)
4. [Operators Deep Dive](#operators-deep-dive)
5. [TaskFlow API (Modern Approach)](#taskflow-api-modern-approach)
6. [Scheduling and Execution](#scheduling-and-execution)
7. [XCom and Data Passing](#xcom-and-data-passing)
8. [Connections and Hooks](#connections-and-hooks)
9. [Best Practices](#best-practices)
10. [Self-Learning Exercises](#self-learning-exercises)

---

## Introduction to Airflow

**Apache Airflow** is an open-source platform to programmatically author, schedule, and monitor workflows. It allows you to define workflows as Directed Acyclic Graphs (DAGs) using Python code.

### Why Airflow?

- **Dynamic**: Pipelines are defined in Python, allowing for dynamic pipeline generation
- **Extensible**: Easily define your own operators and extend libraries
- **Elegant**: Pipelines are lean and explicit with Jinja templating
- **Scalable**: Modular architecture with message queue for orchestration

### Key Use Cases

- ETL/ELT pipelines
- Data warehousing
- Machine Learning pipelines
- Report generation
- System monitoring and maintenance tasks

---

## Core Concepts

### 1. DAG (Directed Acyclic Graph)

A DAG is a collection of tasks with directional dependencies. It defines:
- What tasks to run
- When to run them
- Dependencies between tasks
- Retry policies

**Key Properties:**
- **Directed**: Tasks flow in one direction
- **Acyclic**: No circular dependencies allowed
- **Graph**: Visual representation of task relationships

### 2. Operator

An operator defines a single task in your workflow. Types include:
- **Action Operators**: Execute something (BashOperator, PythonOperator)
- **Transfer Operators**: Move data between systems
- **Sensors**: Wait for conditions to be met

### 3. Task

A task is an instantiated operator - a specific instance that will be executed.

### 4. Task Instance

A specific run of a task for a particular execution date.

### 5. Execution Date / Data Interval

- **Execution Date**: The logical date/time when a DAG run should start (deprecated term)
- **Data Interval**: The period of data the DAG run should process (start and end)

---

## DAG Fundamentals

### Basic DAG Structure

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 11, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
with DAG(
    dag_id='my_first_dag',
    default_args=default_args,
    description='A simple tutorial DAG',
    schedule_interval='@daily',
    catchup=False,
    tags=['tutorial'],
) as dag:
    
    def my_function():
        print("Hello from Airflow!")
    
    task = PythonOperator(
        task_id='print_hello',
        python_callable=my_function,
    )
```

### DAG Parameters Explained

| Parameter | Description | Example |
|-----------|-------------|---------|
| `dag_id` | Unique identifier for the DAG | `'weather_etl'` |
| `default_args` | Default parameters for all tasks | See above |
| `description` | Human-readable description | `'Processes weather data'` |
| `schedule_interval` | How often to run | `'@daily'`, `'*/5 * * * *'` |
| `start_date` | When scheduling begins | `datetime(2025, 11, 1)` |
| `catchup` | Run missed intervals | `False` |
| `max_active_runs` | Concurrent DAG runs allowed | `1` |
| `tags` | Categorization labels | `['etl', 'production']` |

### Schedule Interval Options

```python
# Cron expressions
schedule_interval='0 0 * * *'     # Daily at midnight
schedule_interval='*/15 * * * *'  # Every 15 minutes
schedule_interval='0 9 * * 1-5'   # Weekdays at 9 AM

# Preset schedules
schedule_interval='@once'         # Run once
schedule_interval='@hourly'       # Every hour
schedule_interval='@daily'        # Daily at midnight
schedule_interval='@weekly'       # Weekly on Sunday
schedule_interval='@monthly'      # First day of month

# Programmatic
from datetime import timedelta
schedule_interval=timedelta(hours=2)  # Every 2 hours

# No schedule (manual trigger only)
schedule_interval=None
```

---

## Operators Deep Dive

### 1. PythonOperator

Executes a Python callable.

```python
from airflow.operators.python import PythonOperator

def process_data(**context):
    """Access execution context"""
    execution_date = context['execution_date']
    print(f"Processing data for {execution_date}")
    return {'status': 'success', 'records': 100}

task = PythonOperator(
    task_id='process',
    python_callable=process_data,
    provide_context=True,  # Pass execution context
)
```

### 2. BashOperator

Executes bash commands.

```python
from airflow.operators.bash import BashOperator

# Simple command
task1 = BashOperator(
    task_id='print_date',
    bash_command='date',
)

# Complex script
task2 = BashOperator(
    task_id='cleanup',
    bash_command='''
        cd /tmp
        rm -f *.tmp
        echo "Cleanup complete"
    ''',
)

# With templating
task3 = BashOperator(
    task_id='process_file',
    bash_command='python process.py --date {{ ds }}',
)
```

### 3. EmailOperator

Sends emails.

```python
from airflow.operators.email import EmailOperator

email_task = EmailOperator(
    task_id='send_report',
    to='team@example.com',
    subject='Daily Report - {{ ds }}',
    html_content='''
        <h3>Daily Report</h3>
        <p>Date: {{ ds }}</p>
        <p>Status: Success</p>
    ''',
)
```

### 4. HttpOperator

Makes HTTP requests.

```python
from airflow.providers.http.operators.http import HttpOperator

api_call = HttpOperator(
    task_id='call_api',
    http_conn_id='my_api',
    endpoint='/data',
    method='GET',
    headers={'Content-Type': 'application/json'},
    response_check=lambda response: response.status_code == 200,
)
```

### 5. BranchPythonOperator

Implements conditional logic.

```python
from airflow.operators.python import BranchPythonOperator

def choose_branch(**context):
    """Decide which path to take"""
    hour = datetime.now().hour
    if hour < 12:
        return 'morning_task'
    else:
        return 'afternoon_task'

branch = BranchPythonOperator(
    task_id='branch',
    python_callable=choose_branch,
)

morning = BashOperator(task_id='morning_task', bash_command='echo "Good morning"')
afternoon = BashOperator(task_id='afternoon_task', bash_command='echo "Good afternoon"')

branch >> [morning, afternoon]
```

---

## TaskFlow API (Modern Approach)

The TaskFlow API (introduced in Airflow 2.0) simplifies DAG authoring using Python decorators.

### Basic TaskFlow Example

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    dag_id='taskflow_example',
    start_date=datetime(2025, 11, 1),
    schedule_interval='@daily',
    catchup=False,
)
def my_etl_pipeline():
    
    @task
    def extract():
        """Extract data from source"""
        data = {'temperature': 25.5, 'humidity': 60}
        return data
    
    @task
    def transform(data: dict):
        """Transform the data"""
        data['temp_fahrenheit'] = data['temperature'] * 9/5 + 32
        return data
    
    @task
    def load(data: dict):
        """Load data to destination"""
        print(f"Loading data: {data}")
    
    # Define task dependencies
    raw_data = extract()
    transformed_data = transform(raw_data)
    load(transformed_data)

# Instantiate the DAG
dag_instance = my_etl_pipeline()
```

### TaskFlow vs Traditional Operators

| Aspect | Traditional | TaskFlow |
|--------|------------|----------|
| Syntax | Verbose, explicit | Concise, Pythonic |
| XCom | Manual push/pull | Automatic |
| Type hints | Optional | Encouraged |
| Data passing | String-based task_ids | Function returns |

### Advanced TaskFlow Features

```python
from airflow.decorators import dag, task
from typing import List, Dict

@dag(
    dag_id='advanced_taskflow',
    start_date=datetime(2025, 11, 1),
    schedule_interval='@daily',
    catchup=False,
)
def advanced_pipeline():
    
    @task(multiple_outputs=True)
    def extract() -> Dict[str, any]:
        """Return multiple values as dict"""
        return {
            'users': [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}],
            'count': 2,
            'timestamp': datetime.now().isoformat()
        }
    
    @task
    def process_users(users: List[Dict]) -> List[str]:
        """Process user data"""
        return [user['name'] for user in users]
    
    @task
    def validate_count(count: int, names: List[str]) -> bool:
        """Validate counts match"""
        return count == len(names)
    
    # Extract returns multiple outputs
    data = extract()
    
    # Access dict values directly
    names = process_users(data['users'])
    is_valid = validate_count(data['count'], names)

dag_instance = advanced_pipeline()
```

---

## Scheduling and Execution

### Understanding Scheduling

```python
from datetime import datetime, timedelta
import pendulum

# Use timezone-aware dates (recommended)
start_date = pendulum.datetime(2025, 11, 1, tz="UTC")

# Schedule intervals
schedule_interval='@daily'        # Runs daily at 00:00 UTC
schedule_interval='0 9 * * 1-5'   # Weekdays at 9 AM
schedule_interval=timedelta(hours=6)  # Every 6 hours
```

### Execution Logic

```
start_date: 2025-11-01 00:00:00
schedule_interval: @daily
catchup: False

Timeline:
- 2025-11-01 00:00 → First run triggered (processes data for 2025-11-01)
- 2025-11-02 00:00 → Second run triggered (processes data for 2025-11-02)
- And so on...
```

### Catchup Behavior

```python
# catchup=False (Recommended for most cases)
# Only runs from now forward, skips historical runs
with DAG(
    dag_id='no_catchup',
    start_date=datetime(2025, 1, 1),  # 10 months ago
    schedule_interval='@daily',
    catchup=False,  # Will NOT run 300+ missed days
):
    pass

# catchup=True
# Runs all missed intervals since start_date
with DAG(
    dag_id='with_catchup',
    start_date=datetime(2025, 1, 1),
    schedule_interval='@daily',
    catchup=True,  # Will run ALL missed days!
):
    pass
```

### Task Dependencies

```python
# Linear dependencies
task1 >> task2 >> task3

# Multiple upstream tasks
task1 >> task3
task2 >> task3

# Multiple downstream tasks
task1 >> [task2, task3, task4]

# Complex dependencies
task1 >> task2
task1 >> task3
[task2, task3] >> task4

# Using set_upstream/set_downstream
task2.set_upstream(task1)
task3.set_downstream(task4)
```

### Task Groups

Organize related tasks visually.

```python
from airflow.utils.task_group import TaskGroup

with DAG('grouped_tasks', start_date=datetime(2025, 11, 1)) as dag:
    
    start = BashOperator(task_id='start', bash_command='echo "Starting"')
    
    with TaskGroup('data_processing') as processing:
        extract = BashOperator(task_id='extract', bash_command='echo "Extract"')
        transform = BashOperator(task_id='transform', bash_command='echo "Transform"')
        load = BashOperator(task_id='load', bash_command='echo "Load"')
        
        extract >> transform >> load
    
    with TaskGroup('quality_checks') as checks:
        check1 = BashOperator(task_id='check1', bash_command='echo "Check 1"')
        check2 = BashOperator(task_id='check2', bash_command='echo "Check 2"')
    
    end = BashOperator(task_id='end', bash_command='echo "Done"')
    
    start >> processing >> checks >> end
```

---

## XCom and Data Passing

XCom (short for "cross-communication") allows tasks to exchange small amounts of data.

### Pushing to XCom (Traditional)

```python
def push_data(**context):
    # Explicit push
    context['ti'].xcom_push(key='my_key', value={'data': 100})
    
    # Implicit push (return value)
    return {'status': 'success'}

push_task = PythonOperator(
    task_id='push',
    python_callable=push_data,
)
```

### Pulling from XCom (Traditional)

```python
def pull_data(**context):
    # Pull by key
    data = context['ti'].xcom_pull(key='my_key', task_ids='push')
    
    # Pull return value
    result = context['ti'].xcom_pull(task_ids='push')
    
    print(f"Received: {data}, {result}")

pull_task = PythonOperator(
    task_id='pull',
    python_callable=pull_data,
)
```

### XCom with TaskFlow (Automatic)

```python
@dag(dag_id='xcom_taskflow', start_date=datetime(2025, 11, 1), schedule_interval=None)
def xcom_pipeline():
    
    @task
    def generate_data() -> dict:
        # Return value automatically pushed to XCom
        return {'records': 500, 'status': 'complete'}
    
    @task
    def process_data(data: dict) -> str:
        # Input parameter automatically pulls from XCom
        print(f"Processing {data['records']} records")
        return f"Processed {data['records']} records"
    
    @task
    def send_notification(message: str):
        print(f"Notification: {message}")
    
    # Data flows automatically
    data = generate_data()
    result = process_data(data)
    send_notification(result)

xcom_pipeline()
```

### XCom Best Practices

✅ **DO:**
- Use for small amounts of metadata (IDs, counts, status)
- Use for configuration and parameters
- Keep payloads under 1 KB when possible

❌ **DON'T:**
- Pass large datasets (use external storage instead)
- Store files or binary data
- Rely on XCom for critical data persistence

---

## Connections and Hooks

Connections store credentials and connection details. Hooks use connections to interact with external systems.

### Creating Connections via CLI

```bash
# HTTP Connection
airflow connections add 'my_api' \
    --conn-type 'http' \
    --conn-host 'https://api.example.com'

# PostgreSQL Connection
airflow connections add 'my_postgres' \
    --conn-type 'postgres' \
    --conn-host 'localhost' \
    --conn-schema 'mydb' \
    --conn-login 'user' \
    --conn-password 'password' \
    --conn-port '5432'

# AWS Connection
airflow connections add 'aws_default' \
    --conn-type 'aws' \
    --conn-extra '{"region_name": "us-east-1"}'
```

### Using Hooks

```python
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.http.hooks.http import HttpHook

@task
def query_database():
    # Initialize hook with connection ID
    pg_hook = PostgresHook(postgres_conn_id='my_postgres')
    
    # Execute query
    records = pg_hook.get_records("SELECT * FROM users LIMIT 10")
    return len(records)

@task
def call_api():
    # Initialize HTTP hook
    http_hook = HttpHook(http_conn_id='my_api', method='GET')
    
    # Make request
    response = http_hook.run('endpoint/data')
    return response.json()
```

### Common Hooks

| Hook | Provider | Use Case |
|------|----------|----------|
| PostgresHook | postgres | PostgreSQL operations |
| MySqlHook | mysql | MySQL operations |
| HttpHook | http | REST API calls |
| S3Hook | amazon | AWS S3 operations |
| BigQueryHook | google | Google BigQuery |
| SlackHook | slack | Slack notifications |

---

## Best Practices

### 1. DAG Design

```python
# ✅ GOOD: Idempotent tasks
@task
def process_data(date: str):
    """
    Process data for specific date.
    Running multiple times produces same result.
    """
    # Delete existing data for this date
    delete_records(date)
    # Insert new data
    insert_records(date)

# ❌ BAD: Non-idempotent
@task
def append_data():
    """Running multiple times creates duplicates"""
    # Always appends without checking
    insert_records()
```

### 2. Error Handling

```python
from airflow.exceptions import AirflowException

@task
def safe_operation():
    try:
        result = risky_operation()
        if not validate(result):
            raise AirflowException("Validation failed")
        return result
    except Exception as e:
        # Log error
        print(f"Error: {e}")
        # Re-raise to mark task as failed
        raise

# Configure retries at DAG level
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
}
```

### 3. Resource Management

```python
@task
def database_operation():
    pg_hook = PostgresHook(postgres_conn_id='my_db')
    conn = pg_hook.get_conn()
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        cursor.close()
    finally:
        # Always close connections
        conn.close()
    
    return len(results)
```

### 4. Configuration Management

```python
from airflow.models import Variable

# Store config in Airflow Variables
@task
def use_config():
    api_key = Variable.get("api_key")
    env = Variable.get("environment", default_var="dev")
    
    config = Variable.get("app_config", deserialize_json=True)
    database_url = config['database']['url']
```

### 5. Documentation

```python
@dag(
    dag_id='well_documented_dag',
    description='Processes daily sales data and generates reports',
    start_date=datetime(2025, 11, 1),
    schedule_interval='@daily',
    catchup=False,
    tags=['sales', 'reporting', 'production'],
    doc_md="""
    # Sales Data Pipeline
    
    ## Purpose
    Processes daily sales transactions and generates management reports.
    
    ## Dependencies
    - Sales database must be accessible
    - S3 bucket for report storage
    
    ## Data Flow
    1. Extract sales from database
    2. Aggregate by region
    3. Generate PDF report
    4. Upload to S3
    5. Send email notification
    
    ## Schedule
    Runs daily at 2 AM UTC
    
    ## Contacts
    - Owner: data-team@example.com
    - On-call: +1-555-0100
    """,
)
def sales_pipeline():
    
    @task(doc_md="Extracts sales records for the previous day")
    def extract_sales() -> List[Dict]:
        """
        Connects to sales database and retrieves records.
        Returns list of sale dictionaries.
        """
        pass
```

### 6. Testing DAGs

```python
# Test DAG can be parsed
def test_dag_loaded():
    from airflow.models import DagBag
    dagbag = DagBag(dag_folder='dags/', include_examples=False)
    assert 'my_dag_id' in dagbag.dags
    assert len(dagbag.import_errors) == 0

# Test task count
def test_task_count():
    from airflow.models import DagBag
    dagbag = DagBag()
    dag = dagbag.get_dag('my_dag_id')
    assert len(dag.tasks) == 5

# Test dependencies
def test_dependencies():
    from airflow.models import DagBag
    dagbag = DagBag()
    dag = dagbag.get_dag('my_dag_id')
    
    extract_task = dag.get_task('extract')
    transform_task = dag.get_task('transform')
    
    assert transform_task in extract_task.downstream_list
```

---

## Self-Learning Exercises

### Exercise 1: Basic DAG Creation
**Difficulty:** ⭐ Beginner

**Task:** Create a DAG that runs every 5 minutes and performs these tasks:
1. Print "Starting pipeline"
2. Sleep for 2 seconds
3. Print "Pipeline complete"

**Requirements:**
- Use appropriate operators
- Set proper dependencies
- Name the DAG `exercise_1_basic_pipeline`


---

### Exercise 2: Python Functions and Data Passing
**Difficulty:** ⭐⭐ Intermediate

**Task:** Create a DAG using the TaskFlow API that:
1. Generates a list of 5 random numbers (1-100)
2. Calculates the sum of those numbers
3. Calculates the average
4. Prints both sum and average

**Requirements:**
- Use `@task` decorator
- Pass data between tasks using return values
- Run manually (no schedule)


---

### Exercise 3: Conditional Branching
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced

**Task:** Create a DAG that checks the current hour and:
- If hour < 12: Run "morning_report" task
- If hour >= 12 and < 18: Run "afternoon_report" task  
- If hour >= 18: Run "evening_report" task
- Always run "send_summary" task at the end

**Requirements:**
- Use `BranchPythonOperator`
- Use dummy operators or bash operators for report tasks
- Ensure summary always runs regardless of branch


---

### Exercise 4: Database Integration
**Difficulty:** ⭐⭐⭐ Advanced

**Task:** Create an ETL pipeline that:
1. Creates a table `weather_stats` if it doesn't exist
2. Inserts sample weather data (3 records)
3. Queries the average temperature
4. Prints the result

**Requirements:**
- Use PostgresHook
- Use the existing `postgres_default` connection
- Handle the database connection properly (close it)

**Table Schema:**
```sql
CREATE TABLE IF NOT EXISTS weather_stats (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100),
    temperature FLOAT,
    recorded_at TIMESTAMP
)
```


---

### Exercise 5: API Integration
**Difficulty:** ⭐⭐⭐ Advanced

**Task:** Create a DAG that:
1. Fetches data from a public API (JSONPlaceholder: `https://jsonplaceholder.typicode.com/users`)
2. Parses the JSON response
3. Counts how many users have `.com` email addresses
4. Stores the count in XCom

**Requirements:**
- Use HttpHook with a connection
- Handle the response properly
- Extract and count emails


---

### Exercise 6: Dynamic Task Generation
**Difficulty:** ⭐⭐⭐⭐ Advanced

**Task:** Create a DAG that dynamically generates tasks based on a list of cities:
- Cities: `['New York', 'London', 'Tokyo', 'Paris', 'Mumbai']`
- For each city, create a task that prints "Processing {city}"
- All city tasks should run in parallel
- Add a final task that runs after all city tasks complete

**Requirements:**
- Use a loop to generate tasks dynamically
- Set proper dependencies
- Use TaskFlow API


---

### Exercise 7: Error Handling and Retries
**Difficulty:** ⭐⭐⭐⭐ Advanced

**Task:** Create a DAG that simulates a flaky API call:
1. Create a task that fails 50% of the time randomly
2. Configure it to retry 3 times with 30-second delays
3. On success, log "Success after retries"
4. Add a callback function that runs on failure

**Requirements:**
- Use random number generation to simulate failures
- Configure retry behavior
- Implement `on_failure_callback`


---

### Exercise 8: Complete ETL Pipeline (Capstone)
**Difficulty:** ⭐⭐⭐⭐⭐ Expert

**Task:** Build a complete production-ready ETL pipeline that:

1. **Extract:** Fetches current weather data from Open-Meteo API for 3 cities
2. **Transform:** 
   - Convert temperature from Celsius to Fahrenheit
   - Add timestamp
   - Calculate daily statistics
3. **Load:** Insert into PostgreSQL with proper error handling
4. **Notify:** Send completion status (simulate with print)

**Additional Requirements:**
- Use TaskFlow API
- Implement proper error handling
- Use task groups for organization
- Add data quality checks
- Configure retries appropriately
- Document the DAG with docstrings

---

## Additional Resources

### Official Documentation
- [Apache Airflow Docs](https://airflow.apache.org/docs/)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [TaskFlow API Tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html)

### Community Resources
- [Astronomer Guides](https://docs.astronomer.io/)
- [Awesome Apache Airflow](https://github.com/jghoman/awesome-apache-airflow)
- [Airflow Summit Recordings](https://airflowsummit.org/)

### Books
- *Data Pipelines with Apache Airflow* by Bas P. Harenslak
- *Apache Airflow Cookbook* by Viraj Parekh

---

## Quick Command Reference

```bash
# DAG Management
airflow dags list                          # List all DAGs
airflow dags list-runs -d <dag_id>        # List runs for a DAG
airflow dags trigger <dag_id>             # Trigger manual run
airflow dags pause <dag_id>               # Pause DAG
airflow dags unpause <dag_id>             # Unpause DAG
airflow dags delete <dag_id>              # Delete DAG

# Task Management
airflow tasks list <dag_id>               # List tasks in DAG
airflow tasks test <dag_id> <task_id> <date>  # Test task
airflow tasks states-for-dag-run <dag_id> <execution_date>  # Task states

# Connection Management
airflow connections list                   # List connections
airflow connections add <conn_id> ...     # Add connection
airflow connections delete <conn_id>      # Delete connection

# Variable Management
airflow variables list                     # List variables
airflow variables set <key> <value>       # Set variable
airflow variables get <key>               # Get variable

# Database
airflow db init                           # Initialize database
airflow db upgrade                        # Upgrade database
airflow db reset                          # Reset database (⚠️ destructive)

# User Management
airflow users create -u admin -p admin -f Admin -l User -r Admin -e admin@example.com
airflow users list

# Scheduler/Webserver
airflow scheduler                         # Start scheduler
airflow webserver                         # Start webserver (port 8080)
```

---

## Troubleshooting Common Issues

### Issue: DAG not appearing in UI
**Solutions:**
1. Check file syntax: `python dags/my_dag.py`
2. Check scheduler logs: `docker logs <scheduler_container>`
3. Verify DAG is not paused
4. Check file is in correct `dags/` folder

### Issue: Tasks stuck in "running" state
**Solutions:**
1. Check if scheduler is running
2. Check executor has capacity
3. Review task logs
4. Restart scheduler if needed

### Issue: XCom size limit exceeded
**Solutions:**
1. Reduce data size being passed
2. Use external storage (S3, database) and pass references
3. Increase XCom backend limits (not recommended)

### Issue: Import errors
**Solutions:**
1. Install required provider packages
2. Check Python path
3. Verify dependencies in requirements.txt
4. Restart services after package installation
