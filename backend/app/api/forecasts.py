from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..db import get_db
from ..model import ForecastCreate, ForecastResponse
from ..crud import ForecastCRUD, StormCRUD

router = APIRouter(prefix="/forecasts", tags=["forecasts"])

@router.get("/storm/{storm_id}", response_model=List[ForecastResponse])
async def get_forecasts_by_storm(
    storm_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """Get forecasts for a specific storm"""
    # Verify storm exists
    storm = StormCRUD.get_storm(db, storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    forecasts = ForecastCRUD.get_forecasts_by_storm(db, storm_id, skip=skip, limit=limit)
    return forecasts

@router.get("/storm/{storm_id}/latest", response_model=List[ForecastResponse])
async def get_latest_forecasts(
    storm_id: str,
    db: Session = Depends(get_db)
):
    """Get the latest forecast for a storm"""
    # Verify storm exists
    storm = StormCRUD.get_storm(db, storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    forecasts = ForecastCRUD.get_latest_forecasts(db, storm_id)
    return forecasts

@router.get("/storm/{storm_id}/cone")
async def get_forecast_cone(
    storm_id: str,
    db: Session = Depends(get_db)
):
    """Get forecast cone data for visualization"""
    # Verify storm exists
    storm = StormCRUD.get_storm(db, storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    forecasts = ForecastCRUD.get_latest_forecasts(db, storm_id)
    
    if not forecasts:
        return {
            "type": "FeatureCollection",
            "features": []
        }
    
    # Group forecasts by forecast time (simplified cone)
    forecast_groups = {}
    for forecast in forecasts:
        time_key = forecast.forecast_time[:10] if forecast.forecast_time else "unknown"  # Group by date
        if time_key not in forecast_groups:
            forecast_groups[time_key] = []
        forecast_groups[time_key].append(forecast)
    
    features = []
    
    # Create cone polygons for each forecast time group
    for time_key, forecast_points in forecast_groups.items():
        if len(forecast_points) < 3:
            continue
        
        # Sort points to create proper cone shape
        sorted_points = sorted(forecast_points, key=lambda x: x.lat or 0)
        
        # Create cone coordinates (simplified - in reality you'd use proper cone calculation)
        coordinates = []
        for point in sorted_points:
            if point.lon is not None and point.lat is not None:
                coordinates.append([point.lon, point.lat])
        
        # Close the polygon
        if coordinates and len(coordinates) > 2:
            coordinates.append(coordinates[0])
            
            cone_properties = {
                "type": "forecast_cone",
                "forecast_time": time_key,
                "storm_id": storm.storm_id,
                "name": storm.name,
                "point_count": len(forecast_points)
            }
            
            cone_coords = [coordinates]  # Polygon needs array of coordinate arrays
            features.append({
                "type": "Feature",
                "properties": cone_properties,
                "geometry": {
                    "type": "Polygon",
                    "coordinates": cone_coords
                }
            })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

@router.get("/storm/{storm_id}/track-forecast")
async def get_track_forecast(
    storm_id: str,
    db: Session = Depends(get_db)
):
    """Get forecast track as GeoJSON LineString for visualization"""
    # Verify storm exists
    storm = StormCRUD.get_storm(db, storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    forecasts = ForecastCRUD.get_latest_forecasts(db, storm_id)
    
    if not forecasts:
        return {
            "type": "FeatureCollection",
            "features": []
        }
    
    # Sort by forecast time
    forecasts.sort(key=lambda x: x.forecast_time or "")
    
    # Create GeoJSON LineString
    coordinates = [[forecast.lon, forecast.lat] for forecast in forecasts if forecast.lon is not None and forecast.lat is not None]
    
    # Add properties for each point
    properties = []
    for forecast in forecasts:
        if forecast.lon is not None and forecast.lat is not None:
            properties.append({
                "forecast_time": forecast.forecast_time,
                "wind_speed": forecast.wind_speed,
                "pressure": forecast.pressure,
                "storm_cat": forecast.storm_cat,
                "storm_type": forecast.storm_type,
                "advisory": forecast.advisory
            })
    
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "storm_id": storm.storm_id,
                    "name": storm.name,
                    "basin": storm.basin,
                    "event": storm.event,
                    "point_properties": properties
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates
                }
            }
        ]
    }

@router.post("/", response_model=ForecastResponse)
async def create_forecast(forecast: ForecastCreate, db: Session = Depends(get_db)):
    """Create a new forecast point"""
    # Verify storm exists
    storm = StormCRUD.get_storm(db, forecast.storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    forecast_data = forecast.dict()
    db_forecast = ForecastCRUD.create_forecast(db, forecast_data)
    return db_forecast

@router.post("/batch", response_model=List[ForecastResponse])
async def create_multiple_forecasts(
    forecasts: List[ForecastCreate],
    db: Session = Depends(get_db)
):
    """Create multiple forecast points at once"""
    if not forecasts:
        raise HTTPException(status_code=400, detail="No forecasts provided")
    
    # Verify all storms exist
    storm_ids = set(forecast.storm_id for forecast in forecasts)
    for storm_id in storm_ids:
        storm = StormCRUD.get_storm(db, storm_id)
        if not storm:
            raise HTTPException(status_code=404, detail=f"Storm with ID {storm_id} not found")
    
    forecasts_data = [forecast.dict() for forecast in forecasts]
    db_forecasts = ForecastCRUD.create_multiple_forecasts(db, forecasts_data)
    return db_forecasts

@router.get("/storm/{storm_id}/intensity-forecast")
async def get_intensity_forecast(
    storm_id: str,
    db: Session = Depends(get_db)
):
    """Get intensity forecast over time"""
    # Verify storm exists
    storm = StormCRUD.get_storm(db, storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    forecasts = ForecastCRUD.get_latest_forecasts(db, storm_id)
    
    # Sort by forecast time
    forecasts.sort(key=lambda x: x.forecast_time or "")
    
    intensity_data = []
    for forecast in forecasts:
        intensity_data.append({
            "forecast_time": forecast.forecast_time,
            "wind_speed": forecast.wind_speed,
            "pressure": forecast.pressure,
            "storm_cat": forecast.storm_cat,
            "storm_type": forecast.storm_type,
            "lat": forecast.lat,
            "lon": forecast.lon
        })
    
    return {
        "storm_id": storm.storm_id,
        "name": storm.name,
        "intensity_forecast": intensity_data
    }

@router.get("/storm/{storm_id}/landfall-probability")
async def get_landfall_probability(
    storm_id: str,
    target_latitude: float = Query(..., description="Target latitude for landfall"),
    target_longitude: float = Query(..., description="Target longitude for landfall"),
    radius_km: float = Query(100, ge=10, le=500, description="Radius in kilometers"),
    db: Session = Depends(get_db)
):
    """Calculate landfall probability for a specific location"""
    # Verify storm exists
    storm = StormCRUD.get_storm(db, storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    forecasts = ForecastCRUD.get_latest_forecasts(db, storm_id)
    
    if not forecasts:
        return {
            "storm_id": storm.storm_id,
            "name": storm.name,
            "target_location": {
                "latitude": target_latitude,
                "longitude": target_longitude
            },
            "radius_km": radius_km,
            "landfall_probability": 0.0,
            "closest_approach": None
        }
    
    # Simple distance calculation (in reality, you'd use more sophisticated methods)
    from ..utils import DistanceUtils
    
    target_point = (target_latitude, target_longitude)
    closest_distance = float('inf')
    closest_forecast = None
    
    for forecast in forecasts:
        if forecast.lat is not None and forecast.lon is not None:
            forecast_point = (forecast.lat, forecast.lon)
            distance = DistanceUtils.calculate_distance(target_latitude, target_longitude, forecast.lat, forecast.lon)
            
            if distance < closest_distance:
                closest_distance = distance
                closest_forecast = forecast
    
    # Calculate probability based on distance (simplified)
    if closest_distance <= radius_km:
        probability = max(0, 1 - (closest_distance / radius_km))
    else:
        probability = 0.0
    
    return {
        "storm_id": storm.storm_id,
        "name": storm.name,
        "target_location": {
            "latitude": target_latitude,
            "longitude": target_longitude
        },
        "radius_km": radius_km,
        "landfall_probability": round(probability, 3),
        "closest_approach": {
            "forecast_time": closest_forecast.forecast_time,
            "latitude": closest_forecast.lat,
            "longitude": closest_forecast.lon,
            "distance_km": round(closest_distance, 2)
        } if closest_forecast else None
    }