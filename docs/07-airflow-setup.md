# 07 — Apache Airflow Orchestration

## Overview

Apache Airflow was added to orchestrate the OpenSky ETL pipeline and automate the execution of its Extract, Transform, and Load stages.

The existing Python scripts were integrated into an Airflow DAG, with task dependencies defined explicitly. File paths are passed between tasks using XCom, while PostgreSQL ingestion is handled through an Airflow-specific loader.

## Environment

| Component | Version |
|---|---|
| Ubuntu | 24.04 |
| Python | 3.12.3 |
| Apache Airflow | 3.4.0 |
| PostgreSQL Provider | 7.1.2 |
| Standard Provider | 1.21.0 |
| Psycopg | 3.3.9 |

Airflow is installed in a dedicated virtual environment to keep its dependencies isolated from the main ETL environment.

- **Virtual environment:** `~/bigdata-lab/airflow-venv`
- **Airflow Home:** `~/bigdata-lab/airflow`
- **DAG directory:** `~/bigdata-lab/airflow/dags`

Airflow was installed using the official version-specific constraints for Python 3.12.

## DAG Architecture

The pipeline is implemented as `skytrace_pipeline`, with three sequential tasks:

| Task | Description | Script |
|---|---|---|
| Extract | Retrieves aircraft state data from OpenSky and saves raw JSON | `src/extract.py` |
| Transform | Cleans and structures the raw data, then generates a Parquet file | `src/transform.py` |
| Load | Loads processed data into PostgreSQL | `load_airflow.py` |

```text
Extract → Transform → Load
```

The DAG uses `PythonOperator` and explicit task dependencies to ensure each stage runs only after its upstream task succeeds.

## Scheduling

The DAG is configured to run automatically every 30 minutes.

| Setting | Value |
|---|---|
| Schedule | `*/30 * * * *` |
| Execution interval | 30 minutes |
| Catchup | `False` |
| Start date | 2026-11-21 |

The schedule is defined in the DAG code. Automatic execution depends on the Airflow Scheduler being active.

## Data Transfer Between Tasks

XCom is used to pass file paths between tasks rather than transferring the datasets themselves.

- Extract returns the path to the generated raw JSON file.
- Transform receives the raw file path and returns the processed Parquet file path.
- Load receives the Parquet file path and reads the file for database ingestion.

The Extract and Transform wrapper functions convert `Path` objects to strings to make their return values suitable for XCom.

## PostgreSQL Integration

Airflow connects to PostgreSQL using `PostgresHook` and the configured connection ID:

`skytrace_postgres`

The target table is:

`opensky.aircraft_states`

The original standalone loader (`src/load.py`) remains separate from the Airflow loader.

### Loading Strategy

The Airflow loader uses a staging-based approach:

1. Read the processed Parquet file using Pandas.
2. Check the required columns and their presence.
3. Create a temporary staging table based on the target table structure.
4. Convert the DataFrame into an in-memory CSV buffer.
5. Transfer the records into staging using PostgreSQL `COPY FROM STDIN`.
6. Insert staged records into the target table.
7. Ignore duplicate records based on `(icao24, snapshot_time)`.

The final insert uses:

```sql
ON CONFLICT (icao24, snapshot_time)
DO NOTHING
```

The operation is managed within a database transaction. Successful execution is committed; exceptions trigger rollback, and the connection is closed afterward.

## Execution and Validation

The DAG was tested through the Airflow UI and executed successfully from Extract through Load.

All three tasks completed successfully, and the resulting records were verified in PostgreSQL.

During initial testing, the Load task failed because `copy_expert()` was not available on the Psycopg 3 cursor. The COPY implementation was changed to use Psycopg 3's `cursor.copy()` interface. The failed task was cleared and rerun successfully, followed by a successful end-to-end DAG execution.

## Current Status

- Airflow environment installed and configured.
- PostgreSQL connection established through Airflow.
- Extract, Transform, and Load integrated into a single DAG.
- End-to-end execution verified.
- Automatic scheduling configured for every 30 minutes.
- Successful data ingestion verified in PostgreSQL.

Automatic scheduling has been configured; its recurring execution is being monitored.

## Future Improvements

- Add a dedicated data validation task.
- Configure retry policies and failure notifications.
- Improve monitoring and logging.
- Extend the pipeline with additional data sources and enrichment steps.
