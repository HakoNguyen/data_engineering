from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from ..direct_db import db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/storms", tags=["storms"])

@router.get("/")
async def get_storms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    basin: Optional[str] = None
):
    """Get list of storms"""
    try:
        if not db.connection:
            db.connect()
        
        if basin:
            query = "SELECT * FROM storm WHERE basin = %s ORDER BY start_time DESC NULLS LAST LIMIT %s OFFSET %s"
            storms = db.execute_query(query, (basin, limit, skip))
        else:
            query = "SELECT * FROM storm ORDER BY start_time DESC NULLS LAST LIMIT %s OFFSET %s"
            storms = db.execute_query(query, (limit, skip))
        
        return storms
    except Exception as e:
        logger.error(f"Error getting storms: {e}")
        raise HTTPException(status_code=500, detail="Failed to get storms")

@router.get("/active")
async def get_active_storms():
    """Get active storms (storms with recent tracks)"""
    try:
        if not db.connection:
            db.connect()
        
        query = """
        SELECT s.*
        FROM storm s
        WHERE EXISTS (
            SELECT 1 FROM track t WHERE t.storm_id = s.storm_id
        )
        ORDER BY s.start_time DESC NULLS LAST
        """
        storms = db.execute_query(query)
        return storms
    except Exception as e:
        logger.error(f"Error getting active storms: {e}")
        raise HTTPException(status_code=500, detail="Failed to get active storms")

@router.get("/{storm_id}")
async def get_storm(storm_id: str):
    """Get storm details"""
    try:
        if not db.connection:
            db.connect()
        
        storm = db.get_storm_by_id(storm_id)
        if not storm:
            raise HTTPException(status_code=404, detail="Storm not found")
        
        return storm
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting storm {storm_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get storm")

@router.get("/{storm_id}/tracks")
async def get_storm_tracks(
    storm_id: str,
    limit: int = Query(1000, ge=1, le=10000)
):
    """Get tracks for a storm"""
    try:
        if not db.connection:
            db.connect()
        
        tracks = db.get_tracks_by_storm(storm_id, limit)
        return tracks
    except Exception as e:
        logger.error(f"Error getting tracks for storm {storm_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tracks")

@router.get("/{storm_id}/forecasts")
async def get_storm_forecasts(
    storm_id: str,
    limit: int = Query(1000, ge=1, le=10000)
):
    """Get forecasts for a storm"""
    try:
        if not db.connection:
            db.connect()
        
        forecasts = db.get_forecasts_by_storm(storm_id, limit)
        return forecasts
    except Exception as e:
        logger.error(f"Error getting forecasts for storm {storm_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get forecasts")

@router.get("/{storm_id}/geojson")
async def get_storm_geojson(storm_id: str):
    """Get storm data in GeoJSON format"""
    try:
        if not db.connection:
            db.connect()
        
        # Get storm info
        storm = db.get_storm_by_id(storm_id)
        if not storm:
            raise HTTPException(status_code=404, detail="Storm not found")
        
        # Get tracks
        tracks = db.get_tracks_by_storm(storm_id, 10000)
        
        # Create GeoJSON
        coordinates = []
        for track in tracks:
            if track.get('lon') is not None and track.get('lat') is not None:
                coordinates.append([track['lon'], track['lat']])
        
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "storm_id": storm['storm_id'],
                        "name": storm['name'],
                        "basin": storm['basin'],
                        "event": storm['event'],
                        "storm_type": storm['storm_type'],
                        "storm_cat": storm['storm_cat']
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": coordinates
                    }
                }
            ]
        }
        
        return geojson
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting GeoJSON for storm {storm_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get GeoJSON")

@router.post("/create-sample")
async def create_sample_data():
    """Create sample data for testing"""
    try:
        if not db.connection:
            db.connect()
        
        success = db.create_sample_data()
        if success:
            return {"message": "Sample data created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create sample data")
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        raise HTTPException(status_code=500, detail="Failed to create sample data")
