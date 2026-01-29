"""
PDF download endpoint.

Handles converted PDF file downloads.
"""

from fastapi import APIRouter, HTTPException, Path as PathParam
from fastapi.responses import FileResponse

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
    # TODO: Implement PDF download
    # 1. Validate file_id exists
    # 2. Get file path from temp directory
    # 3. Validate file exists
    # 4. Return FileResponse with PDF
    # 5. Set Content-Disposition header for download
    raise HTTPException(status_code=501, detail="Download endpoint not yet implemented")
