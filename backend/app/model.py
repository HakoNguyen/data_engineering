from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

Base = declarative_base()

# Database Models - Updated to match XWeather API structure
class Storm(Base):
    __tablename__ = "storm"
    
    storm_id = Column(String, primary_key=True)  # XWeather storm ID
    name = Column(String, nullable=True)
    start_time = Column(String, nullable=True)  # startDateTimeISO from API
    basin = Column(String, nullable=True)  # basinCurrent from API
    event = Column(String, nullable=True)  # event from API
    storm_type = Column(String, nullable=True)  # maxStormType from API
    storm_cat = Column(String, nullable=True)  # maxStormCat from API
    lon = Column(Float, nullable=True)  # longitude from position.coordinates
    lat = Column(Float, nullable=True)  # latitude from position.coordinates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tracks = relationship("Track", back_populates="storm", cascade="all, delete-orphan")
    forecasts = relationship("Forecast", back_populates="storm", cascade="all, delete-orphan")

class Track(Base):
    __tablename__ = "track"
    
    id = Column(Integer, primary_key=True, index=True)
    storm_id = Column(String, ForeignKey("storm.storm_id"), nullable=False)
    track_time = Column(String, nullable=True)  # dateTimeISO from API
    track_name = Column(String, nullable=True)  # stormName from details
    storm_type = Column(String, nullable=True)  # stormType from details
    storm_cat = Column(String, nullable=True)  # stormCat from details
    advisory = Column(String, nullable=True)  # advisoryNumber from details
    directionDEG = Column(Float, nullable=True)  # directionDEG from movement
    speed = Column(Float, nullable=True)  # speedKTS from movement
    wind_speed = Column(Float, nullable=True)  # windSpeedKPH from details
    gust_speed = Column(Float, nullable=True)  # gustSpeedKPH from details
    pressure = Column(Float, nullable=True)  # pressureMB from details
    lon = Column(Float, nullable=True)  # longitude from location.coordinates
    lat = Column(Float, nullable=True)  # latitude from location.coordinates
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    storm = relationship("Storm", back_populates="tracks")

class Forecast(Base):
    __tablename__ = "forecast"
    
    id = Column(Integer, primary_key=True, index=True)
    storm_id = Column(String, ForeignKey("storm.storm_id"), nullable=False)
    forecast_time = Column(String, nullable=True)  # dateTimeISO from API
    forecast_name = Column(String, nullable=True)  # stormName from details
    storm_type = Column(String, nullable=True)  # stormType from details
    storm_cat = Column(String, nullable=True)  # stormCat from details
    advisory = Column(String, nullable=True)  # advisoryNumber from details
    directionDEG = Column(Float, nullable=True)  # directionDEG from movement
    speed = Column(Float, nullable=True)  # speedKTS from movement
    wind_speed = Column(Float, nullable=True)  # windSpeedKPH from details
    gust_speed = Column(Float, nullable=True)  # gustSpeedKPH from details
    pressure = Column(Float, nullable=True)  # pressureMB from details
    lon = Column(Float, nullable=True)  # longitude from location.coordinates
    lat = Column(Float, nullable=True)  # latitude from location.coordinates
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    storm = relationship("Storm", back_populates="forecasts")

# Pydantic Models for API - Updated to match XWeather structure
class StormBase(BaseModel):
    storm_id: str
    name: Optional[str] = None
    start_time: Optional[str] = None
    basin: Optional[str] = None
    event: Optional[str] = None
    storm_type: Optional[str] = None
    storm_cat: Optional[str] = None
    lon: Optional[float] = None
    lat: Optional[float] = None

class StormCreate(StormBase):
    pass

class StormUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[str] = None
    basin: Optional[str] = None
    event: Optional[str] = None
    storm_type: Optional[str] = None
    storm_cat: Optional[str] = None
    lon: Optional[float] = None
    lat: Optional[float] = None

class StormResponse(StormBase):
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TrackBase(BaseModel):
    storm_id: str
    track_time: Optional[str] = None
    track_name: Optional[str] = None
    storm_type: Optional[str] = None
    storm_cat: Optional[str] = None
    advisory: Optional[str] = None
    directionDEG: Optional[float] = None
    speed: Optional[float] = None
    wind_speed: Optional[float] = None
    gust_speed: Optional[float] = None
    pressure: Optional[float] = None
    lon: Optional[float] = None
    lat: Optional[float] = None

class TrackCreate(TrackBase):
    pass

class TrackResponse(TrackBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ForecastBase(BaseModel):
    storm_id: str
    forecast_time: Optional[str] = None
    forecast_name: Optional[str] = None
    storm_type: Optional[str] = None
    storm_cat: Optional[str] = None
    advisory: Optional[str] = None
    directionDEG: Optional[float] = None
    speed: Optional[float] = None
    wind_speed: Optional[float] = None
    gust_speed: Optional[float] = None
    pressure: Optional[float] = None
    lon: Optional[float] = None
    lat: Optional[float] = None

class ForecastCreate(ForecastBase):
    pass

class ForecastResponse(ForecastBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class StormWithTracksAndForecasts(StormResponse):
    tracks: List[TrackResponse] = []
    forecasts: List[ForecastResponse] = []

class StormSummary(BaseModel):
    storm_id: str
    name: Optional[str] = None
    basin: Optional[str] = None
    event: Optional[str] = None
    storm_type: Optional[str] = None
    storm_cat: Optional[str] = None
    lon: Optional[float] = None
    lat: Optional[float] = None
    track_count: int = 0
    forecast_count: int = 0
    last_update: Optional[datetime] = None

# Basin mapping for XWeather API
class BasinMapping:
    BASIN_NAMES = {
        "AL": "Atlantic",
        "EP": "Eastern Pacific", 
        "CP": "Central Pacific",
        "WP": "Western Pacific",
        "IO": "Indian Ocean",
        "SH": "Southern Hemisphere"
    }
    
    @classmethod
    def get_basin_name(cls, basin_code: str) -> str:
        return cls.BASIN_NAMES.get(basin_code, basin_code)

# Storm category mapping
class StormCategoryMapping:
    CATEGORY_NAMES = {
        "TD": "Tropical Depression",
        "TS": "Tropical Storm", 
        "H1": "Category 1 Hurricane",
        "H2": "Category 2 Hurricane",
        "H3": "Category 3 Hurricane",
        "H4": "Category 4 Hurricane",
        "H5": "Category 5 Hurricane",
        "EX": "Extratropical",
        "SS": "Subtropical Storm",
        "SD": "Subtropical Depression"
    }
    
    @classmethod
    def get_category_name(cls, category_code: str) -> str:
        return cls.CATEGORY_NAMES.get(category_code, category_code)