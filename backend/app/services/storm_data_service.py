import httpx
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class StormDataService:
    """Service for fetching real storm data from external APIs"""
    
    def __init__(self):
        self.nhc_base_url = "https://www.nhc.noaa.gov"
        self.noaa_api_key = None  # Set this from environment variables
        self.timeout = 30.0
    
    async def fetch_active_storms(self) -> List[Dict]:
        """Fetch currently active storms from NHC"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # NHC provides active storms in various formats
                # This is a simplified example - in reality you'd parse their XML/JSON feeds
                response = await client.get(f"{self.nhc_base_url}/json/active_storms.json")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching active storms: {e}")
            return []
    
    async def fetch_storm_data(self, storm_id: str) -> Optional[Dict]:
        """Fetch detailed data for a specific storm"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Fetch storm advisory data
                advisory_url = f"{self.nhc_base_url}/json/{storm_id}_advisory.json"
                response = await client.get(advisory_url)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching storm data for {storm_id}: {e}")
            return None
    
    async def fetch_storm_track(self, storm_id: str) -> List[Dict]:
        """Fetch track data for a specific storm"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Fetch track data
                track_url = f"{self.nhc_base_url}/json/{storm_id}_track.json"
                response = await client.get(track_url)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching track data for {storm_id}: {e}")
            return []
    
    async def fetch_storm_forecast(self, storm_id: str) -> List[Dict]:
        """Fetch forecast data for a specific storm"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Fetch forecast data
                forecast_url = f"{self.nhc_base_url}/json/{storm_id}_forecast.json"
                response = await client.get(forecast_url)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching forecast data for {storm_id}: {e}")
            return []
    
    def parse_storm_data(self, raw_data: Dict) -> Dict:
        """Parse raw storm data into our format"""
        try:
            # This is a simplified parser - in reality you'd need to handle
            # the specific format of NHC data
            return {
                "storm_id": raw_data.get("storm_id", ""),
                "name": raw_data.get("name", ""),
                "basin": raw_data.get("basin", "ATL"),
                "season": raw_data.get("season", datetime.now().year),
                "status": raw_data.get("status", "ACTIVE"),
                "category": raw_data.get("category"),
                "max_wind_speed": raw_data.get("max_wind_speed"),
                "min_pressure": raw_data.get("min_pressure"),
                "start_date": self._parse_datetime(raw_data.get("start_date")),
                "end_date": self._parse_datetime(raw_data.get("end_date"))
            }
        except Exception as e:
            logger.error(f"Error parsing storm data: {e}")
            return {}
    
    def parse_track_data(self, raw_data: List[Dict], storm_id: int) -> List[Dict]:
        """Parse raw track data into our format"""
        try:
            tracks = []
            for point in raw_data:
                track = {
                    "storm_id": storm_id,
                    "latitude": float(point.get("lat", 0)),
                    "longitude": float(point.get("lon", 0)),
                    "wind_speed": point.get("wind_speed"),
                    "pressure": point.get("pressure"),
                    "category": point.get("category"),
                    "timestamp": self._parse_datetime(point.get("timestamp"))
                }
                tracks.append(track)
            return tracks
        except Exception as e:
            logger.error(f"Error parsing track data: {e}")
            return []
    
    def parse_forecast_data(self, raw_data: List[Dict], storm_id: int) -> List[Dict]:
        """Parse raw forecast data into our format"""
        try:
            forecasts = []
            for point in raw_data:
                forecast = {
                    "storm_id": storm_id,
                    "forecast_hour": int(point.get("forecast_hour", 0)),
                    "latitude": float(point.get("lat", 0)),
                    "longitude": float(point.get("lon", 0)),
                    "wind_speed": point.get("wind_speed"),
                    "pressure": point.get("pressure"),
                    "category": point.get("category"),
                    "forecast_time": self._parse_datetime(point.get("forecast_time"))
                }
                forecasts.append(forecast)
            return forecasts
        except Exception as e:
            logger.error(f"Error parsing forecast data: {e}")
            return []
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not date_str:
            return None
        
        try:
            # Handle various datetime formats
            formats = [
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If none of the formats work, try parsing with dateutil
            from dateutil import parser
            return parser.parse(date_str)
        except Exception as e:
            logger.error(f"Error parsing datetime {date_str}: {e}")
            return None

class MockStormDataService(StormDataService):
    """Mock service for development and testing"""
    
    async def fetch_active_storms(self) -> List[Dict]:
        """Return mock active storms data"""
        return [
            {
                "storm_id": "AL012024",
                "name": "Hurricane Test",
                "basin": "ATL",
                "season": 2024,
                "status": "ACTIVE",
                "category": "CATEGORY_3",
                "max_wind_speed": 120.0,
                "min_pressure": 950.0,
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": None
            },
            {
                "storm_id": "AL022024",
                "name": "Tropical Storm Demo",
                "basin": "ATL",
                "season": 2024,
                "status": "ACTIVE",
                "category": "TROPICAL_STORM",
                "max_wind_speed": 65.0,
                "min_pressure": 1000.0,
                "start_date": "2024-01-02T00:00:00Z",
                "end_date": None
            }
        ]
    
    async def fetch_storm_track(self, storm_id: str) -> List[Dict]:
        """Return mock track data"""
        # Generate mock track points
        base_lat = 25.0
        base_lon = -80.0
        tracks = []
        
        for i in range(10):
            track = {
                "lat": base_lat + (i * 0.5),
                "lon": base_lon + (i * 0.3),
                "wind_speed": 100.0 - (i * 2),
                "pressure": 960.0 + (i * 5),
                "category": "CATEGORY_2" if i < 5 else "TROPICAL_STORM",
                "timestamp": (datetime.now() - timedelta(hours=24-i*2)).isoformat()
            }
            tracks.append(track)
        
        return tracks
    
    async def fetch_storm_forecast(self, storm_id: str) -> List[Dict]:
        """Return mock forecast data"""
        # Generate mock forecast points
        base_lat = 30.0
        base_lon = -75.0
        forecasts = []
        
        for i in range(12):  # 5 days of forecasts (every 12 hours)
            forecast = {
                "lat": base_lat + (i * 0.8),
                "lon": base_lon + (i * 0.5),
                "wind_speed": 80.0 - (i * 3),
                "pressure": 980.0 + (i * 8),
                "category": "TROPICAL_STORM" if i < 6 else "TROPICAL_DEPRESSION",
                "forecast_hour": i * 12,
                "forecast_time": (datetime.now() + timedelta(hours=i*12)).isoformat()
            }
            forecasts.append(forecast)
        
        return forecasts

# Factory function to get the appropriate service
def get_storm_data_service(use_mock: bool = True) -> StormDataService:
    """Get storm data service instance"""
    if use_mock:
        return MockStormDataService()
    else:
        return StormDataService()
