from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional
from datetime import datetime, timedelta
from .model import Storm, Track, Forecast

class StormCRUD:
    @staticmethod
    def get_storm(db: Session, storm_id: str):
        return db.query(Storm).filter(Storm.storm_id == storm_id).first()
    
    @staticmethod
    def get_storms(db: Session, skip: int = 0, limit: int = 100, basin: Optional[str] = None):
        query = db.query(Storm)
        if basin:
            query = query.filter(Storm.basin == basin)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_active_storms(db: Session):
        # Active storms are those with recent tracks or forecasts
        return db.query(Storm).join(Track).distinct().all()
    
    @staticmethod
    def create_storm(db: Session, storm_data: dict):
        db_storm = Storm(**storm_data)
        db.add(db_storm)
        db.commit()
        db.refresh(db_storm)
        return db_storm
    
    @staticmethod
    def update_storm(db: Session, storm_id: str, storm_data: dict):
        db_storm = db.query(Storm).filter(Storm.storm_id == storm_id).first()
        if db_storm:
            for key, value in storm_data.items():
                if value is not None:
                    setattr(db_storm, key, value)
            db_storm.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_storm)
        return db_storm
    
    @staticmethod
    def delete_storm(db: Session, storm_id: str):
        db_storm = db.query(Storm).filter(Storm.storm_id == storm_id).first()
        if db_storm:
            db.delete(db_storm)
            db.commit()
        return db_storm
    
    @staticmethod
    def upsert_storm(db: Session, storm_data: dict):
        """Insert or update storm data"""
        existing_storm = db.query(Storm).filter(Storm.storm_id == storm_data["storm_id"]).first()
        
        if existing_storm:
            # Update existing storm
            for key, value in storm_data.items():
                if value is not None:
                    setattr(existing_storm, key, value)
            existing_storm.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_storm)
            return existing_storm
        else:
            # Create new storm
            db_storm = Storm(**storm_data)
            db.add(db_storm)
            db.commit()
            db.refresh(db_storm)
            return db_storm

class TrackCRUD:
    @staticmethod
    def get_tracks_by_storm(db: Session, storm_id: str, skip: int = 0, limit: int = 1000):
        return db.query(Track).filter(Track.storm_id == storm_id).order_by(Track.track_time).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_latest_track(db: Session, storm_id: str):
        return db.query(Track).filter(Track.storm_id == storm_id).order_by(desc(Track.track_time)).first()
    
    @staticmethod
    def create_track(db: Session, track_data: dict):
        db_track = Track(**track_data)
        db.add(db_track)
        db.commit()
        db.refresh(db_track)
        return db_track
    
    @staticmethod
    def create_multiple_tracks(db: Session, tracks_data: List[dict]):
        db_tracks = [Track(**track_data) for track_data in tracks_data]
        db.add_all(db_tracks)
        db.commit()
        for track in db_tracks:
            db.refresh(track)
        return db_tracks
    
    @staticmethod
    def get_tracks_in_timeframe(db: Session, storm_id: str, start_time: str, end_time: str):
        return db.query(Track).filter(
            and_(
                Track.storm_id == storm_id,
                Track.track_time >= start_time,
                Track.track_time <= end_time
            )
        ).order_by(Track.track_time).all()
    
    @staticmethod
    def delete_tracks_by_storm(db: Session, storm_id: str):
        db.query(Track).filter(Track.storm_id == storm_id).delete()
        db.commit()
    
    @staticmethod
    def upsert_tracks(db: Session, storm_id: str, tracks_data: List[dict]):
        """Replace all tracks for a storm with new data"""
        # Delete existing tracks
        TrackCRUD.delete_tracks_by_storm(db, storm_id)
        
        # Add new tracks
        if tracks_data:
            return TrackCRUD.create_multiple_tracks(db, tracks_data)
        return []

class ForecastCRUD:
    @staticmethod
    def get_forecasts_by_storm(db: Session, storm_id: str, skip: int = 0, limit: int = 1000):
        return db.query(Forecast).filter(Forecast.storm_id == storm_id).order_by(Forecast.forecast_time).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_latest_forecasts(db: Session, storm_id: str):
        return db.query(Forecast).filter(Forecast.storm_id == storm_id).order_by(Forecast.forecast_time).all()
    
    @staticmethod
    def create_forecast(db: Session, forecast_data: dict):
        db_forecast = Forecast(**forecast_data)
        db.add(db_forecast)
        db.commit()
        db.refresh(db_forecast)
        return db_forecast
    
    @staticmethod
    def create_multiple_forecasts(db: Session, forecasts_data: List[dict]):
        db_forecasts = [Forecast(**forecast_data) for forecast_data in forecasts_data]
        db.add_all(db_forecasts)
        db.commit()
        for forecast in db_forecasts:
            db.refresh(forecast)
        return db_forecasts
    
    @staticmethod
    def delete_forecasts_by_storm(db: Session, storm_id: str):
        db.query(Forecast).filter(Forecast.storm_id == storm_id).delete()
        db.commit()
    
    @staticmethod
    def upsert_forecasts(db: Session, storm_id: str, forecasts_data: List[dict]):
        """Replace all forecasts for a storm with new data"""
        # Delete existing forecasts
        ForecastCRUD.delete_forecasts_by_storm(db, storm_id)
        
        # Add new forecasts
        if forecasts_data:
            return ForecastCRUD.create_multiple_forecasts(db, forecasts_data)
        return []

class StormAnalytics:
    @staticmethod
    def get_storm_summary(db: Session, storm_id: str):
        storm = db.query(Storm).filter(Storm.storm_id == storm_id).first()
        if not storm:
            return None
        
        track_count = db.query(func.count(Track.id)).filter(Track.storm_id == storm_id).scalar()
        forecast_count = db.query(func.count(Forecast.id)).filter(Forecast.storm_id == storm_id).scalar()
        
        latest_track = TrackCRUD.get_latest_track(db, storm_id)
        last_update = latest_track.created_at if latest_track else storm.updated_at
        
        return {
            "storm_id": storm.storm_id,
            "name": storm.name,
            "basin": storm.basin,
            "event": storm.event,
            "storm_type": storm.storm_type,
            "storm_cat": storm.storm_cat,
            "lon": storm.lon,
            "lat": storm.lat,
            "track_count": track_count,
            "forecast_count": forecast_count,
            "last_update": last_update
        }
    
    @staticmethod
    def get_storms_by_basin(db: Session, basin: str):
        return db.query(Storm).filter(Storm.basin == basin).all()
    
    @staticmethod
    def get_storm_intensity_history(db: Session, storm_id: str):
        tracks = db.query(Track).filter(Track.storm_id == storm_id).order_by(Track.track_time).all()
        return [
            {
                "track_time": track.track_time,
                "wind_speed": track.wind_speed,
                "pressure": track.pressure,
                "storm_cat": track.storm_cat,
                "lat": track.lat,
                "lon": track.lon
            }
            for track in tracks
        ]
    
    @staticmethod
    def get_forecast_intensity_history(db: Session, storm_id: str):
        forecasts = db.query(Forecast).filter(Forecast.storm_id == storm_id).order_by(Forecast.forecast_time).all()
        return [
            {
                "forecast_time": forecast.forecast_time,
                "wind_speed": forecast.wind_speed,
                "pressure": forecast.pressure,
                "storm_cat": forecast.storm_cat,
                "lat": forecast.lat,
                "lon": forecast.lon
            }
            for forecast in forecasts
        ]