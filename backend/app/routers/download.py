"""
PDF download endpoint.

Handles converted PDF file downloads.
"""

import logging

from fastapi import APIRouter, HTTPException, Path as PathParam
from fastapi.responses import FileResponse

from app.services.file_manager import file_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/download/{file_id}")
async def download_pdf(file_id: str = PathParam(..., description="Converted file UUID")):
    """
    Download converted PDF file.

    Args:
        file_id: Converted file UUID

    Returns:
        FileResponse with PDF file

    Raises:
        HTTPException 404: File not found or expired
    """
    # 1. Validate file_id exists
    metadata = file_manager.get_file(file_id)
    if metadata is None:
        raise HTTPException(
            status_code=404,
            detail="Converted file not found or expired (files expire after 1 hour).",
        )

    # 2. Verify file exists on disk
    if not metadata.file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Converted file not found or expired (files expire after 1 hour).",
        )

    logger.info(f"Download requested: {file_id} -> {metadata.original_name}")

    # 3. Return FileResponse with PDF
    return FileResponse(
        path=metadata.file_path,
        media_type="application/pdf",
        filename=metadata.original_name,
        headers={
            "Content-Disposition": f'attachment; filename="{metadata.original_name}"'
        },
    )
