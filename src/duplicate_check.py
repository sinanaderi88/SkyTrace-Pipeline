
import getpass

import psycopg


DB_CONFIG = {
    "host": "localhost",
    "dbname": "opensky_db",
    "user": "opensky_user",
}

TABLE_NAME = "opensky.aircraft_states"


def duplicate_check():
    password = getpass.getpass("PostgreSQL password: ")

    query = f"""
        SELECT
            icao24,
            snapshot_time,
            COUNT(*) AS duplicate_count
        FROM {TABLE_NAME}
        GROUP BY icao24, snapshot_time
        HAVING COUNT(*) > 1
        ORDER BY duplicate_count DESC;
    """

    with psycopg.connect(**DB_CONFIG, password=password) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            duplicates = cur.fetchall()

    print("\nDuplicate Check Results")
    print("-" * 50)

    if not duplicates:
        print("No duplicate records found.")
    else:
        print(f"Duplicate groups found: {len(duplicates)}")

        for row in duplicates:
            print(
                f"icao24: {row[0]} | "
                f"snapshot_time: {row[1]} | "
                f"count: {row[2]}"
            )


if __name__ == "__main__":
    duplicate_check()

