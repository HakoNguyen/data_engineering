import requests
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import os
import logging

# Cấu hình logging để hiển thị ra console
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def _load_env_variables():

    load_dotenv(BASE_DIR.parent / ".env")

def fetch_xweather_storms(limit: int = 10):
    try:
        _load_env_variables()
        CLIENT_ID = os.getenv("client_id")
        CLIENT_SECRET = os.getenv("client_secret")

        if not CLIENT_ID or not CLIENT_SECRET:
            raise ValueError("Missing client_id or client_secret in environment")

        url = (
            f"https://data.api.xweather.com/tropicalcyclones?"
            f"p=&filter=all&limit={limit}"
            f"&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}"
        )
        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"API error {response.status_code}: {response.text}")

        data = response.json()

        file_name = DATA_DIR / f"xweather_storms_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(file_name, "w") as f:
            json.dump(data, f, indent=2)

        logging.info(f"[OK] Saved to {file_name}")
        return str(file_name)

    except Exception as e:
        logging.error(f"[ERROR] Fetch failed: {e}")
        return None

if __name__ == "__main__":
    output = fetch_xweather_storms()
    print("File output:", output)
