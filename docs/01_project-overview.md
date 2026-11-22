# SkyTrace
### Aviation Data Engineering & Flight Data Pipeline

## Project Overview

SkyTrace is an aviation data engineering project focused on collecting, processing, storing, and analyzing aircraft tracking data from the OpenSky Network.

The project captures aircraft state snapshots through the OpenSky REST API and builds a structured data pipeline to transform raw aviation data into a format suitable for historical storage and analytical processing.

It is designed around a modular ETL architecture, separating data extraction, transformation, and loading into independent components. The pipeline stores raw API responses in JSON format, processes them into compressed Parquet datasets, and loads the resulting records into PostgreSQL.

Beyond data ingestion, SkyTrace aims to establish a foundation for historical flight tracking, aircraft movement analysis, and aviation data exploration. Apache Airflow is being introduced to orchestrate, schedule, and monitor pipeline execution, evolving the workflow from manually executed scripts into an automated data engineering pipeline.

## Project Objectives

- Collect aircraft state data from the OpenSky Network API.
- Preserve raw API responses for traceability and potential reprocessing.
- Transform semi-structured JSON data into structured analytical datasets.
- Store processed data in Parquet format using Snappy compression.
- Load data efficiently into PostgreSQL through bulk ingestion.
- Maintain historical aircraft snapshots for temporal analysis.
- Implement data integrity and duplicate-record validation.
- Orchestrate and schedule ETL workflows using Apache Airflow.
- Establish a foundation for future flight movement and trajectory analysis.

## Pipeline Architecture

OpenSky Network API  
→ Extract  
→ Raw JSON Storage  
→ Transform  
→ Processed Parquet (Snappy)  
→ Load  
→ PostgreSQL  
→ Apache Airflow Orchestration

## Future Direction

SkyTrace is intended to evolve beyond periodic aircraft state collection toward a broader aviation data platform, enabling historical movement analysis, flight trajectory reconstruction, and integration of additional flight-related datasets where data availability permits.
