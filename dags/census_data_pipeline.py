from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.utils.log.logging_mixin import LoggingMixin

import pandas as pd
import requests
import sqlite3
import os

# Constants
DATA_URL = "https://raw.githubusercontent.com/practical-bootcamp/week4-assignment1-template/main/city_census.csv"
RAW_CSV_PATH = "/tmp/city_census.csv"
FILTERED_CSV_PATH = "/tmp/filtered_census.csv"
DB_PATH = "/tmp/census_data.db"

logger = LoggingMixin().log

# DAG default arguments
default_args = {
    'owner': 'airflow',
}

# DAG Definition
with DAG(
    dag_id='census_data_pipeline',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval=None,  # Manual trigger
    catchup=False,
    description="A pipeline to extract, transform, and load census data using Airflow",
    tags=["example", "census", "ETL"]
) as dag:

    def download_data(**kwargs):
        """Download CSV data from remote URL."""
        logger.info(f"Downloading data from {DATA_URL}")
        response = requests.get(DATA_URL)
        response.raise_for_status()

        with open(RAW_CSV_PATH, "wb") as f:
            f.write(response.content)

        logger.info(f"Data downloaded successfully to {RAW_CSV_PATH}")

    def transform_data(**kwargs):
        """Clean, filter, and store data."""
        logger.info("Reading raw data...")
        df = pd.read_csv(RAW_CSV_PATH)
        logger.info(f"Original Data Shape: {df.shape}")

        # Drop rows with missing critical fields
        df_clean = df.dropna(subset=["last"])
        logger.info(f"After dropping rows with missing 'last' field: {df_clean.shape}")

        # Filter based on weight condition
        df_filtered = df_clean[df_clean["weight"] > 200]
        logger.info(f"Filtered Data Shape (weight > 200): {df_filtered.shape}")

        # Optional: Save filtered data to CSV for inspection
        df_filtered.to_csv(FILTERED_CSV_PATH, index=False)
        logger.info(f"Filtered data saved to {FILTERED_CSV_PATH}")

        # Store data to SQLite for next task
        with sqlite3.connect(DB_PATH) as conn:
            df_filtered.to_sql('filtered_census', conn, if_exists='replace', index=False)
        logger.info(f"Filtered data stored to SQLite at {DB_PATH}")

    def validate_and_statistics(**kwargs):
        """Basic validation and statistics on the final dataset."""
        logger.info("Loading filtered data from SQLite...")
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql("SELECT * FROM filtered_census", conn)

        if df.empty:
            logger.error("Validation failed: No data available after filtering.")
            raise ValueError("No data to load after filtering. Pipeline halted.")

        logger.info(f"Total Rows Loaded: {len(df)}")

        total_weight = df['weight'].sum()
        logger.info(f"Total Weight Sum: {total_weight}")

    # Task Definitions
    task_download = PythonOperator(
        task_id="download_data",
        python_callable=download_data
    )

    task_transform = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data
    )

    task_validate = PythonOperator(
        task_id="validate_and_statistics",
        python_callable=validate_and_statistics
    )

    # Task Dependencies
    task_download >> task_transform >> task_validate
