#!/usr/bin/env python3
"""
Migration script to convert data from old structure to XWeather API structure
"""
import os
import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.config import settings
from app.crud import StormCRUD, TrackCRUD, ForecastCRUD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_from_csv(csv_dir: str):
    """Migrate data from CSV files to new database structure"""
    try:
        # Connect to database
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Create tables
        from app.model import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
        
        csv_path = Path(csv_dir)
        
        # Migrate storm data
        storm_csv = csv_path / "storm.csv"
        if storm_csv.exists():
            logger.info("Migrating storm data...")
            storm_df = pd.read_csv(storm_csv)
            
            for _, row in storm_df.iterrows():
                storm_data = {
                    "storm_id": str(row["storm_id"]),
                    "name": row.get("name"),
                    "start_time": row.get("start_time"),
                    "basin": row.get("basin"),
                    "event": row.get("event"),
                    "storm_type": row.get("storm_type"),
                    "storm_cat": row.get("storm_cat"),
                    "lon": row.get("lon"),
                    "lat": row.get("lat")
                }
                
                # Remove None values
                storm_data = {k: v for k, v in storm_data.items() if pd.notna(v)}
                
                StormCRUD.upsert_storm(db, storm_data)
            
            logger.info(f"Migrated {len(storm_df)} storm records")
        
        # Migrate track data
        track_csv = csv_path / "track.csv"
        if track_csv.exists():
            logger.info("Migrating track data...")
            track_df = pd.read_csv(track_csv)
            
            # Group by storm_id and insert in batches
            for storm_id, group in track_df.groupby("storm_id"):
                track_records = []
                for _, row in group.iterrows():
                    track_data = {
                        "storm_id": str(row["storm_id"]),
                        "track_time": row.get("track_time"),
                        "track_name": row.get("track_name"),
                        "storm_type": row.get("storm_type"),
                        "storm_cat": row.get("storm_cat"),
                        "advisory": row.get("advisory"),
                        "directionDEG": row.get("directionDEG"),
                        "speed": row.get("speed"),
                        "wind_speed": row.get("wind_speed"),
                        "gust_speed": row.get("gust_speed"),
                        "pressure": row.get("pressure"),
                        "lon": row.get("lon"),
                        "lat": row.get("lat")
                    }
                    
                    # Remove None values
                    track_data = {k: v for k, v in track_data.items() if pd.notna(v)}
                    track_records.append(track_data)
                
                if track_records:
                    TrackCRUD.upsert_tracks(db, str(storm_id), track_records)
            
            logger.info(f"Migrated {len(track_df)} track records")
        
        # Migrate forecast data
        forecast_csv = csv_path / "forecast.csv"
        if forecast_csv.exists():
            logger.info("Migrating forecast data...")
            forecast_df = pd.read_csv(forecast_csv)
            
            # Group by storm_id and insert in batches
            for storm_id, group in forecast_df.groupby("storm_id"):
                forecast_records = []
                for _, row in group.iterrows():
                    forecast_data = {
                        "storm_id": str(row["storm_id"]),
                        "forecast_time": row.get("forecast_time"),
                        "forecast_name": row.get("forecast_name"),
                        "storm_type": row.get("storm_type"),
                        "storm_cat": row.get("storm_cat"),
                        "advisory": row.get("advisory"),
                        "directionDEG": row.get("directionDEG"),
                        "speed": row.get("speed"),
                        "wind_speed": row.get("wind_speed"),
                        "gust_speed": row.get("gust_speed"),
                        "pressure": row.get("pressure"),
                        "lon": row.get("lon"),
                        "lat": row.get("lat")
                    }
                    
                    # Remove None values
                    forecast_data = {k: v for k, v in forecast_data.items() if pd.notna(v)}
                    forecast_records.append(forecast_data)
                
                if forecast_records:
                    ForecastCRUD.upsert_forecasts(db, str(storm_id), forecast_records)
            
            logger.info(f"Migrated {len(forecast_df)} forecast records")
        
        db.commit()
        db.close()
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

def migrate_from_old_database():
    """Migrate data from old database structure to new structure"""
    try:
        # Connect to old database (if exists)
        old_engine = create_engine("postgresql://postgres:password@localhost:5432/xweather_old")
        old_session = sessionmaker(autocommit=False, autoflush=False, bind=old_engine)
        old_db = old_session()
        
        # Connect to new database
        new_engine = create_engine(settings.DATABASE_URL)
        new_session = sessionmaker(autocommit=False, autoflush=False, bind=new_engine)
        new_db = new_session()
        
        # Create new tables
        from app.model import Base
        Base.metadata.create_all(bind=new_engine)
        
        # Migrate storms
        logger.info("Migrating storms from old database...")
        old_storms = old_db.execute(text("SELECT * FROM storms")).fetchall()
        
        for storm in old_storms:
            storm_data = {
                "storm_id": storm.storm_id,
                "name": storm.name,
                "start_time": storm.start_date.isoformat() if storm.start_date else None,
                "basin": storm.basin,
                "event": "Hurricane",  # Default event
                "storm_type": storm.category,
                "storm_cat": storm.category,
                "lon": None,  # Will be updated from tracks
                "lat": None   # Will be updated from tracks
            }
            
            StormCRUD.upsert_storm(new_db, storm_data)
        
        # Migrate tracks
        logger.info("Migrating tracks from old database...")
        old_tracks = old_db.execute(text("SELECT * FROM tracks")).fetchall()
        
        for track in old_tracks:
            track_data = {
                "storm_id": track.storm_id,
                "track_time": track.timestamp.isoformat(),
                "track_name": None,
                "storm_type": track.category,
                "storm_cat": track.category,
                "advisory": None,
                "directionDEG": None,
                "speed": None,
                "wind_speed": track.wind_speed,
                "gust_speed": None,
                "pressure": track.pressure,
                "lon": track.longitude,
                "lat": track.latitude
            }
            
            TrackCRUD.create_track(new_db, track_data)
        
        # Migrate forecasts
        logger.info("Migrating forecasts from old database...")
        old_forecasts = old_db.execute(text("SELECT * FROM forecasts")).fetchall()
        
        for forecast in old_forecasts:
            forecast_data = {
                "storm_id": forecast.storm_id,
                "forecast_time": forecast.forecast_time.isoformat(),
                "forecast_name": None,
                "storm_type": forecast.category,
                "storm_cat": forecast.category,
                "advisory": None,
                "directionDEG": None,
                "speed": None,
                "wind_speed": forecast.wind_speed,
                "gust_speed": None,
                "pressure": forecast.pressure,
                "lon": forecast.longitude,
                "lat": forecast.latitude
            }
            
            ForecastCRUD.create_forecast(new_db, forecast_data)
        
        new_db.commit()
        old_db.close()
        new_db.close()
        
        logger.info("Database migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        raise

def create_sample_data():
    """Create sample data for testing"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Create tables
        from app.model import Base
        Base.metadata.create_all(bind=engine)
        
        # Sample storm data
        sample_storm = {
            "storm_id": "AL012024",
            "name": "Hurricane Sample",
            "start_time": "2024-01-01T00:00:00Z",
            "basin": "AL",
            "event": "Hurricane",
            "storm_type": "Hurricane",
            "storm_cat": "H3",
            "lon": -80.0,
            "lat": 25.0
        }
        
        StormCRUD.upsert_storm(db, sample_storm)
        
        # Sample track data
        sample_tracks = [
            {
                "storm_id": "AL012024",
                "track_time": "2024-01-01T00:00:00Z",
                "track_name": "Hurricane Sample",
                "storm_type": "Hurricane",
                "storm_cat": "H3",
                "advisory": "001",
                "directionDEG": 270.0,
                "speed": 15.0,
                "wind_speed": 185.0,
                "gust_speed": 220.0,
                "pressure": 950.0,
                "lon": -80.0,
                "lat": 25.0
            },
            {
                "storm_id": "AL012024",
                "track_time": "2024-01-01T06:00:00Z",
                "track_name": "Hurricane Sample",
                "storm_type": "Hurricane",
                "storm_cat": "H3",
                "advisory": "002",
                "directionDEG": 275.0,
                "speed": 12.0,
                "wind_speed": 180.0,
                "gust_speed": 215.0,
                "pressure": 955.0,
                "lon": -79.5,
                "lat": 25.5
            }
        ]
        
        TrackCRUD.upsert_tracks(db, "AL012024", sample_tracks)
        
        # Sample forecast data
        sample_forecasts = [
            {
                "storm_id": "AL012024",
                "forecast_time": "2024-01-02T00:00:00Z",
                "forecast_name": "Hurricane Sample",
                "storm_type": "Hurricane",
                "storm_cat": "H2",
                "advisory": "003",
                "directionDEG": 280.0,
                "speed": 10.0,
                "wind_speed": 165.0,
                "gust_speed": 200.0,
                "pressure": 970.0,
                "lon": -79.0,
                "lat": 26.0
            }
        ]
        
        ForecastCRUD.upsert_forecasts(db, "AL012024", sample_forecasts)
        
        db.commit()
        db.close()
        
        logger.info("Sample data created successfully!")
        
    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate data to XWeather API structure")
    parser.add_argument("--csv-dir", help="Directory containing CSV files")
    parser.add_argument("--from-old-db", action="store_true", help="Migrate from old database")
    parser.add_argument("--create-sample", action="store_true", help="Create sample data")
    
    args = parser.parse_args()
    
    if args.csv_dir:
        migrate_from_csv(args.csv_dir)
    elif args.from_old_db:
        migrate_from_old_database()
    elif args.create_sample:
        create_sample_data()
    else:
        print("Please specify migration method: --csv-dir, --from-old-db, or --create-sample")
