import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from ..direct_db import db

logger = logging.getLogger(__name__)

class DataSyncService:
    """Service for managing storm data from database (populated by Airflow)"""
    
    def __init__(self):
        # No external API calls needed - data comes from Airflow
        self.is_running = False
    
    async def get_database_stats(self):
        """Get statistics about data in database"""
        try:
            if not db.connection:
                db.connect()
            
            stats = db.get_database_stats()
            return stats
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {
                "total_storms": 0,
                "total_tracks": 0,
                "total_forecasts": 0,
                "last_update": None
            }
    
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old storm data"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            db = SessionLocal()
            try:
                # Delete old tracks and forecasts
                old_tracks = db.query(Track).filter(Track.created_at < cutoff_date).delete()
                old_forecasts = db.query(Forecast).filter(Forecast.created_at < cutoff_date).delete()
                
                db.commit()
                logger.info(f"Cleaned up {old_tracks} old tracks and {old_forecasts} old forecasts")
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

# Global sync service instance
sync_service = DataSyncService()

# Note: No background sync needed since Airflow handles data ingestion