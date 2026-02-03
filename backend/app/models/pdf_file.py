"""PDF file data models."""

from pydantic import BaseModel
from uuid import UUID


class PDFFile(BaseModel):
    """Represents an uploaded PDF file."""

    upload_id: UUID
    file_name: str
    file_size: int
    file_path: str
    page_count: int
    annotation_count: int
    status: str  # "uploaded", "processing", "converted", "failed"


class PDFUploadResponse(BaseModel):
    """Response model for PDF upload endpoint."""

    upload_id: str
    file_name: str
    file_size: int
    status: str
    page_count: int
    annotation_count: int
    message: str


class ConversionRequest(BaseModel):
    """Request model for PDF conversion endpoint."""

    direction: str  # "bid_to_deployment" or "deployment_to_bid"
    output_filename: str | None = None  # Custom output filename (without .pdf extension)


class ConversionResponse(BaseModel):
    """Response model for PDF conversion endpoint."""

    upload_id: str
    file_id: str
    status: str
    original_file: str
    converted_file: str
    direction: str
    annotations_processed: int
    annotations_converted: int
    annotations_skipped: int
    skipped_subjects: list[str]
    processing_time_ms: int
    download_url: str
    message: str
