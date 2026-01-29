"""
PDF conversion endpoint.

Handles PDF annotation conversion from bid to deployment icons.
"""

from fastapi import APIRouter, HTTPException, Path as PathParam
from app.models.pdf_file import ConversionRequest, ConversionResponse

router = APIRouter()


@router.post("/convert/{upload_id}", response_model=ConversionResponse)
async def convert_pdf(
    upload_id: str = PathParam(..., description="Upload session UUID"),
    request: ConversionRequest = None,
):
    """
    Convert PDF annotations from bid to deployment icons.

    Args:
        upload_id: Upload session UUID
        request: Conversion request with direction parameter

    Returns:
        ConversionResponse with conversion results

    Raises:
        HTTPException 400: Invalid direction parameter
        HTTPException 404: Upload not found or expired
        HTTPException 500: Conversion failed
    """
    # TODO: Implement PDF conversion
    # 1. Validate upload_id exists
    # 2. Validate direction parameter (bid_to_deployment only for MVP)
    # 3. Load uploaded PDF
    # 4. Parse annotations
    # 5. Load mappings and BTX reference data
    # 6. Replace annotations (bid→deployment)
    # 7. Reconstruct PDF
    # 8. Generate file_id for download
    # 9. Track processing time
    # 10. Return ConversionResponse
    raise HTTPException(status_code=501, detail="Convert endpoint not yet implemented")
