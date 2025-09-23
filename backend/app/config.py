import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # Database - Use same database as Airflow
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://airflow:airflow@localhost:5432/airflow")
    
    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # External APIs
    NOAA_API_KEY: str = os.getenv("NOAA_API_KEY", "")
    USE_MOCK_DATA: bool = os.getenv("USE_MOCK_DATA", "True").lower() == "true"
    
    # Data Sync
    SYNC_INTERVAL: int = int(os.getenv("SYNC_INTERVAL", "3600"))
    CLEANUP_DAYS: int = int(os.getenv("CLEANUP_DAYS", "30"))
    
    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001"
    ).split(",")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Storm Data
    MAX_TRACK_POINTS: int = 10000
    MAX_FORECAST_POINTS: int = 10000
    MAX_FORECAST_HOURS: int = 240  # 10 days
    
    # Visualization
    DEFAULT_MAP_CENTER: tuple = (25.0, -80.0)  # Miami, FL
    DEFAULT_ZOOM: int = 6

settings = Settings()
