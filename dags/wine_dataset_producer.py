from datetime import datetime
from pathlib import Path
import pandas as pd

from airflow import DAG, Dataset
from airflow.decorators import task

# Dataset path (dynamic)
raw_dataset_path = Path.home() / "airflow" / "datasets" / "raw_wine_dataset.csv"
RAW_WINE_DATASET = Dataset(f"file://{raw_dataset_path}")

with DAG(
    dag_id="wine_dataset_producer",
    schedule="@daily",  # or None for manual triggering
    start_date=datetime(2025, 7, 10),
    catchup=False,
    tags=["example"],
) as dag:

    @task(outlets=[RAW_WINE_DATASET])
    def download_dataset():
        url = "https://raw.githubusercontent.com/paiml/wine-ratings/refs/heads/main/wine-ratings.csv"
        df = pd.read_csv(url)
        raw_dataset_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(raw_dataset_path, index=False)

    download_dataset()
