# ETL Pipeline Architecture

SkyTrace implements a modular ETL pipeline using Python, with each stage developed as an independent script. This separation allows individual components to be tested, maintained, and executed independently before being integrated into a workflow orchestration system.

The pipeline consists of three stages: Extract, Transform, and Load.

## 1. Extract

The extraction component retrieves aircraft state data from the OpenSky REST API.

**Implementation:** `src/extract.py`

### Process

- Sends an HTTP GET request to the OpenSky API.
- Validates the HTTP response using `raise_for_status()`.
- Verifies that the response contains the `states` field.
- Preserves the complete API response in JSON format.
- Saves each snapshot as a separate file in the raw data directory.
- Records the number of aircraft state records extracted.

### Raw Data Storage

Raw snapshots are stored in:

`data/raw/`

Files follow the naming convention:

`opensky_YYYYMMDD_HHMMSS.json`

The filename is based on the UTC extraction time, providing a unique identifier for each extraction.

The original JSON response is retained to support traceability, reprocessing, and comparison between snapshots.

---

## 2. Transform

The transformation component converts the raw JSON response into a structured tabular dataset.

**Implementation:** `src/transform.py`

### Process

- Reads the raw JSON snapshot.
- Converts the aircraft state vectors into a Pandas DataFrame using the predefined 17-column schema.
- Removes leading and trailing whitespace from callsigns.
- Converts Unix timestamps into UTC datetime values.
- Adds `snapshot_time` based on the API response timestamp.
- Adds `source_file` to identify the original raw file.
- Serializes the `sensors` field into JSON strings when present.
- Preserves missing values instead of discarding records.
- Writes the transformed dataset to Parquet format.

### Processed Data Storage

Processed datasets are stored in:

`data/processed/`

Files follow the naming convention:

`opensky_YYYYMMDD_HHMMSS_processed.parquet`

### Storage Format

Parquet is used as a columnar storage format, making the processed data suitable for efficient analytical workloads.

Snappy compression is applied to reduce storage footprint while maintaining efficient read and write performance.

**Technology Stack:**

- Pandas — data manipulation and transformation.
- PyArrow — Parquet engine.
- Snappy — compression.

---

## 3. Load

The loading component transfers the processed Parquet dataset into PostgreSQL.

**Implementation:** `src/load.py`

### Process

- Reads the processed Parquet file into a Pandas DataFrame.
- Selects the expected columns and preserves their order.
- Converts Pandas missing values, including `NaN` and `NaT`, into Python `None` values to ensure compatibility with PostgreSQL NULL handling.
- Creates a temporary staging table for the incoming dataset.
- Uses PostgreSQL `COPY` through Psycopg to perform bulk data ingestion.
- Inserts records from the staging table into the target table.
- Uses `ON CONFLICT DO NOTHING` to prevent inserting records with duplicate primary keys.

### Bulk Loading Strategy

Instead of inserting records individually, the pipeline uses PostgreSQL's `COPY` mechanism through Psycopg.

The data is first loaded into a temporary staging table and then transferred to the final target table.

This approach separates ingestion from final table insertion and provides an efficient mechanism for loading larger datasets.

### Target Table

`opensky.aircraft_states`

The target table stores aircraft state records along with snapshot metadata required for historical tracking.

The composite primary key is:

`(icao24, snapshot_time)`

This allows the same aircraft to be stored across multiple snapshots while preventing duplicate records for the same aircraft within the same snapshot.

---

## 4. Pipeline Execution

During the development phase, Extract, Transform, and Load are executed independently through Python scripts.

The workflow is currently executed manually. Apache Airflow is being introduced to automate task execution, establish dependencies, schedule recurring snapshots, and monitor pipeline runs.

## ETL Workflow

OpenSky API  
↓  
Extract — `extract.py`  
↓  
Raw JSON  
↓  
Transform — `transform.py`  
↓  
Processed Parquet (Snappy)  
↓  
Load — `load.py`  
↓  
PostgreSQL — `opensky.aircraft_states`
