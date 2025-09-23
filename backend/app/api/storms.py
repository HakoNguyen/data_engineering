from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..db import get_db
from ..model import StormCreate, StormUpdate, StormResponse, StormWithTracksAndForecasts, StormSummary
from ..crud import StormCRUD, StormAnalytics

router = APIRouter(prefix="/storms", tags=["storms"])

@router.get("/", response_model=List[StormSummary])
async def get_storms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    basin: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of storms with optional filtering"""
    storms = StormCRUD.get_storms(db, skip=skip, limit=limit, basin=basin)
    
    # Convert to summary format
    summaries = []
    for storm in storms:
        summary = StormAnalytics.get_storm_summary(db, storm.storm_id)
        if summary:
            summaries.append(StormSummary(**summary))
    
    return summaries

@router.get("/active", response_model=List[StormSummary])
async def get_active_storms(db: Session = Depends(get_db)):
    """Get all currently active storms"""
    storms = StormCRUD.get_active_storms(db)
    summaries = []
    for storm in storms:
        summary = StormAnalytics.get_storm_summary(db, storm.storm_id)
        if summary:
            summaries.append(StormSummary(**summary))
    return summaries

@router.get("/{storm_id}", response_model=StormWithTracksAndForecasts)
async def get_storm(
    storm_id: str,
    include_tracks: bool = Query(True),
    include_forecasts: bool = Query(True),
    track_limit: int = Query(1000, ge=1, le=10000),
    forecast_limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """Get detailed storm information with tracks and forecasts"""
    storm = StormCRUD.get_storm(db, storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    result = StormWithTracksAndForecasts(
        storm_id=storm.storm_id,
        name=storm.name,
        start_time=storm.start_time,
        basin=storm.basin,
        event=storm.event,
        storm_type=storm.storm_type,
        storm_cat=storm.storm_cat,
        lon=storm.lon,
        lat=storm.lat,
        created_at=storm.created_at,
        updated_at=storm.updated_at,
        tracks=[],
        forecasts=[]
    )
    
    if include_tracks:
        from ..crud import TrackCRUD
        tracks = TrackCRUD.get_tracks_by_storm(db, storm_id, limit=track_limit)
        result.tracks = tracks
    
    if include_forecasts:
        from ..crud import ForecastCRUD
        forecasts = ForecastCRUD.get_forecasts_by_storm(db, storm_id, limit=forecast_limit)
        result.forecasts = forecasts
    
    return result

@router.post("/", response_model=StormResponse)
async def create_storm(storm: StormCreate, db: Session = Depends(get_db)):
    """Create a new storm"""
    # Check if storm_id already exists
    existing_storm = StormCRUD.get_storm(db, storm.storm_id)
    if existing_storm:
        raise HTTPException(status_code=400, detail="Storm with this ID already exists")
    
    storm_data = storm.dict()
    db_storm = StormCRUD.create_storm(db, storm_data)
    return db_storm

@router.put("/{storm_id}", response_model=StormResponse)
async def update_storm(
    storm_id: str,
    storm_update: StormUpdate,
    db: Session = Depends(get_db)
):
    """Update storm information"""
    storm_data = {k: v for k, v in storm_update.dict().items() if v is not None}
    if not storm_data:
        raise HTTPException(status_code=400, detail="No data provided for update")
    
    db_storm = StormCRUD.update_storm(db, storm_id, storm_data)
    if not db_storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    return db_storm

@router.delete("/{storm_id}")
async def delete_storm(storm_id: str, db: Session = Depends(get_db)):
    """Delete a storm and all its tracks and forecasts"""
    db_storm = StormCRUD.delete_storm(db, storm_id)
    if not db_storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    return {"message": "Storm deleted successfully"}

@router.get("/{storm_id}/summary", response_model=StormSummary)
async def get_storm_summary(storm_id: str, db: Session = Depends(get_db)):
    """Get storm summary with statistics"""
    summary = StormAnalytics.get_storm_summary(db, storm_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    return StormSummary(**summary)

@router.get("/{storm_id}/intensity-history")
async def get_storm_intensity_history(storm_id: str, db: Session = Depends(get_db)):
    """Get storm intensity history over time"""
    storm = StormCRUD.get_storm(db, storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    history = StormAnalytics.get_storm_intensity_history(db, storm_id)
    return {
        "storm_id": storm.storm_id,
        "name": storm.name,
        "intensity_history": history
    }

@router.get("/{storm_id}/forecast-intensity")
async def get_forecast_intensity_history(storm_id: str, db: Session = Depends(get_db)):
    """Get forecast intensity history over time"""
    storm = StormCRUD.get_storm(db, storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    history = StormAnalytics.get_forecast_intensity_history(db, storm_id)
    return {
        "storm_id": storm.storm_id,
        "name": storm.name,
        "forecast_intensity_history": history
    }

@router.get("/basin/{basin}", response_model=List[StormSummary])
async def get_storms_by_basin(basin: str, db: Session = Depends(get_db)):
    """Get storms by basin (AL, EP, CP, WP, IO, SH)"""
    storms = StormAnalytics.get_storms_by_basin(db, basin.upper())
    summaries = []
    for storm in storms:
        summary = StormAnalytics.get_storm_summary(db, storm.storm_id)
        if summary:
            summaries.append(StormSummary(**summary))
    return summaries

@router.get("/{storm_id}/geojson")
async def get_storm_geojson(storm_id: str, db: Session = Depends(get_db)):
    """Get storm data in GeoJSON format for visualization"""
    storm = StormCRUD.get_storm(db, storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    from ..crud import TrackCRUD, ForecastCRUD
    from ..utils import StormVisualizationUtils
    
    # Get tracks and forecasts
    tracks = TrackCRUD.get_tracks_by_storm(db, storm_id, limit=10000)
    forecasts = ForecastCRUD.get_forecasts_by_storm(db, storm_id, limit=10000)
    
    # Convert to GeoJSON
    track_geojson = StormVisualizationUtils.create_storm_track_geojson(tracks)
    forecast_geojson = StormVisualizationUtils.create_forecast_cone_geojson(forecasts)
    
    return {
        "storm_info": {
            "storm_id": storm.storm_id,
            "name": storm.name,
            "basin": storm.basin,
            "event": storm.event,
            "storm_type": storm.storm_type,
            "storm_cat": storm.storm_cat,
            "current_position": {
                "lat": storm.lat,
                "lon": storm.lon
            }
        },
        "track_geojson": track_geojson,
        "forecast_geojson": forecast_geojson
    }