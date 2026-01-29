"""
FastAPI application entry point for Bluebeam PDF Map Converter.

This module initializes the FastAPI application, configures CORS,
registers API routers, and sets up the health check endpoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers (to be implemented)
# from app.routers import upload, convert, download

app = FastAPI(
    title="Bluebeam PDF Map Converter",
    description="Convert PDF venue maps from bid icons to deployment icons",
    version="1.0.0",
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers (to be uncommented when implemented)
# app.include_router(upload.router, prefix="/api", tags=["upload"])
# app.include_router(convert.router, prefix="/api", tags=["convert"])
# app.include_router(download.router, prefix="/api", tags=["download"])


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns service status and mapping configuration status.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "mapping_loaded": False,  # TODO: Check if mapping.md is loaded
        "mapping_count": 0,
        "toolchest_bid_icons": 0,
        "toolchest_deployment_icons": 0,
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Bluebeam PDF Map Converter API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
