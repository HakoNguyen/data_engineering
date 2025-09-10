import requests
import os
import json
from pathlib import Path
from datetime import datetime
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


""" Lay file Json moi nhat """
files = sorted(RAW_DIR.glob('xweather_storms_*.json'))
if not files:
    raise FileNotFoundError(" No JSON file found ")
latest_file = files[-1]

with open(latest_file, 'r') as f:
    data = json.load(f)

def extract_storm(data):
    storms = data.get('response', [])
    storm_records = []

    for storm in storms:
        info = storm.get('profile', {})
        loc =  storm.get('position', {}).get('location', {}).get("coordinates", [None, None])

        storm_records.append({
            'storm_id': storm.get("id"),
            'name': info.get('name'),
            'start_time': info.get("lifespan", {}).get("startDateTimeISO"),
            'basin': info.get('basinCurrent'),
            'event': info.get('event'),
            'storm_type': info.get('maxStormType'),
            'storm_cat': info.get('maxStormCat'),
            'lon': loc[0],
            'lat': loc[1]
    })
    return storm_records

def extract_track(data):
    storms = data.get("response", [])
    track_records = []
    
    for storm in storms:  
        storm_id = storm.get("id")
        tracks = storm.get("track", [])
        
        for track in tracks:
            details = track.get("details", {})
            coords = track.get("location", {}).get("coordinates", [None, None])
            track_records.append({
                "storm_id": storm_id,
                "track_name": details.get("stormName"),
                "storm_type": details.get("stormType"),
                "storm_cat": details.get("stormCat"),
                "advisory": details.get("advisoryNumber"),
                'directionDEG': details.get('movement', {}).get('directionDEG'),
                'speed': details.get('movement', {}).get('speedKTS'),
                'wind_speed': details.get('windSpeedKPH'),
                'gust_speed': details.get('gustSpeedKPH'),
                'pressure': details.get('pressureMB'),
                "lon": coords[0],
                "lat": coords[1],
            })
    return  track_records

storm_df = pd.DataFrame(extract_storm(data))
track_df = pd.DataFrame(extract_track(data))

def save_csv(df, file_name, folder=PROCESSED_DIR):
    file_path = folder / file_name
    try:
        if file_path.exists():
            os.remove(file_path)
            print("Delete old file")
        df.to_csv(file_path, index=False)
        print('Saved')
    except Exception as e:
        print(f'Warn {e}')

def transform(json_path: str):

    with open(json_path, "r") as f: 
        data = json.load(f)

    storm_df = pd.DataFrame(extract_storm(data))
    track_df = pd.DataFrame(extract_track(data))

    storm_csv, track_csv = None, None

    if not storm_df.empty:
            storm_csv = save_csv(storm_df, "storm.csv")
    else:
            print("⚠️ storm_df is empty, skip saving storm.csv")

    if not track_df.empty:
            track_csv = save_csv(track_df, "track.csv")
    else:
            print("⚠️ track_df is empty, skip saving track.csv")

    return storm_csv, track_csv

if __name__ == "__main__":
    transform(str(latest_file))
