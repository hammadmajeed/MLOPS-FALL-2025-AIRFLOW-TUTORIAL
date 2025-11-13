# Airflow Quick Start Guide

## Getting Started with the Tutorial

### Prerequisites
- Docker and Docker Compose installed
- Python 3.8+ (for local DAG development)
- Text editor or IDE

### Setup Your Environment

1. **Start Airflow Stack**
```bash
cd /home/hammad/airflow_intro
docker-compose up -d
```

2. **Verify Services are Running**
```bash
docker-compose ps

# Should show:
# - airflow-webserver (healthy)
# - airflow-scheduler (running)
# - postgres (healthy)
```

3. **Access Airflow UI**
- Open browser: http://localhost:8080
- Username: `airflow`
- Password: `airflow`

### Using the Tutorial

#### Step 1: Read the Main Tutorial
Open `AIRFLOW_TUTORIAL.md` and read sections 1-9 to understand core concepts.

#### Step 2: Explore Example DAGs

Copy example DAGs to your `dags/` folder:

```bash
# Example DAGs are in the project root
# Copy them to dags/ folder so Airflow can see them

cp example_*.py dags/
```

Wait 30 seconds for Airflow to discover the new DAGs, then check the UI.

#### Step 3: Run Examples

In the Airflow UI:
1. Find an example DAG (e.g., `example_01_basic_sequential`)
2. Toggle it to "unpause" (switch on left)
3. Click the DAG name to view details
4. Click "Trigger DAG" (play button) to run it
5. Click on task boxes to view logs

#### Step 4: Complete Exercises

Work through exercises 1-8 in `AIRFLOW_TUTORIAL.md`:
- Start with Exercise 1 (easiest)
- Create DAG files in `dags/` folder
- Test each exercise before moving to the next
- Use hints if you get stuck
- Check solutions only after attempting

### Example DAGs Included

| File | Demonstrates | Difficulty |
|------|-------------|-----------|
| `example_01_basic_sequential.py` | Sequential tasks, BashOperator | ⭐ |
| `example_02_taskflow_xcom.py` | TaskFlow API, data passing | ⭐⭐ |
| `example_03_parallel_execution.py` | Parallel tasks | ⭐⭐ |
| `example_04_branching.py` | Conditional logic | ⭐⭐⭐ |
| `example_05_task_groups.py` | Task organization | ⭐⭐⭐ |
| `example_06_error_handling.py` | Retries, callbacks | ⭐⭐⭐⭐ |

### Testing Your DAGs

Before deploying to Airflow:

```bash
# Test DAG syntax
python dags/my_dag.py

# Test specific task (from container)
docker exec airflow_intro_airflow-scheduler_1 \
  airflow tasks test my_dag_id my_task_id 2025-11-11

# List DAGs
docker exec airflow_intro_airflow-scheduler_1 \
  airflow dags list

# Trigger manual run
docker exec airflow_intro_airflow-scheduler_1 \
  airflow dags trigger my_dag_id
```

### Common Commands

```bash
# View scheduler logs
docker-compose logs -f airflow-scheduler

# View webserver logs
docker-compose logs -f airflow-webserver

# Restart services
docker-compose restart airflow-scheduler airflow-webserver

# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v

# Create HTTP connection
docker exec airflow_intro_airflow-scheduler_1 \
  airflow connections add 'my_api' \
    --conn-type 'http' \
    --conn-host 'https://api.example.com'

# List connections
docker exec airflow_intro_airflow-scheduler_1 \
  airflow connections list
```

### Troubleshooting

**DAG not showing in UI:**
```bash
# Check if file has syntax errors
python dags/my_dag.py

# Check scheduler logs
docker-compose logs airflow-scheduler | tail -50

# Force scheduler to reload
docker-compose restart airflow-scheduler
```

**Task failing:**
```bash
# View task logs in UI (click on task box)
# Or check via CLI:
docker exec airflow_intro_airflow-scheduler_1 \
  airflow tasks logs my_dag_id my_task_id 2025-11-11 1
```

**Permission errors:**
```bash
# Fix ownership (if needed)
sudo chown -R $USER:$USER dags/ logs/

# Or re-run init
docker-compose run --rm airflow-init
```

### Exercise Workflow

For each exercise:

1. **Read requirements** carefully
2. **Create DAG file** in `dags/` folder
3. **Test syntax**: `python dags/exercise_N_*.py`
4. **Wait 30 seconds** for Airflow to discover DAG
5. **Unpause in UI**
6. **Trigger manual run**
7. **Check logs** to verify correctness
8. **Compare with solution** (after attempting!)

### Learning Path

**Week 1: Basics**
- Read tutorial sections 1-4
- Complete exercises 1-2
- Explore example DAGs 1-3

**Week 2: Intermediate**
- Read tutorial sections 5-7
- Complete exercises 3-5
- Explore example DAGs 4-5

**Week 3: Advanced**
- Read tutorial sections 8-9
- Complete exercises 6-7
- Review example DAG 6

**Week 4: Capstone**
- Complete exercise 8 (complete ETL)
- Build your own custom pipeline
- Review best practices

### Resources at Your Fingertips

📚 **Main Tutorial**: `AIRFLOW_TUTORIAL.md`
- Comprehensive guide with 8 exercises
- Concepts, examples, and solutions
- Best practices and patterns

🔧 **Example DAGs**: `example_*.py`
- Working code examples
- Copy-paste starting points
- Reference implementations

🗒️ **Quick Reference**: This file
- Setup instructions
- Common commands
- Troubleshooting tips

🌐 **Airflow UI**: http://localhost:8080
- Visual DAG monitoring
- Task logs and execution history
- Connection management

### Next Steps After Tutorial

1. **Customize existing DAG** (`weather_etl` or `operator.py`)
2. **Build your own pipeline** from scratch
3. **Integrate with real data sources** (APIs, databases)
4. **Explore advanced features**:
   - Sensors
   - Custom operators
   - Plugins
   - Dynamic task mapping
5. **Study production patterns**:
   - CI/CD for DAGs
   - Testing strategies
   - Monitoring and alerting
6. **Join the community**:
   - Airflow Slack
   - GitHub discussions
   - Stack Overflow

### Getting Help

- **Tutorial**: Read `AIRFLOW_TUTORIAL.md`
- **Hints**: Each exercise has hints
- **Solutions**: After attempting, check solution outlines
- **Logs**: Always check task logs for error details
- **Documentation**: https://airflow.apache.org/docs/

---

## Quick Reference Card

### File Locations
```
/home/hammad/airflow_intro/
├── dags/              # Put your DAG files here
├── logs/              # Airflow logs
├── plugins/           # Custom plugins (optional)
├── docker-compose.yml # Airflow stack configuration
├── AIRFLOW_TUTORIAL.md   # Main tutorial (⭐ START HERE)
├── QUICKSTART.md      # This file
└── example_*.py       # Example DAGs
```

### Essential Commands
```bash
# Start/Stop
docker-compose up -d              # Start all services
docker-compose down              # Stop all services
docker-compose restart <service> # Restart specific service

# Status
docker-compose ps                # Check service status
docker-compose logs -f <service> # Follow logs

# Airflow CLI
docker exec airflow_intro_airflow-scheduler_1 airflow <command>

# Common Airflow commands:
airflow dags list                # List all DAGs
airflow dags trigger <dag_id>    # Manual trigger
airflow tasks test <dag_id> <task_id> <date>  # Test task
```

### Keyboard Shortcuts (Airflow UI)
- `g + d` : Go to DAGs page
- `g + r` : Go to runs page
- `/` : Search

---

**Happy Learning! 🚀**

Remember: The best way to learn Airflow is by building. Start small, experiment often, and gradually increase complexity.
