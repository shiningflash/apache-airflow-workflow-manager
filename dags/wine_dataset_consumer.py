import logging
from datetime import datetime
from pathlib import Path

from airflow import DAG, Dataset
from airflow.decorators import task

logger = logging.getLogger(__name__)

# Dynamic paths
base_path = Path.home() / "airflow" / "datasets"
raw_path = base_path / "raw_wine_dataset.csv"
clean_path = base_path / "cleaned_wine_dataset.csv"
db_path = Path.home() / "airflow" / "databases" / "wine_dataset.db"

# Dataset reference
RAW_WINE_DATASET = Dataset(f"file://{raw_path}")

with DAG(
    dag_id="wine_dataset_consumer",
    schedule=[RAW_WINE_DATASET],
    start_date=datetime(2025, 7, 10),
    tags=["example"],
    catchup=False,
) as dag:

    @task.virtualenv(
        task_id="clean_dataset",
        requirements=["pandas==2.1.4"],
        system_site_packages=False,
    )
    def clean_dataset():
        import pandas as pd
        from pathlib import Path

        base_path = Path.home() / "airflow" / "datasets"
        raw_path = base_path / "raw_wine_dataset.csv"
        clean_path = base_path / "cleaned_wine_dataset.csv"

        df = pd.read_csv(raw_path, index_col=0)
        df.replace({"\r": ""}, regex=True, inplace=True)
        df.replace({"\n": " "}, regex=True, inplace=True)
        if "grape" in df.columns:
            df.drop(["grape"], axis=1, inplace=True)
        df.to_csv(clean_path)

    @task.virtualenv(
        task_id="persist_dataset",
        requirements=["pandas==2.1.4", "sqlalchemy==1.4.54"],
        system_site_packages=False,
    )
    def persist_dataset():
        import pandas as pd
        from sqlalchemy import create_engine
        from pathlib import Path

        dataset_path = Path.home() / "airflow" / "datasets" / "cleaned_wine_dataset.csv"
        db_path = Path.home() / "airflow" / "databases" / "wine_dataset.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        engine = create_engine(f"sqlite:///{db_path}", echo=False)

        df = pd.read_csv(dataset_path, index_col=0)
        df.to_sql("wine_dataset", con=engine, index=False, if_exists="replace")
        df[["notes"]].to_sql("wine_notes", con=engine, index=False, if_exists="replace")

    clean_dataset() >> persist_dataset()
