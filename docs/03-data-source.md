# Data Source & API

## Data Source

SkyTrace uses the **OpenSky Network** as its primary data source. OpenSky provides aircraft surveillance data collected from a network of sensors, including ADS-B, Mode S, and other surveillance technologies.

The project retrieves aircraft state data through the OpenSky REST API and captures periodic snapshots of aircraft currently visible to the network.

## API Endpoint

The data is collected from the following endpoint:

`GET https://opensky-network.org/api/states/all`

This endpoint returns the current state vectors of aircraft, along with a timestamp representing the time of the snapshot.

## Data Collection Method

The pipeline retrieves the API response as JSON and stores the original response in the raw data layer before processing.

Each API response represents a snapshot of aircraft states at a particular point in time. Repeated collection allows the project to build a historical dataset of aircraft observations.

The extraction process preserves the original API response, including nullable fields, for traceability and potential reprocessing.

## State Vector Structure

Each aircraft state vector contains 17 fields:

| Index | Field | Description |
|---:|---|---|
| 0 | `icao24` | Unique aircraft transponder identifier |
| 1 | `callsign` | Aircraft callsign, when available |
| 2 | `origin_country` | Country of registration |
| 3 | `time_position` | Unix timestamp of the last position update |
| 4 | `last_contact` | Unix timestamp of the last received contact |
| 5 | `longitude` | Longitude in decimal degrees |
| 6 | `latitude` | Latitude in decimal degrees |
| 7 | `baro_altitude` | Barometric altitude in meters |
| 8 | `on_ground` | Indicates whether the aircraft is on the ground |
| 9 | `velocity` | Ground speed in meters per second |
| 10 | `true_track` | Direction of movement in degrees |
| 11 | `vertical_rate` | Vertical speed in meters per second |
| 12 | `sensors` | Sensor identifiers, when available |
| 13 | `geo_altitude` | Geometric altitude in meters |
| 14 | `squawk` | Transponder squawk code |
| 15 | `spi` | Special Position Identification indicator |
| 16 | `position_source` | Source type of position information |

## Snapshot Metadata

In addition to the aircraft state vectors, the API response contains a top-level timestamp:

- `time` — Unix timestamp representing the snapshot time returned by the API.

SkyTrace converts this timestamp to UTC and stores it as `snapshot_time` during transformation. This field is used to distinguish aircraft observations across different snapshots.

## Data Limitations

- Aircraft visibility depends on the OpenSky sensor network coverage.
- Not all state vector fields are populated for every aircraft.
- Callsigns may be missing or contain incomplete information.
- Position and altitude information may be null.
- State vectors do not inherently provide flight origin and destination airports.
- A callsign alone cannot reliably determine a flight's destination.

SkyTrace retains records with missing attributes rather than discarding them solely because some fields are null.

## API Access

The pipeline currently uses direct HTTP requests through Python's `requests` library.

The extraction script validates the HTTP response and the presence of the `states` field before storing the response.

Anonymous API access is used during the current development stage, subject to OpenSky access restrictions and rate limits.
