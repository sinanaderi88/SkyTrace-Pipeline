# Database Design

## Database Overview

SkyTrace uses PostgreSQL as its primary relational database for storing structured aircraft state observations.

The database is designed to support historical data collection, querying, data validation, and analytical workloads. Each record represents an aircraft observation within a specific API snapshot.
## Database Setup & Initialization

The PostgreSQL database environment was configured using the following steps.

### 1. Create the Database User

Connect to PostgreSQL using an administrative account:

```bash
sudo -u postgres psql
```

Create the dedicated database user:

```sql
CREATE USER opensky_user WITH LOGIN;
```

Set the user password interactively:

```sql
\password opensky_user
```

### 2. Create the Database

Create the project database and assign ownership to the dedicated user:

```sql
CREATE DATABASE opensky_db OWNER opensky_user;
```

### 3. Connect to the Project Database

Exit the PostgreSQL administrative session:

```sql
\q
```

Connect to the newly created database:

```bash
psql -h localhost -U opensky_user -d opensky_db
```

### 4. Create the Schema

Create a dedicated schema for the project:

```sql
CREATE SCHEMA opensky;
```

### 5. Create the Target Table

The following SQL statement creates the main table used to store aircraft state observations:

```sql
CREATE TABLE opensky.aircraft_states (
    icao24          VARCHAR(6) NOT NULL,
    callsign        VARCHAR(20),
    origin_country  VARCHAR(100),
    time_position   TIMESTAMPTZ,
    last_contact    TIMESTAMPTZ,
    longitude       DOUBLE PRECISION,
    latitude        DOUBLE PRECISION,
    baro_altitude   DOUBLE PRECISION,
    on_ground       BOOLEAN,
    velocity        DOUBLE PRECISION,
    true_track       DOUBLE PRECISION,
    vertical_rate   DOUBLE PRECISION,
    sensors         JSONB,
    geo_altitude    DOUBLE PRECISION,
    squawk          VARCHAR(10),
    spi             BOOLEAN,
    position_source  SMALLINT,
    snapshot_time   TIMESTAMPTZ NOT NULL,
    source_file     TEXT NOT NULL,
    PRIMARY KEY (icao24, snapshot_time)
);
```

The table is created inside the `opensky` schema and uses a composite primary key to uniquely identify each aircraft observation within a snapshot.

### Database Configuration

| Component | Value |
|---|---|
| Database | `opensky_db` |
| Schema | `opensky` |
| Target Table | `aircraft_states` |
| Database Engine | PostgreSQL |
| Database User | `opensky_user` |

The project uses a dedicated database and schema to keep aviation data isolated from other databases and workloads running in the development environment.

---

## Schema Structure

The target table is:

`opensky.aircraft_states`

The table stores the 17 aircraft state vector attributes provided by the OpenSky API, along with two additional pipeline metadata columns:

- `snapshot_time` — identifies the API snapshot associated with the observation.
- `source_file` — records the raw JSON filename from which the record was processed.

### Table Columns

| Column | PostgreSQL Data Type | Description |
|---|---|---|
| `icao24` | VARCHAR(6) | Aircraft ICAO 24-bit address |
| `callsign` | VARCHAR(20) | Aircraft callsign |
| `origin_country` | VARCHAR(100) | Country of aircraft registration |
| `time_position` | TIMESTAMPTZ | Timestamp of the last position update |
| `last_contact` | TIMESTAMPTZ | Timestamp of the last received contact |
| `longitude` | DOUBLE PRECISION | Longitude in decimal degrees |
| `latitude` | DOUBLE PRECISION | Latitude in decimal degrees |
| `baro_altitude` | DOUBLE PRECISION | Barometric altitude in meters |
| `on_ground` | BOOLEAN | Indicates whether the aircraft is on the ground |
| `velocity` | DOUBLE PRECISION | Ground speed in meters per second |
| `true_track` | DOUBLE PRECISION | Direction of movement in degrees |
| `vertical_rate` | DOUBLE PRECISION | Vertical speed in meters per second |
| `sensors` | JSONB | Sensor information, when available |
| `geo_altitude` | DOUBLE PRECISION | Geometric altitude in meters |
| `squawk` | VARCHAR(10) | Transponder squawk code |
| `spi` | BOOLEAN | Special Position Identification indicator |
| `position_source` | SMALLINT | Position data source type |
| `snapshot_time` | TIMESTAMPTZ | Timestamp identifying the API snapshot |
| `source_file` | TEXT | Name of the original raw JSON file |

---

## Primary Key Design

The table uses a composite primary key:

`(icao24, snapshot_time)`

### Rationale

Aircraft are observed repeatedly across different API snapshots. Using `icao24` alone as the primary key would prevent storing historical observations of the same aircraft.

The composite key allows:

- The same aircraft to be recorded across multiple snapshots.
- Historical aircraft observations to be retained.
- Duplicate records for the same aircraft within the same snapshot to be prevented.

This design supports time-based analysis while maintaining record-level uniqueness.

---

## Data Type Selection

PostgreSQL data types were selected according to the characteristics of the source data:

- **TIMESTAMPTZ** — used for timestamps to maintain timezone-aware temporal data, with observations normalized to UTC.
- **DOUBLE PRECISION** — used for geographic coordinates, altitude, velocity, and movement-related numeric values.
- **BOOLEAN** — used for binary state indicators such as `on_ground` and `spi`.
- **JSONB** — used for the `sensors` field to support structured data storage.
- **SMALLINT** — used for the numeric `position_source` classification.
- **VARCHAR / TEXT** — used for aircraft identifiers, callsigns, country names, and source filenames.

Nullable fields are retained to accommodate incomplete observations returned by the API.

---

## Historical Data Strategy

SkyTrace follows a snapshot-based storage approach rather than maintaining only the latest aircraft state.

Each collection cycle creates a new observation period identified by `snapshot_time`. Consequently, the same aircraft can have multiple records in the table, each associated with a different snapshot.

This approach establishes the foundation for:

- Historical aircraft observation analysis.
- Temporal comparisons between snapshots.
- Aircraft movement analysis.
- Position and altitude changes over time.
- Future trajectory analysis.

The current schema is designed for historical snapshot storage. State-change detection and trajectory reconstruction are future analytical capabilities rather than implemented database features.

---

## Data Lineage

The `source_file` column provides record-level traceability to the original raw JSON file.

This enables records stored in PostgreSQL to be associated with their source extraction files, supporting data auditing, troubleshooting, and potential reprocessing.

---

## Database Design Summary

The PostgreSQL data model provides a structured foundation for SkyTrace by combining aircraft state attributes, snapshot metadata, historical record retention, and a composite primary key.

The design prioritizes data integrity, traceability, and historical storage while remaining suitable for future analytical development.
