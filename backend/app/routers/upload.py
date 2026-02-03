"""
PDF upload endpoint.

Handles PDF file uploads and validation.
"""

import logging

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import settings
from app.models.pdf_file import PDFUploadResponse
from app.services.file_manager import file_manager
from app.services.pdf_parser import PDFAnnotationParser
from app.utils.errors import (
    InvalidFileTypeError,
    MultiPagePDFError,
    NoAnnotationsFoundError,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# PDF magic number
PDF_MAGIC = b"%PDF"
MAX_FILE_SIZE = settings.max_file_size_mb * 1024 * 1024  # Convert MB to bytes


@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF venue map for conversion.

    Args:
        file: PDF file uploaded by user

    Returns:
        PDFUploadResponse with upload_id and file metadata

    Raises:
        HTTPException 400: Invalid file type, size, or structure
    """
    # 1. Validate file extension
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="File is not a PDF. Please upload a PDF venue map.",
        )

    # 2. Read file content
    content = await file.read()

    # 3. Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"PDF file too large (max {settings.max_file_size_mb}MB). Please reduce file size.",
        )

    # 4. Validate PDF magic number
    if not content.startswith(PDF_MAGIC):
        raise HTTPException(
            status_code=400,
            detail="File is not a valid PDF. Please upload a PDF venue map.",
        )

    # 5. Store file temporarily for parsing
    metadata = file_manager.store_upload(content, file.filename)

    try:
        # 6. Parse PDF to get page count and annotation count
        parser = PDFAnnotationParser()

        # Validate PDF structure
        if not parser.validate_pdf(metadata.file_path):
            raise HTTPException(
                status_code=400,
                detail="File is not a valid PDF. Please upload a PDF venue map.",
            )

        # Get page count
        page_count = parser.get_page_count(metadata.file_path)

        # 7. Validate single-page PDF (MVP constraint)
        if page_count > 1:
            raise HTTPException(
                status_code=400,
                detail="Multi-page PDFs not yet supported. Please upload a single-page venue map.",
            )

        # 8. Parse annotations
        try:
            annotations = parser.parse_pdf(metadata.file_path)
            annotation_count = len(annotations)
        except NoAnnotationsFoundError:
            raise HTTPException(
                status_code=400,
                detail="No icon markup annotations found in PDF. Please verify you uploaded a marked-up bid map.",
            )
        except MultiPagePDFError:
            raise HTTPException(
                status_code=400,
                detail="Multi-page PDFs not yet supported. Please upload a single-page venue map.",
            )
        except InvalidFileTypeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to parse PDF structure. {str(e)}",
            )

        # 9. Validate annotations exist
        if annotation_count == 0:
            raise HTTPException(
                status_code=400,
                detail="No icon markup annotations found in PDF. Please verify you uploaded a marked-up bid map.",
            )

        logger.info(
            f"Upload successful: {file.filename} - {page_count} page(s), "
            f"{annotation_count} annotation(s)"
        )

        # 10. Return response
        return PDFUploadResponse(
            upload_id=metadata.file_id,
            file_name=file.filename,
            file_size=metadata.file_size,
            status="uploaded",
            page_count=page_count,
            annotation_count=annotation_count,
            message="PDF uploaded successfully",
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}",
        )
