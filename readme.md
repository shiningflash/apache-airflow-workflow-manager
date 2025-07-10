# Apache Airflow Workflow Manager

Simple Apache Airflow setup with both standalone and Docker-Compose workflows for quick orchestration experiments.

---

## Getting Started with Standalone Setup

### Create Virtual Environment and Install Airflow

```bash
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
````

### Run Airflow Standalone

```bash
$ airflow standalone
```

Access the Airflow UI at: [http://localhost:8080](http://localhost:8080)

Generated password is stored here:

```bash
$ cat /Users/<username>/airflow/simple_auth_manager_passwords.json.generated
```

---

## Install Apache Airflow using Docker-Compose

### Download Docker-Compose Setup

```bash
$ curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.0/docker-compose.yaml'
```

### Review and Modify `docker-compose.yaml` (Optional)

```bash
$ less docker-compose.yaml
$ vim docker-compose.yaml
```

### Initialize Airflow

```bash
$ docker compose up airflow-init
```

### Start Airflow Services

```bash
$ docker compose up
```

Access the Airflow UI at: [http://localhost:8080](http://localhost:8080)

**Default Credentials:**

* Username: `airflow`
* Password: `airflow`

---

## Available DAGs and Their Workflow

| DAG Name               | Description                                   | File                                      | Flow Summary                                      |
|------------------------|-----------------------------------------------|-------------------------------------------|---------------------------------------------------|
| `wine_dataset_producer` | Downloads raw wine dataset from GitHub        | `wine_dataset_producer.py`                | `download → save → trigger Dataset`              |
| `wine_dataset_consumer` | Cleans and persists wine data on trigger      | `wine_dataset_consumer.py`                | `clean → save cleaned → persist to SQLite`       |
| `census_data_pipeline`  | ETL pipeline using PythonOperators            | `census_data_pipeline.py`                 | `download → transform → validate`                |

### 1. `wine_dataset_producer`

**File:** [`wine_dataset_producer.py`](./dags/wine_dataset_producer.py)
**Purpose:**
Fetches the raw wine ratings dataset from a GitHub URL and saves it to a local file as a [Dataset](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/datasets.html).

**Tasks:**
* Download CSV from GitHub
* Save to: `~/airflow/datasets/raw_wine_dataset.csv`
* Publish `Dataset` trigger for downstream DAGs

---

### 2. `wine_dataset_consumer`

**File:** [`wine_dataset_consumer.py`](./dags/wine_dataset_consumer.py)
**Triggered by:** `wine_dataset_producer` via `Dataset`
**Purpose:**
Reads, cleans, and persists the wine dataset using virtualenv tasks and SQLite.

**Tasks:**
* Clean dataset (drop `grape`, normalize line breaks)
* Save cleaned CSV to: `~/airflow/datasets/cleaned_wine_dataset.csv`
* Store full dataset and `notes` column into SQLite at: `~/airflow/databases/wine_dataset.db`

---

### 3. `census_data_pipeline`

**File:** [`census_data_pipeline.py`](./dags/census_data_pipeline.py)  
**Purpose:**  
Demonstrates a basic ETL pipeline using Airflow's `PythonOperator`. It fetches census data from a public URL, filters the data, stores it in SQLite, and performs basic validation and statistics.

**Tasks:**
- **`download_data`**: Downloads raw census data from GitHub and stores it at `/tmp/city_census.csv`
- **`transform_data`**: Cleans missing values, filters rows where `weight > 200`, and saves output to both CSV and a SQLite table (`/tmp/census_data.db`)
- **`validate_and_statistics`**: Loads the data from SQLite and runs basic validation and summary stats (e.g., row count and total weight)
- **Flow:** `download\_data → transform\_data → validate\_and\_statistics`
- **Tags:** `example`, `ETL`

---

## License

MIT License
