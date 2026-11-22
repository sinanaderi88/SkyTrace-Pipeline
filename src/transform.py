import json
import pandas as pd
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"


COLUMNS = [
    "icao24",
    "callsign",
    "origin_country",
    "time_position",
    "last_contact",
    "longitude",
    "latitude",
    "baro_altitude",
    "on_ground",
    "velocity",
    "true_track",
    "vertical_rate",
    "sensors",
    "geo_altitude",
    "squawk",
    "spi",
    "position_source"
]


def transform_data(raw_file):

    raw_file = Path(raw_file)

    # Read raw JSON
    with open(raw_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert raw states to DataFrame
    df = pd.DataFrame(data["states"], columns=COLUMNS)

    # Clean callsign
    df["callsign"] = df["callsign"].str.strip()

    # Convert Unix timestamps to UTC datetime
    df["time_position"] = pd.to_datetime(
        df["time_position"],
        unit="s",
        utc=True
    )

    df["last_contact"] = pd.to_datetime(
        df["last_contact"],
        unit="s",
        utc=True
    )

    # Add snapshot timestamp
    df["snapshot_time"] = pd.to_datetime(
        data["time"],
        unit="s",
        utc=True
    )

    # Add source file information
    df["source_file"] = raw_file.name

    # Convert sensors to JSON string if populated
    df["sensors"] = df["sensors"].apply(
        lambda value: json.dumps(value) if value is not None else None
    )

    # Create processed directory
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Output Parquet file
    output_file = PROCESSED_DIR / f"{raw_file.stem}_processed.parquet"

    # Save transformed data
    df.to_parquet(
        output_file,
        index=False,
        engine="pyarrow",
        compression="snappy"
    )

    print("Transformation successful")
    print(f"Records: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Output format: Parquet")
    print(f"Saved to: {output_file}")

    return output_file


if __name__ == "__main__":

    latest_raw_file = max(
        RAW_DIR.glob("opensky_*.json"),
        key=lambda f: f.stat().st_mtime
    )

    transform_data(latest_raw_file)
