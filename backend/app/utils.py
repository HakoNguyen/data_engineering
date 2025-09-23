import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import math

class GeoJSONUtils:
    """Utilities for creating GeoJSON data for visualization"""
    
    @staticmethod
    def create_point_feature(latitude: float, longitude: float, properties: Dict[str, Any] = None) -> Dict:
        """Create a GeoJSON Point feature"""
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [longitude, latitude]
            },
            "properties": properties or {}
        }
    
    @staticmethod
    def create_linestring_feature(coordinates: List[List[float]], properties: Dict[str, Any] = None) -> Dict:
        """Create a GeoJSON LineString feature"""
        return {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coordinates
            },
            "properties": properties or {}
        }
    
    @staticmethod
    def create_polygon_feature(coordinates: List[List[List[float]]], properties: Dict[str, Any] = None) -> Dict:
        """Create a GeoJSON Polygon feature"""
        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": coordinates
            },
            "properties": properties or {}
        }
    
    @staticmethod
    def create_feature_collection(features: List[Dict]) -> Dict:
        """Create a GeoJSON FeatureCollection"""
        return {
            "type": "FeatureCollection",
            "features": features
        }

class StormVisualizationUtils:
    """Utilities for storm data visualization"""
    
    @staticmethod
    def create_storm_track_geojson(tracks: List[Dict]) -> Dict:
        """Create GeoJSON for storm track visualization"""
        if not tracks:
            return GeoJSONUtils.create_feature_collection([])
        
        # Sort tracks by timestamp
        sorted_tracks = sorted(tracks, key=lambda x: x.get('timestamp', ''))
        
        # Create coordinates array
        coordinates = []
        point_features = []
        
        for i, track in enumerate(sorted_tracks):
            lat = track.get('latitude', 0)
            lon = track.get('longitude', 0)
            coordinates.append([lon, lat])
            
            # Create individual point feature for each track point
            point_properties = {
                "timestamp": track.get('timestamp'),
                "wind_speed": track.get('wind_speed'),
                "pressure": track.get('pressure'),
                "category": track.get('category'),
                "point_index": i
            }
            point_features.append(GeoJSONUtils.create_point_feature(lat, lon, point_properties))
        
        # Create LineString feature for the track
        track_properties = {
            "type": "storm_track",
            "point_count": len(tracks)
        }
        track_feature = GeoJSONUtils.create_linestring_feature(coordinates, track_properties)
        
        # Combine track and points
        all_features = [track_feature] + point_features
        
        return GeoJSONUtils.create_feature_collection(all_features)
    
    @staticmethod
    def create_forecast_cone_geojson(forecasts: List[Dict]) -> Dict:
        """Create GeoJSON for forecast cone visualization"""
        if not forecasts:
            return GeoJSONUtils.create_feature_collection([])
        
        # Group forecasts by forecast hour
        forecast_groups = {}
        for forecast in forecasts:
            hour = forecast.get('forecast_hour', 0)
            if hour not in forecast_groups:
                forecast_groups[hour] = []
            forecast_groups[hour].append(forecast)
        
        features = []
        
        # Create cone polygons for each forecast hour
        for hour, forecast_points in forecast_groups.items():
            if len(forecast_points) < 3:
                continue
            
            # Sort points to create proper cone shape
            sorted_points = sorted(forecast_points, key=lambda x: x.get('latitude', 0))
            
            # Create cone coordinates (simplified - in reality you'd use proper cone calculation)
            coordinates = []
            for point in sorted_points:
                lat = point.get('latitude', 0)
                lon = point.get('longitude', 0)
                coordinates.append([lon, lat])
            
            # Close the polygon
            if coordinates:
                coordinates.append(coordinates[0])
            
            cone_properties = {
                "type": "forecast_cone",
                "forecast_hour": hour,
                "forecast_time": forecast_points[0].get('forecast_time'),
                "point_count": len(forecast_points)
            }
            
            cone_coords = [coordinates]  # Polygon needs array of coordinate arrays
            cone_feature = GeoJSONUtils.create_polygon_feature(cone_coords, cone_properties)
            features.append(cone_feature)
        
        return GeoJSONUtils.create_feature_collection(features)
    
    @staticmethod
    def create_intensity_chart_data(tracks: List[Dict]) -> Dict:
        """Create data for intensity chart visualization"""
        if not tracks:
            return {"timeline": [], "wind_speed": [], "pressure": []}
        
        # Sort tracks by timestamp
        sorted_tracks = sorted(tracks, key=lambda x: x.get('timestamp', ''))
        
        timeline = []
        wind_speed = []
        pressure = []
        
        for track in sorted_tracks:
            timestamp = track.get('timestamp')
            if timestamp:
                timeline.append(timestamp)
                wind_speed.append(track.get('wind_speed'))
                pressure.append(track.get('pressure'))
        
        return {
            "timeline": timeline,
            "wind_speed": wind_speed,
            "pressure": pressure
        }
    
    @staticmethod
    def create_forecast_intensity_data(forecasts: List[Dict]) -> Dict:
        """Create data for forecast intensity visualization"""
        if not forecasts:
            return {"forecast_hours": [], "wind_speed": [], "pressure": []}
        
        # Sort forecasts by forecast hour
        sorted_forecasts = sorted(forecasts, key=lambda x: x.get('forecast_hour', 0))
        
        forecast_hours = []
        wind_speed = []
        pressure = []
        
        for forecast in sorted_forecasts:
            forecast_hours.append(forecast.get('forecast_hour', 0))
            wind_speed.append(forecast.get('wind_speed'))
            pressure.append(forecast.get('pressure'))
        
        return {
            "forecast_hours": forecast_hours,
            "wind_speed": wind_speed,
            "pressure": pressure
        }

class StormCategoryUtils:
    """Utilities for storm category classification"""
    
    @staticmethod
    def get_category_from_wind_speed(wind_speed: Optional[float]) -> Optional[str]:
        """Get storm category based on wind speed in knots"""
        if wind_speed is None:
            return None
        
        if wind_speed < 34:
            return "TROPICAL_DEPRESSION"
        elif wind_speed < 64:
            return "TROPICAL_STORM"
        elif wind_speed < 83:
            return "CATEGORY_1"
        elif wind_speed < 96:
            return "CATEGORY_2"
        elif wind_speed < 113:
            return "CATEGORY_3"
        elif wind_speed < 135:
            return "CATEGORY_4"
        else:
            return "CATEGORY_5"
    
    @staticmethod
    def get_category_color(category: Optional[str]) -> str:
        """Get color code for storm category"""
        color_map = {
            "TROPICAL_DEPRESSION": "#00BFFF",  # Deep Sky Blue
            "TROPICAL_STORM": "#32CD32",       # Lime Green
            "CATEGORY_1": "#FFFF00",           # Yellow
            "CATEGORY_2": "#FFA500",           # Orange
            "CATEGORY_3": "#FF4500",           # Orange Red
            "CATEGORY_4": "#FF0000",           # Red
            "CATEGORY_5": "#8B0000"            # Dark Red
        }
        return color_map.get(category, "#808080")  # Default to gray
    
    @staticmethod
    def get_category_name(category: Optional[str]) -> str:
        """Get human-readable category name"""
        name_map = {
            "TROPICAL_DEPRESSION": "Tropical Depression",
            "TROPICAL_STORM": "Tropical Storm",
            "CATEGORY_1": "Category 1 Hurricane",
            "CATEGORY_2": "Category 2 Hurricane",
            "CATEGORY_3": "Category 3 Hurricane",
            "CATEGORY_4": "Category 4 Hurricane",
            "CATEGORY_5": "Category 5 Hurricane"
        }
        return name_map.get(category, "Unknown")

class DistanceUtils:
    """Utilities for distance calculations"""
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    @staticmethod
    def find_closest_point(target_lat: float, target_lon: float, points: List[Dict]) -> Optional[Dict]:
        """Find the closest point to target coordinates"""
        if not points:
            return None
        
        closest_point = None
        min_distance = float('inf')
        
        for point in points:
            lat = point.get('latitude', 0)
            lon = point.get('longitude', 0)
            distance = DistanceUtils.calculate_distance(target_lat, target_lon, lat, lon)
            
            if distance < min_distance:
                min_distance = distance
                closest_point = point
        
        if closest_point:
            closest_point['distance_km'] = min_distance
        
        return closest_point

class TimeUtils:
    """Utilities for time-related calculations"""
    
    @staticmethod
    def format_timestamp(timestamp: datetime) -> str:
        """Format timestamp for display"""
        return timestamp.strftime("%Y-%m-%d %H:%M UTC")
    
    @staticmethod
    def get_time_ago(timestamp: datetime) -> str:
        """Get human-readable time ago string"""
        now = datetime.utcnow()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    
    @staticmethod
    def is_recent_data(timestamp: datetime, hours: int = 6) -> bool:
        """Check if data is recent (within specified hours)"""
        now = datetime.utcnow()
        diff = now - timestamp
        return diff.total_seconds() < (hours * 3600)
