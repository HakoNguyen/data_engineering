import psycopg2
import psycopg2.extras
from typing import List, Dict, Any, Optional
import logging
from urllib.parse import urlparse
from .config import settings

logger = logging.getLogger(__name__)

class DirectDB:
    """Direct database connection using psycopg2"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Connect to database"""
        try:
            # Parse settings.DATABASE_URL
            dsn = settings.DATABASE_URL
            url = urlparse(dsn)
            self.connection = psycopg2.connect(
                host=url.hostname,
                port=url.port or 5432,
                database=url.path.lstrip('/'),
                user=url.username,
                password=url.password
            )
            self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            logger.info("Connected to database successfully")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Disconnected from database")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query and return results"""
        try:
            if not self.connection:
                self.connect()
            
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = None) -> bool:
        """Execute INSERT/UPDATE/DELETE query"""
        try:
            if not self.connection:
                self.connect()
            
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Update execution failed: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def get_storms(self, limit: int = 100) -> List[Dict]:
        """Get all storms"""
        query = "SELECT * FROM storm ORDER BY start_time DESC NULLS LAST LIMIT %s"
        return self.execute_query(query, (limit,))
    
    def get_storm_by_id(self, storm_id: str) -> Optional[Dict]:
        """Get storm by ID"""
        query = "SELECT * FROM storm WHERE storm_id = %s"
        results = self.execute_query(query, (storm_id,))
        return results[0] if results else None
    
    def get_tracks_by_storm(self, storm_id: str, limit: int = 1000) -> List[Dict]:
        """Get tracks for a storm"""
        query = """
        SELECT * FROM track 
        WHERE storm_id = %s 
        ORDER BY track_time 
        LIMIT %s
        """
        return self.execute_query(query, (storm_id, limit))
    
    def get_forecasts_by_storm(self, storm_id: str, limit: int = 1000) -> List[Dict]:
        """Get forecasts for a storm"""
        query = """
        SELECT * FROM forecast 
        WHERE storm_id = %s 
        ORDER BY forecast_time 
        LIMIT %s
        """
        return self.execute_query(query, (storm_id, limit))
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            storm_count_rows = self.execute_query("SELECT COUNT(*) as count FROM storm")
            track_count_rows = self.execute_query("SELECT COUNT(*) as count FROM track")
            forecast_count_rows = self.execute_query("SELECT COUNT(*) as count FROM forecast")

            storm_count = storm_count_rows[0]['count'] if storm_count_rows else 0
            track_count = track_count_rows[0]['count'] if track_count_rows else 0
            forecast_count = forecast_count_rows[0]['count'] if forecast_count_rows else 0

            # Determine last update from the latest track_time or forecast_time
            latest_track_time_rows = self.execute_query(
                "SELECT MAX(track_time) AS last_time FROM track"
            )
            latest_forecast_time_rows = self.execute_query(
                "SELECT MAX(forecast_time) AS last_time FROM forecast"
            )

            latest_track_time = (
                latest_track_time_rows[0]['last_time'] if latest_track_time_rows else None
            )
            latest_forecast_time = (
                latest_forecast_time_rows[0]['last_time'] if latest_forecast_time_rows else None
            )

            # Choose the most recent ISO timestamp (they are strings in ISO format)
            candidates = [t for t in [latest_track_time, latest_forecast_time] if t]
            last_update = max(candidates) if candidates else None
            
            return {
                "total_storms": storm_count,
                "total_tracks": track_count,
                "total_forecasts": forecast_count,
                "last_update": last_update
            }
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {
                "total_storms": 0,
                "total_tracks": 0,
                "total_forecasts": 0,
                "last_update": None
            }
    
    def create_sample_data(self):
        """Create sample data for testing"""
        try:
            # Create storm
            storm_query = """
            INSERT INTO storm (storm_id, name, start_time, basin, event, storm_type, storm_cat, lon, lat)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (storm_id) DO NOTHING
            """
            storm_data = (
                "AL012024", "Hurricane Sample", "2024-01-01T00:00:00Z",
                "AL", "Hurricane", "Hurricane", "H3", -80.0, 25.0
            )
            self.execute_update(storm_query, storm_data)
            
            # Create tracks
            track_query = """
            INSERT INTO track (storm_id, track_time, track_name, storm_type, storm_cat, 
                             advisory, directionDEG, speed, wind_speed, gust_speed, pressure, lon, lat)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            track_data = [
                ("AL012024", "2024-01-01T00:00:00Z", "Hurricane Sample", "Hurricane", "H3",
                 "001", 270.0, 15.0, 185.0, 220.0, 950.0, -80.0, 25.0),
                ("AL012024", "2024-01-01T06:00:00Z", "Hurricane Sample", "Hurricane", "H3",
                 "002", 275.0, 12.0, 180.0, 215.0, 955.0, -79.5, 25.5)
            ]
            
            for data in track_data:
                self.execute_update(track_query, data)
            
            # Create forecasts
            forecast_query = """
            INSERT INTO forecast (storm_id, forecast_time, forecast_name, storm_type, storm_cat,
                                advisory, directionDEG, speed, wind_speed, gust_speed, pressure, lon, lat)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            forecast_data = [
                ("AL012024", "2024-01-02T00:00:00Z", "Hurricane Sample", "Hurricane", "H2",
                 "003", 280.0, 10.0, 165.0, 200.0, 970.0, -79.0, 26.0)
            ]
            
            for data in forecast_data:
                self.execute_update(forecast_query, data)
            
            logger.info("Sample data created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create sample data: {e}")
            return False

# Global instance
db = DirectDB()
