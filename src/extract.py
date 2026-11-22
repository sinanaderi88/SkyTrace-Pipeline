import requests
import json
from pathlib import Path
from datetime import datetime, timezone


API_URL = "https://opensky-network.org/api/states/all"

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def extract_data():
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    data = response.json()

    if "states" not in data:
        raise ValueError("Invalid API response: 'states' field is missing")

    extracted_at = datetime.now(timezone.utc)
    filename = extracted_at.strftime("opensky_%Y%m%d_%H%M%S.json")

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    file_path = RAW_DIR / filename

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    aircraft_count = len(data["states"] or [])

    print(f"Extraction successful")
    print(f"Aircraft records: {aircraft_count}")
    print(f"Saved to: {file_path}")

    return file_path


if __name__ == "__main__":
    extract_data()
