from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..db import get_db
from ..model import TrackCreate, TrackResponse
from ..crud import TrackCRUD, StormCRUD

router = APIRouter(prefix="/tracks", tags=["tracks"])

@router.get("/storm/{storm_id}", response_model=List[TrackResponse])
async def get_tracks_by_storm(
    storm_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get tracks for a specific storm"""
    # Verify storm exists
    storm = StormCRUD.get_storm(db, storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    if start_time and end_time:
        tracks = TrackCRUD.get_tracks_in_timeframe(db, storm_id, start_time, end_time)
    else:
        tracks = TrackCRUD.get_tracks_by_storm(db, storm_id, skip=skip, limit=limit)
    
    return tracks

@router.get("/storm/{storm_id}/latest", response_model=TrackResponse)
async def get_latest_track(storm_id: str, db: Session = Depends(get_db)):
    """Get the latest track point for a storm"""
    # Verify storm exists
    storm = StormCRUD.get_storm(db, storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    track = TrackCRUD.get_latest_track(db, storm_id)
    if not track:
        raise HTTPException(status_code=404, detail="No tracks found for this storm")
    
    return track

@router.get("/storm/{storm_id}/recent", response_model=List[TrackResponse])
async def get_recent_tracks(
    storm_id: str,
    hours: int = Query(24, ge=1, le=168),  # Default 24 hours, max 1 week
    db: Session = Depends(get_db)
):
    """Get recent tracks for a storm within specified hours"""
    # Verify storm exists
    storm = StormCRUD.get_storm(db, storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    # Calculate time range
    end_time = datetime.utcnow().isoformat()
    start_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    
    tracks = TrackCRUD.get_tracks_in_timeframe(db, storm_id, start_time, end_time)
    return tracks

@router.post("/", response_model=TrackResponse)
async def create_track(track: TrackCreate, db: Session = Depends(get_db)):
    """Create a new track point"""
    # Verify storm exists
    storm = StormCRUD.get_storm(db, track.storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    track_data = track.dict()
    db_track = TrackCRUD.create_track(db, track_data)
    return db_track

@router.post("/batch", response_model=List[TrackResponse])
async def create_multiple_tracks(
    tracks: List[TrackCreate],
    db: Session = Depends(get_db)
):
    """Create multiple track points at once"""
    if not tracks:
        raise HTTPException(status_code=400, detail="No tracks provided")
    
    # Verify all storms exist
    storm_ids = set(track.storm_id for track in tracks)
    for storm_id in storm_ids:
        storm = StormCRUD.get_storm(db, storm_id)
        if not storm:
            raise HTTPException(status_code=404, detail=f"Storm with ID {storm_id} not found")
    
    tracks_data = [track.dict() for track in tracks]
    db_tracks = TrackCRUD.create_multiple_tracks(db, tracks_data)
    return db_tracks

@router.get("/storm/{storm_id}/path")
async def get_storm_path(
    storm_id: str,
    db: Session = Depends(get_db)
):
    """Get storm path as GeoJSON LineString for visualization"""
    # Verify storm exists
    storm = StormCRUD.get_storm(db, storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    tracks = TrackCRUD.get_tracks_by_storm(db, storm_id, limit=10000)
    
    if not tracks:
        return {
            "type": "FeatureCollection",
            "features": []
        }
    
    # Create GeoJSON LineString
    coordinates = [[track.lon, track.lat] for track in tracks if track.lon is not None and track.lat is not None]
    
    # Add properties for each point
    properties = []
    for track in tracks:
        if track.lon is not None and track.lat is not None:
            properties.append({
                "track_time": track.track_time,
                "wind_speed": track.wind_speed,
                "pressure": track.pressure,
                "storm_cat": track.storm_cat,
                "storm_type": track.storm_type,
                "advisory": track.advisory
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

@router.get("/storm/{storm_id}/current-position")
async def get_current_position(storm_id: str, db: Session = Depends(get_db)):
    """Get current position and status of storm"""
    # Verify storm exists
    storm = StormCRUD.get_storm(db, storm_id)
    if not storm:
        raise HTTPException(status_code=404, detail="Storm not found")
    
    latest_track = TrackCRUD.get_latest_track(db, storm_id)
    if not latest_track:
        raise HTTPException(status_code=404, detail="No track data available")
    
    return {
        "storm_id": storm.storm_id,
        "name": storm.name,
        "event": storm.event,
        "current_position": {
            "latitude": latest_track.lat,
            "longitude": latest_track.lon,
            "track_time": latest_track.track_time,
            "wind_speed": latest_track.wind_speed,
            "pressure": latest_track.pressure,
            "storm_cat": latest_track.storm_cat,
            "storm_type": latest_track.storm_type,
            "advisory": latest_track.advisory
        },
        "storm_info": {
            "basin": storm.basin,
            "event": storm.event,
            "storm_type": storm.storm_type,
            "storm_cat": storm.storm_cat
        }
    }