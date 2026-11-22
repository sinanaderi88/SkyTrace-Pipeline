# Environment & Infrastructure

## Development Environment

SkyTrace is developed and executed in a Linux-based virtual machine running Ubuntu 24.04, hosted on Oracle VirtualBox.

The development environment uses Python 3.12.3 and isolated Python virtual environments to manage project dependencies and avoid conflicts between different data engineering projects.

### Infrastructure

| Component | Configuration |
|---|---|
| Operating System | Ubuntu 24.04 |
| Virtualization | Oracle VirtualBox |
| Python | 3.12.3 |
| Data Processing | Pandas |
| Data Format | Parquet |
| Parquet Engine | PyArrow |
| Compression | Snappy |
| Database | PostgreSQL |
| Database Driver | Psycopg 3 |
| Orchestration | Apache Airflow 3.4.0 |
| Source Control | Git |

### Python Environment Management

The project uses a dedicated Python virtual environment for its ETL components, located in the shared Big Data workspace:

`~/bigdata-lab/.venv`

This environment contains the Python libraries required for data extraction, transformation, and database loading.

Apache Airflow is installed in a separate virtual environment:

`~/bigdata-lab/airflow-venv`

Separating Airflow from the ETL environment helps isolate its dependencies and prevents potential conflicts with the libraries used by the pipeline.

### Project Workspace

The project resides in:

`~/bigdata-lab/opensky-data-pipeline`

The workspace is organized into dedicated directories for source code, raw data, processed data, notebooks, logs, and documentation.

### Infrastructure Design Considerations

- Maintain isolated Python environments for different workloads.
- Keep raw and processed datasets separate.
- Use local infrastructure for development and experimentation.
- Introduce workflow orchestration without disrupting the existing ETL implementation.
- Keep the environment flexible for future scaling and additional aviation data sources.

