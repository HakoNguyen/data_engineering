import os
import psycopg2
from pathlib import Path
import logging

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

def save_to_postgres_dag(storm_csv, track_csv, forecast_csv):
    try:
        pg_host = os.getenv("PG_HOST", "postgres")
        pg_port = int(os.getenv("PG_PORT", "5432"))
        pg_db = os.getenv("PG_DB", "airflow")
        pg_user = os.getenv("PG_USER", "airflow")
        pg_password = os.getenv("PG_PASSWORD", "airflow")

        conn = psycopg2.connect(
            dbname=pg_db,
            user=pg_user,
            password=pg_password,
            host=pg_host,
            port=pg_port,
        )
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS storm (
                storm_id text PRIMARY KEY,
                name text,
                start_time text,
                basin text,
                event text,
                storm_type text,
                storm_cat text,
                lon double precision,
                lat double precision
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS track (
                storm_id text NOT NULL,
                track_time text, 
                track_name text,
                storm_type text,
                storm_cat text,
                advisory text,
                directionDEG double precision,
                speed double precision,
                wind_speed double precision,
                gust_speed double precision,
                pressure double precision,
                lon double precision,
                lat double precision,
                CONSTRAINT fk_track_storm
                FOREIGN KEY(storm_id)
                REFERENCES storm(storm_id)
                ON DELETE CASCADE
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS forecast (
                storm_id text NOT NULL,
                forecast_time text,
                forecast_name text,
                storm_type text,
                storm_cat text,
                advisory text,
                directionDEG double precision,
                speed double precision,
                wind_speed double precision,
                gust_speed double precision,
                pressure double precision,
                lon double precision,
                lat double precision,
                CONSTRAINT fk_forecast_storm
                FOREIGN KEY(storm_id)
                REFERENCES storm(storm_id)
                ON DELETE CASCADE
            );
            """
        )
        cur.execute("TRUNCATE TABLE track, forecast, storm;")

        with open(PROCESSED_DIR / "storm.csv", "r", encoding="utf-8") as f:
            cur.copy_expert("COPY storm FROM STDIN WITH CSV HEADER", f)

        with open(PROCESSED_DIR / "track.csv", "r", encoding="utf-8") as f:
            cur.copy_expert(
                "COPY track (storm_id, track_time, track_name, storm_type, storm_cat, advisory, directionDEG, speed, wind_speed, gust_speed, pressure, lon, lat) FROM STDIN WITH CSV HEADER",
                f,
            )
        with open(PROCESSED_DIR / "forecast.csv", "r", encoding="utf-8") as f:
            cur.copy_expert(
                "COPY forecast (storm_id, forecast_time, forecast_name, storm_type, storm_cat, advisory, directionDEG, speed, wind_speed, gust_speed, pressure, lon, lat) FROM STDIN WITH CSV HEADER",
                f,
            )

        cur.close()
        conn.close()
        logging.info("data loaded into Postgres service 'postgres'")
        return True
    except Exception as e:
        logging.error(f"Failed to load: {e}")
        return False