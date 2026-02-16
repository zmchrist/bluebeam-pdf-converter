"""
FastAPI application entry point for Bluebeam PDF Map Converter.

This module initializes the FastAPI application, configures CORS,
registers API routers, and sets up the health check endpoint.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import upload, convert, download
from app.config import settings
from app.services.file_manager import file_manager
from app.services.mapping_parser import MappingParser
from app.services.btx_loader import BTXReferenceLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

CLEANUP_INTERVAL_SECONDS = 15 * 60


async def _periodic_cleanup() -> None:
    while True:
        try:
            count = file_manager.cleanup_expired()
            if count > 0:
                logger.info(f"Background cleanup removed {count} expired file(s)")
        except Exception as e:
            logger.error(f"Error during background cleanup: {e}")
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup cleanup
    try:
        count = file_manager.cleanup_expired()
        if count > 0:
            logger.info(f"Startup cleanup removed {count} expired file(s)")
    except Exception as e:
        logger.error(f"Error during startup cleanup: {e}")
    # Start periodic task
    cleanup_task = asyncio.create_task(_periodic_cleanup())
    logger.info("Background file cleanup task started (interval: 15 minutes)")
    yield
    # Shutdown
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Bluebeam PDF Map Converter",
    description="Convert PDF venue maps from bid icons to deployment icons",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(convert.router, prefix="/api", tags=["convert"])
app.include_router(download.router, prefix="/api", tags=["download"])


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns service status and mapping configuration status.
    """
    mapping_loaded = False
    mapping_count = 0
    bid_icon_count = 0
    deployment_icon_count = 0
    error_message = None

    try:
        # Check mapping file
        if settings.mapping_file.exists():
            mapping_parser = MappingParser(settings.mapping_file)
            mapping_parser.load_mappings()
            mapping_loaded = True
            mapping_count = len(mapping_parser.mappings)
        else:
            error_message = "mapping.md file not found"

        # Check BTX toolchest
        if settings.toolchest_dir.exists():
            btx_loader = BTXReferenceLoader(settings.toolchest_dir)
            btx_loader.load_toolchest()
            bid_icon_count = btx_loader.get_bid_icon_count()
            deployment_icon_count = btx_loader.get_deployment_icon_count()

    except Exception as e:
        logger.error(f"Health check error: {e}")
        error_message = str(e)

    status = "healthy" if mapping_loaded and not error_message else "unhealthy"

    response = {
        "status": status,
        "version": settings.version,
        "timestamp": datetime.now().isoformat(),
        "mapping_loaded": mapping_loaded,
        "mapping_count": mapping_count,
        "toolchest_bid_icons": bid_icon_count,
        "toolchest_deployment_icons": deployment_icon_count,
    }

    if error_message:
        response["error"] = error_message

    return response


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Bluebeam PDF Map Converter API",
        "version": settings.version,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
