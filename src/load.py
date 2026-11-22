
import getpass
from pathlib import Path

import pandas as pd
import psycopg
from psycopg import sql


PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

DB_CONFIG = {
    "host": "localhost",
    "dbname": "opensky_db",
    "user": "opensky_user",
}

TABLE_SCHEMA = "opensky"
TABLE_NAME = "aircraft_states"

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
    "position_source",
    "snapshot_time",
    "source_file",
]


def load_data(parquet_file):
    parquet_file = Path(parquet_file)

    df = pd.read_parquet(parquet_file)

    df = df[COLUMNS]

    df = df.astype(object).where(pd.notna(df), None)

    password = getpass.getpass("PostgreSQL password: ")

    with psycopg.connect(**DB_CONFIG, password=password) as conn:
        with conn.cursor() as cur:

            staging_table = "aircraft_states_staging"

            cur.execute(
                sql.SQL("""
                    CREATE TEMP TABLE {} 
                    (LIKE {}.{} INCLUDING DEFAULTS)
                    ON COMMIT DROP
                """).format(
                    sql.Identifier(staging_table),
                    sql.Identifier(TABLE_SCHEMA),
                    sql.Identifier(TABLE_NAME),
                )
            )

            copy_query = sql.SQL("""
                COPY {} ({}) FROM STDIN
            """).format(
                sql.Identifier(staging_table),
                sql.SQL(", ").join(
                    sql.Identifier(column) for column in COLUMNS
                ),
            )

            with cur.copy(copy_query) as copy:
                for row in df.itertuples(index=False, name=None):
                    copy.write_row(row)

            insert_query = sql.SQL("""
                INSERT INTO {}.{} ({})
                SELECT {} FROM {}
                ON CONFLICT (icao24, snapshot_time) DO NOTHING
            """).format(
                sql.Identifier(TABLE_SCHEMA),
                sql.Identifier(TABLE_NAME),
                sql.SQL(", ").join(
                    sql.Identifier(column) for column in COLUMNS
                ),
                sql.SQL(", ").join(
                    sql.Identifier(column) for column in COLUMNS
                ),
                sql.Identifier(staging_table),
            )

            cur.execute(insert_query)

            loaded_count = cur.rowcount

    print("Load successful")
    print(f"Source records: {len(df)}")
    print(f"Inserted records: {loaded_count}")
    print(f"Source file: {parquet_file.name}")
    print(f"Target table: {TABLE_SCHEMA}.{TABLE_NAME}")


if __name__ == "__main__":
    latest_parquet = max(
        PROCESSED_DIR.glob("*_processed.parquet"),
        key=lambda f: f.stat().st_mtime,
    )

    load_data(latest_parquet)
