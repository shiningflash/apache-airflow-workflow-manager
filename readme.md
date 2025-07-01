
# Apache Airflow Workflow Manager

Simple Apache Airflow setup with both standalone and Docker-Compose workflows for quick orchestration experiments.

---

## Getting Started with Standalone Setup

### Create Virtual Environment and Install Airflow

```bash
$ python -m venv venv
$ source venv/bin/activate
$ pip install apache-airflow
````

### Run Airflow Standalone

```bash
$ airflow standalone
```

Access the Airflow UI at: [http://localhost:8080](http://localhost:8080)

Generated password is stored here:

```bash
$ cat /Users/amirul/airflow/simple_auth_manager_passwords.json.generated
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

## License

MIT License
