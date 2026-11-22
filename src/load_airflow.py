import os
import io

import pandas as pd

from airflow.providers.postgres.hooks.postgres import PostgresHook


DB_SCHEMA = "opensky"
DB_TABLE = "aircraft_states"
CONNECTION_ID = "skytrace_postgres"

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

    if not os.path.exists(parquet_file):
        raise FileNotFoundError(parquet_file)

    df = pd.read_parquet(parquet_file)

    if df.empty:
        print("No data to load.")
        return 0

    missing_columns = set(COLUMNS) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    df = df[COLUMNS]

    hook = PostgresHook(postgres_conn_id=CONNECTION_ID)
    conn = hook.get_conn()

    try:
        with conn.cursor() as cur:

            cur.execute(
                f"""
                CREATE TEMP TABLE aircraft_states_staging
                (LIKE {DB_SCHEMA}.{DB_TABLE} INCLUDING DEFAULTS)
                ON COMMIT DROP
                """
            )

            buffer = io.StringIO()

            df.to_csv(
                buffer,
                index=False,
                header=False,
                na_rep="",
            )

            buffer.seek(0)

            copy_sql = f"""
                COPY aircraft_states_staging ({', '.join(COLUMNS)})
                FROM STDIN WITH (FORMAT CSV)
            """

            with cur.copy(copy_sql) as copy:
                copy.write(buffer.getvalue().encode("utf-8"))

            insert_sql = f"""
                INSERT INTO {DB_SCHEMA}.{DB_TABLE}
                ({', '.join(COLUMNS)})
                SELECT {', '.join(COLUMNS)}
                FROM aircraft_states_staging
                ON CONFLICT (icao24, snapshot_time)
                DO NOTHING
            """

            cur.execute(insert_sql)

            inserted_rows = cur.rowcount

        conn.commit()

        print(f"Successfully loaded {inserted_rows} records.")

        return inserted_rows

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
