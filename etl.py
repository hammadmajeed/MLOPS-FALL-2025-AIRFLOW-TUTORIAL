from airflow import DAG
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from datetime import datetime, timedelta, timezone
from dateutil import parser
import pendulum

LATITUDE = '33.738045'
LONGITUDE = '73.08448'
POSTGRES_CONN_ID = 'postgres_default'
API_CONN_ID = 'open_meteo_api'  # Make sure this connection is set up in Airflow UI

default_args = {
    'owner': 'airflow',
    # Use a fixed, timezone-aware start_date for Airflow scheduling
    'start_date': pendulum.datetime(2025, 11, 10, tz="UTC"),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'weather_etl',
    default_args=default_args,
    description='A simple weather ETL DAG',
    schedule='@daily',
    catchup=False,
    tags=["weather", "ETL"]
) as dag:

    @task
    def extract():
        http = HttpHook(http_conn_id=API_CONN_ID, method='GET')
        endpoint = f'v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true'
        response = http.run(endpoint)
        return response.json()

    @task
    def transform(data):
        current_weather = data['current_weather']
        transformed_data = {
            'latitude': float(LATITUDE),
            'longitude': float(LONGITUDE),
            'temperature': current_weather['temperature'],
            'windspeed': current_weather['windspeed'],
            'weathercode': current_weather['weathercode'],
            # Keep time as ISO string to keep XCom JSON-serializable; parse in load()
            'time': current_weather['time']
        }
        return transformed_data

    @task
    def load(data):
        pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        conn = pg_hook.get_conn()
        try:
            cursor = conn.cursor()
            # Ensure table exists with TIMESTAMPTZ and uniqueness to avoid duplicates
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS weather_data (
                    id SERIAL PRIMARY KEY,
                    latitude FLOAT,
                    longitude FLOAT,
                    temperature FLOAT,
                    windspeed FLOAT,
                    weathercode INT,
                    time TIMESTAMPTZ,
                    UNIQUE (time, latitude, longitude)
                )
                """
            )

            # Parse timestamp (assume UTC if timezone info is missing)
            ts = parser.parse(data['time']) if isinstance(data['time'], str) else data['time']
            if isinstance(ts, datetime) and ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)

            cursor.execute(
                """
                INSERT INTO weather_data (latitude, longitude, temperature, windspeed, weathercode, time)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (time, latitude, longitude) DO NOTHING
                """,
                (
                    data['latitude'],
                    data['longitude'],
                    data['temperature'],
                    data['windspeed'],
                    data['weathercode'],
                    ts,
                ),
            )
            conn.commit()
            cursor.close()
        finally:
            conn.close()

    # Define ETL pipeline
    raw_data = extract()
    cleaned_data = transform(raw_data)
    load(cleaned_data)
