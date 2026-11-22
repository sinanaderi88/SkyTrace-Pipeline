# Data Validation & Quality Checks

## Overview

Data quality validation is implemented across different stages of the SkyTrace pipeline to verify data integrity, identify incomplete observations, and ensure reliable data ingestion into PostgreSQL.

The validation process focuses on source response integrity, record consistency, null-value analysis, ingestion verification, and duplicate detection.

## 1. API Response Validation

During extraction, the pipeline performs basic validation before storing the API response.

The following checks are implemented:

- HTTP response status validation using `raise_for_status()`.
- Verification that the API response contains the expected `states` field.
- Handling of empty or null state collections.

These checks prevent invalid or unsuccessful API responses from being silently processed as valid datasets.

## 2. Data Completeness

Aircraft state records may contain missing attributes because data availability depends on the aircraft, its transmission status, and sensor coverage.

SkyTrace preserves records containing null values rather than discarding entire observations because of incomplete attributes.

During initial validation, missing values were examined in important position-related fields, including:

- `latitude`
- `longitude`
- `time_position`

This helps distinguish incomplete source observations from pipeline processing failures.

## 3. Record Count Validation

Record counts are checked across the extraction, transformation, and loading stages.

The validation process compares:

- Records retrieved from the API.
- Records written to the processed Parquet dataset.
- Records inserted into PostgreSQL.

This comparison helps identify unexpected record loss or inconsistencies during processing and ingestion.

## 4. Database Validation

After loading the processed dataset into PostgreSQL, SQL queries are used to validate the resulting records.

The checks include:

- Total number of stored records.
- Number of distinct aircraft identifiers (`icao24`).
- Number of distinct snapshots.
- Missing latitude values.
- Missing longitude values.
- Missing position timestamps.

These checks provide an overview of the loaded dataset and its completeness.

## 5. Duplicate Detection

SkyTrace identifies duplicate aircraft observations using the combination of:

`icao24` + `snapshot_time`

This composite key represents the uniqueness of an aircraft observation within a snapshot.

Duplicate insertion is also prevented at the database level through the composite primary key and the `ON CONFLICT DO NOTHING` loading strategy.

The duplicate-checking script is used to audit the stored data for duplicate keys.

The current implementation focuses on exact duplicate observations within the same snapshot. Repeated observations of the same aircraft across different snapshots are retained as historical records.

Aircraft state-change detection is not part of the current duplicate-validation logic.

## 6. Initial Validation Results

The first successful ingestion was validated in PostgreSQL.

| Metric | Result |
|---|---:|
| Total Records | 11,810 |
| Unique Aircraft | 11,810 |
| Snapshots | 1 |
| Missing Latitude | 63 |
| Missing Longitude | 63 |
| Missing Position Timestamp | 63 |

The validation confirmed that all 11,810 records from the processed dataset were successfully loaded into PostgreSQL.

The 63 records with missing position-related fields were retained. These missing values originated from incomplete API observations and were not treated as ingestion failures.

## 7. Data Quality Approach

SkyTrace currently follows these data quality principles:

- Validate API responses before processing.
- Preserve original source data.
- Retain incomplete records for further analysis.
- Validate record counts after ingestion.
- Maintain record uniqueness through database constraints.
- Separate source-data limitations from ETL errors.
- Preserve historical snapshots rather than overwriting previous observations.

## Summary

The initial validation confirms that the extraction, transformation, and loading process operates successfully for the first snapshot.

The validation framework provides a foundation for future enhancements, including automated quality checks, threshold-based monitoring, schema validation, anomaly detection, and pipeline-level alerting.
