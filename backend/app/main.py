from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import asyncio
from contextlib import asynccontextmanager

from .db import create_tables
from .api import simple_storms
from .services.data_sync import sync_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting XWeather Backend API...")
    
    # Create database tables
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    # Get database stats
    try:
        stats = await sync_service.get_database_stats()
        logger.info(f"Database stats: {stats}")
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down XWeather Backend API...")

# Create FastAPI application
app = FastAPI(
    title="XWeather Storm Data API",
    description="API for fetching and visualizing storm data including tracks and forecasts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(simple_storms.router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "XWeather Storm Data API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "storms": "/api/v1/storms",
            "tracks": "/api/v1/tracks",
            "forecasts": "/api/v1/forecasts"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }

# Database management endpoints
@app.get("/api/v1/database/stats")
async def get_database_stats():
    """Get database statistics"""
    try:
        stats = await sync_service.get_database_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get database statistics")

@app.post("/api/v1/database/cleanup")
async def cleanup_old_data(days_to_keep: int = 30):
    """Clean up old data from database"""
    try:
        await sync_service.cleanup_old_data(days_to_keep)
        return {"message": f"Cleaned up data older than {days_to_keep} days"}
    except Exception as e:
        logger.error(f"Error cleaning up data: {e}")
        raise HTTPException(status_code=500, detail="Failed to clean up old data")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Resource not found", "detail": str(exc)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": "An unexpected error occurred"}
    )

# Additional utility endpoints
@app.get("/api/v1/stats")
async def get_api_stats():
    """Get API statistics from database"""
    try:
        stats = await sync_service.get_database_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting API stats: {e}")
        return {
            "total_storms": 0,
            "total_tracks": 0,
            "total_forecasts": 0,
            "last_update": None
        }

@app.get("/api/v1/basins")
async def get_available_basins():
    """Get list of available storm basins"""
    return {
        "basins": [
            {"code": "ATL", "name": "Atlantic"},
            {"code": "EPAC", "name": "Eastern Pacific"},
            {"code": "WPAC", "name": "Western Pacific"},
            {"code": "CPAC", "name": "Central Pacific"},
            {"code": "IO", "name": "Indian Ocean"},
            {"code": "SH", "name": "Southern Hemisphere"}
        ]
    }

@app.get("/api/v1/categories")
async def get_storm_categories():
    """Get list of storm categories"""
    return {
        "categories": [
            {"code": "TROPICAL_DEPRESSION", "name": "Tropical Depression", "wind_range": "0-38 mph"},
            {"code": "TROPICAL_STORM", "name": "Tropical Storm", "wind_range": "39-73 mph"},
            {"code": "CATEGORY_1", "name": "Category 1 Hurricane", "wind_range": "74-95 mph"},
            {"code": "CATEGORY_2", "name": "Category 2 Hurricane", "wind_range": "96-110 mph"},
            {"code": "CATEGORY_3", "name": "Category 3 Hurricane", "wind_range": "111-129 mph"},
            {"code": "CATEGORY_4", "name": "Category 4 Hurricane", "wind_range": "130-156 mph"},
            {"code": "CATEGORY_5", "name": "Category 5 Hurricane", "wind_range": "157+ mph"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
