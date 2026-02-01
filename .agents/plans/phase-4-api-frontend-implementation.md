# Feature: Phase 4 - Complete API Endpoints & Full Conversion Testing

The following plan should be complete, but it's important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Complete the Bluebeam PDF Map Converter by implementing the FastAPI endpoints (upload, convert, download), testing full BidMap.pdf conversion with the rich icon rendering system, and preparing the application for Phase 4 frontend development. This plan covers the remaining backend work before frontend implementation.

## User Story

As a project estimator
I want to upload a bid map PDF and download a converted deployment map PDF via API
So that I can automate the conversion process without manual icon replacement

## Problem Statement

The backend services (PDF parsing, BTX loading, mapping, annotation replacement, icon rendering) are complete and tested, but the API layer to expose them to clients is not connected. The FastAPI routers exist as skeleton implementations returning 501 errors. Additionally, the full conversion pipeline with rich icons needs end-to-end validation.

## Solution Statement

1. Implement the three FastAPI endpoints (upload, convert, download) using existing services
2. Connect routers to main.py with proper dependency injection
3. Update health check endpoint to validate mapping configuration
4. Run full BidMap.pdf conversion to validate the pipeline
5. Verify converted PDF opens correctly and icons render properly

## Feature Metadata

**Feature Type**: Enhancement (completing existing scaffolding)
**Estimated Complexity**: Medium
**Primary Systems Affected**: API layer, file management, service integration
**Dependencies**: All backend services already implemented (pdf_parser, mapping_parser, btx_loader, annotation_replacer, icon_renderer)

---

## CONTEXT REFERENCES

### Relevant Codebase Files IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

- `backend/app/routers/upload.py` (lines 1-37) - Why: Skeleton endpoint to implement
- `backend/app/routers/convert.py` (lines 1-45) - Why: Skeleton endpoint to implement
- `backend/app/routers/download.py` (lines 1-34) - Why: Skeleton endpoint to implement
- `backend/app/main.py` (lines 1-66) - Why: Must register routers and update health check
- `backend/app/config.py` (lines 1-42) - Why: Settings for file paths, max sizes, retention
- `backend/app/models/pdf_file.py` (lines 1-53) - Why: Pydantic models for request/response
- `backend/app/services/pdf_parser.py` - Why: Service to parse uploaded PDFs
- `backend/app/services/mapping_parser.py` - Why: Service to load mapping configuration
- `backend/app/services/btx_loader.py` - Why: Service to load BTX icon data
- `backend/app/services/annotation_replacer.py` - Why: Main conversion service
- `backend/app/services/appearance_extractor.py` - Why: Optional appearance extraction
- `backend/app/services/icon_renderer.py` - Why: Rich icon rendering
- `backend/scripts/test_conversion.py` - Why: Pattern for running full conversion

### New Files to Create

- `backend/app/services/file_manager.py` - File storage service for uploads/downloads
- `backend/scripts/test_api_endpoints.py` - Manual API testing script

### Relevant Documentation YOU SHOULD READ THESE BEFORE IMPLEMENTING!

- [FastAPI File Uploads](https://fastapi.tiangolo.com/tutorial/request-files/)
  - Specific section: UploadFile handling
  - Why: Required for PDF upload endpoint
- [FastAPI Path Parameters](https://fastapi.tiangolo.com/tutorial/path-params/)
  - Why: For upload_id and file_id parameters
- [FastAPI FileResponse](https://fastapi.tiangolo.com/advanced/custom-response/#fileresponse)
  - Why: For PDF download endpoint

### Patterns to Follow

**Naming Conventions:**
- Services: `snake_case` class names with `CamelCase` (e.g., `MappingParser`, `BTXReferenceLoader`)
- Functions: `snake_case` (e.g., `replace_annotations`, `get_deployment_subject`)
- Models: `CamelCase` with descriptive names (e.g., `PDFUploadResponse`, `ConversionRequest`)
- File paths: Use `Path` objects from pathlib

**Error Handling:**
```python
# Pattern from existing routers
raise HTTPException(status_code=400, detail="User-friendly error message")
raise HTTPException(status_code=404, detail="Resource not found or expired")
raise HTTPException(status_code=500, detail="Internal processing error")
```

**Service Initialization Pattern (from test_conversion.py):**
```python
# Load services
mapping_parser = MappingParser(Path("backend/data/mapping.md"))
mapping_parser.load_mappings()

btx_loader = BTXReferenceLoader()
btx_loader.load_toolchest(bid_tools_dir, deployment_tools_dir)

annotation_replacer = AnnotationReplacer(
    mapping_parser=mapping_parser,
    btx_loader=btx_loader,
    appearance_extractor=appearance_extractor,
    icon_renderer=icon_renderer,
)
```

**File Storage Pattern:**
- UUID-based naming: `{uuid}_{original_filename}`
- Store in `backend/data/temp/`
- Track metadata for retrieval

---

## IMPLEMENTATION PLAN

### Phase 1: File Management Service

Create a centralized service to manage file storage, tracking, and cleanup.

**Tasks:**
- Create `FileManager` service class
- Implement upload storage with UUID generation
- Implement file metadata tracking (in-memory dict for MVP)
- Implement file retrieval by ID
- Add file expiration checking

### Phase 2: Upload Endpoint Implementation

Implement the PDF upload endpoint with validation.

**Tasks:**
- Read uploaded file and validate type
- Validate file size against max_file_size_mb
- Check PDF magic number (%PDF-1)
- Parse PDF to get page count and annotation count
- Validate single-page constraint
- Validate annotations exist
- Store file and return metadata

### Phase 3: Convert Endpoint Implementation

Implement the conversion endpoint using existing services.

**Tasks:**
- Validate upload_id exists
- Validate direction parameter (bid_to_deployment only)
- Load all required services
- Execute annotation replacement
- Generate output file_id
- Track processing time
- Return conversion results

### Phase 4: Download Endpoint Implementation

Implement the file download endpoint.

**Tasks:**
- Validate file_id exists
- Check file hasn't expired
- Return FileResponse with proper headers

### Phase 5: Main App Integration

Connect routers and update health check.

**Tasks:**
- Import and register all routers
- Update health check to validate mapping and BTX
- Add startup event to pre-load services (optional optimization)

### Phase 6: End-to-End Validation

Test the complete pipeline with real data.

**Tasks:**
- Run full BidMap.pdf conversion via API
- Verify output PDF opens correctly
- Check icon rendering quality

---

## STEP-BY-STEP TASKS

IMPORTANT: Execute every task in order, top to bottom. Each task is atomic and independently testable.

### CREATE backend/app/services/file_manager.py

- **IMPLEMENT**: FileManager class with methods for upload storage, retrieval, and cleanup
- **PATTERN**: Use Settings from `backend/app/config.py` for paths
- **IMPORTS**: `from pathlib import Path`, `from uuid import uuid4`, `from datetime import datetime`
- **GOTCHA**: Ensure temp directory exists before writing
- **VALIDATE**: `source .venv/bin/activate && python -c "from app.services.file_manager import FileManager; print('OK')"`

```python
"""
File management service for handling PDF uploads and downloads.

Manages temporary file storage with UUID-based naming and expiration tracking.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from app.config import settings

logger = logging.getLogger(__name__)


class FileMetadata:
    """Metadata for a stored file."""

    def __init__(
        self,
        file_id: str,
        original_name: str,
        file_path: Path,
        created_at: datetime,
        file_size: int,
        file_type: str = "upload",  # "upload" or "converted"
    ):
        self.file_id = file_id
        self.original_name = original_name
        self.file_path = file_path
        self.created_at = created_at
        self.file_size = file_size
        self.file_type = file_type

    def is_expired(self, retention_hours: int) -> bool:
        """Check if file has expired based on retention period."""
        expiry_time = self.created_at + timedelta(hours=retention_hours)
        return datetime.now() > expiry_time


class FileManager:
    """
    Service for managing PDF file storage and retrieval.

    Handles:
    - Storing uploaded PDFs with UUID-based naming
    - Tracking file metadata for retrieval
    - File expiration checking
    - Cleanup of expired files
    """

    def __init__(self, temp_dir: Path | None = None):
        """
        Initialize FileManager.

        Args:
            temp_dir: Directory for temporary file storage. Defaults to settings.temp_dir
        """
        self.temp_dir = temp_dir or settings.temp_dir
        self._files: dict[str, FileMetadata] = {}

        # Ensure temp directory exists
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def store_upload(self, content: bytes, original_name: str) -> FileMetadata:
        """
        Store an uploaded file.

        Args:
            content: File content as bytes
            original_name: Original filename from upload

        Returns:
            FileMetadata with file_id and storage info
        """
        file_id = str(uuid4())
        safe_name = self._sanitize_filename(original_name)
        file_path = self.temp_dir / f"{file_id}_{safe_name}"

        # Write file
        file_path.write_bytes(content)

        # Create and store metadata
        metadata = FileMetadata(
            file_id=file_id,
            original_name=original_name,
            file_path=file_path,
            created_at=datetime.now(),
            file_size=len(content),
            file_type="upload",
        )
        self._files[file_id] = metadata

        logger.info(f"Stored upload: {file_id} -> {file_path}")
        return metadata

    def store_converted(
        self,
        content: bytes,
        original_name: str,
        upload_id: str,
    ) -> FileMetadata:
        """
        Store a converted file.

        Args:
            content: File content as bytes
            original_name: Original filename (will add _deployment suffix)
            upload_id: Related upload ID for tracking

        Returns:
            FileMetadata with file_id and storage info
        """
        file_id = str(uuid4())

        # Create deployment filename
        base_name = Path(original_name).stem
        converted_name = f"{base_name}_deployment.pdf"
        file_path = self.temp_dir / f"{file_id}_{converted_name}"

        # Write file
        file_path.write_bytes(content)

        # Create and store metadata
        metadata = FileMetadata(
            file_id=file_id,
            original_name=converted_name,
            file_path=file_path,
            created_at=datetime.now(),
            file_size=len(content),
            file_type="converted",
        )
        self._files[file_id] = metadata

        logger.info(f"Stored converted: {file_id} -> {file_path}")
        return metadata

    def get_file(self, file_id: str) -> FileMetadata | None:
        """
        Get file metadata by ID.

        Args:
            file_id: UUID of the file

        Returns:
            FileMetadata if found and not expired, None otherwise
        """
        metadata = self._files.get(file_id)
        if metadata is None:
            return None

        # Check expiration
        if metadata.is_expired(settings.file_retention_hours):
            self._cleanup_file(file_id)
            return None

        # Check file still exists
        if not metadata.file_path.exists():
            del self._files[file_id]
            return None

        return metadata

    def get_file_path(self, file_id: str) -> Path | None:
        """
        Get file path by ID.

        Args:
            file_id: UUID of the file

        Returns:
            Path to file if found, None otherwise
        """
        metadata = self.get_file(file_id)
        return metadata.file_path if metadata else None

    def _cleanup_file(self, file_id: str) -> None:
        """Remove a file and its metadata."""
        metadata = self._files.get(file_id)
        if metadata:
            try:
                if metadata.file_path.exists():
                    metadata.file_path.unlink()
                logger.info(f"Cleaned up file: {file_id}")
            except Exception as e:
                logger.error(f"Error cleaning up file {file_id}: {e}")
            finally:
                del self._files[file_id]

    def cleanup_expired(self) -> int:
        """
        Remove all expired files.

        Returns:
            Number of files cleaned up
        """
        expired_ids = [
            file_id
            for file_id, metadata in self._files.items()
            if metadata.is_expired(settings.file_retention_hours)
        ]

        for file_id in expired_ids:
            self._cleanup_file(file_id)

        return len(expired_ids)

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Sanitize filename for safe storage."""
        # Remove path components and keep only filename
        safe_name = Path(name).name
        # Replace problematic characters
        for char in ['/', '\\', '..', '\x00']:
            safe_name = safe_name.replace(char, '_')
        return safe_name


# Global file manager instance (singleton pattern)
file_manager = FileManager()
```

### UPDATE backend/app/routers/upload.py

- **IMPLEMENT**: Complete upload endpoint with PDF validation
- **PATTERN**: Follow error handling pattern from existing routers
- **IMPORTS**: Add `from app.services.file_manager import file_manager`, `from app.services.pdf_parser import PDFAnnotationParser`
- **GOTCHA**: Read file content before parsing; file may be read-once stream
- **VALIDATE**: `source .venv/bin/activate && python -c "from app.routers.upload import router; print('OK')"`

```python
"""
PDF upload endpoint.

Handles PDF file uploads and validation.
"""

import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import settings
from app.models.pdf_file import PDFUploadResponse
from app.services.file_manager import file_manager
from app.services.pdf_parser import PDFAnnotationParser
from app.utils.errors import (
    InvalidPDFError,
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
        except InvalidPDFError as e:
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
```

### UPDATE backend/app/routers/convert.py

- **IMPLEMENT**: Complete conversion endpoint with service orchestration
- **PATTERN**: Mirror service initialization from `backend/scripts/test_conversion.py`
- **IMPORTS**: Add services, file_manager, time module
- **GOTCHA**: Use Path objects consistently; track processing time in milliseconds
- **VALIDATE**: `source .venv/bin/activate && python -c "from app.routers.convert import router; print('OK')"`

```python
"""
PDF conversion endpoint.

Handles PDF annotation conversion from bid to deployment icons.
"""

import logging
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException, Path as PathParam

from app.config import settings
from app.models.pdf_file import ConversionRequest, ConversionResponse
from app.services.file_manager import file_manager
from app.services.mapping_parser import MappingParser
from app.services.btx_loader import BTXReferenceLoader
from app.services.annotation_replacer import AnnotationReplacer
from app.services.appearance_extractor import AppearanceExtractor
from app.services.icon_renderer import IconRenderer
from app.services.icon_config import GEAR_ICONS_DIR

logger = logging.getLogger(__name__)
router = APIRouter()

# Supported conversion directions
SUPPORTED_DIRECTIONS = {"bid_to_deployment"}


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
    start_time = time.time()

    # 1. Validate upload_id exists
    upload_metadata = file_manager.get_file(upload_id)
    if upload_metadata is None:
        raise HTTPException(
            status_code=404,
            detail="Upload session not found or expired.",
        )

    # 2. Validate direction parameter
    direction = "bid_to_deployment"  # Default
    if request and request.direction:
        direction = request.direction

    if direction not in SUPPORTED_DIRECTIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid conversion direction. MVP supports 'bid_to_deployment' only.",
        )

    input_path = upload_metadata.file_path

    try:
        # 3. Load mapping configuration
        mapping_parser = MappingParser(settings.mapping_file)
        mapping_parser.load_mappings()
        logger.info(f"Loaded {len(mapping_parser.mappings.mappings)} mappings")

        # 4. Load BTX reference data
        btx_loader = BTXReferenceLoader()
        btx_loader.load_toolchest(
            settings.bid_tools_dir,
            settings.deployment_tools_dir,
        )
        logger.info(
            f"Loaded BTX: {btx_loader.get_bid_icon_count()} bid, "
            f"{btx_loader.get_deployment_icon_count()} deployment icons"
        )

        # 5. Optional: Load appearance extractor
        appearance_extractor = None
        deployment_map = Path("samples/maps/DeploymentMap.pdf")
        if deployment_map.exists():
            appearance_extractor = AppearanceExtractor()
            appearance_extractor.load_from_pdf(deployment_map)
            logger.info("Loaded appearance data from DeploymentMap.pdf")

        # 6. Initialize icon renderer
        icon_renderer = None
        gear_icons_path = GEAR_ICONS_DIR
        if gear_icons_path.exists():
            icon_renderer = IconRenderer(gear_icons_path)
            logger.info("Initialized icon renderer")

        # 7. Create annotation replacer
        replacer = AnnotationReplacer(
            mapping_parser=mapping_parser,
            btx_loader=btx_loader,
            appearance_extractor=appearance_extractor,
            icon_renderer=icon_renderer,
        )

        # 8. Generate output path
        output_path = settings.temp_dir / f"converted_{upload_id}.pdf"

        # 9. Execute conversion
        converted_count, skipped_count, skipped_subjects = replacer.replace_annotations(
            input_path,
            output_path,
        )

        # 10. Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        # 11. Store converted file
        converted_content = output_path.read_bytes()
        converted_metadata = file_manager.store_converted(
            converted_content,
            upload_metadata.original_name,
            upload_id,
        )

        # Remove temporary output file (we stored it with proper naming)
        if output_path.exists() and output_path != converted_metadata.file_path:
            output_path.unlink()

        logger.info(
            f"Conversion complete: {converted_count} converted, "
            f"{skipped_count} skipped in {processing_time_ms}ms"
        )

        # 12. Return response
        return ConversionResponse(
            upload_id=upload_id,
            file_id=converted_metadata.file_id,
            status="success",
            original_file=upload_metadata.original_name,
            converted_file=converted_metadata.original_name,
            direction=direction,
            annotations_processed=converted_count + skipped_count,
            annotations_converted=converted_count,
            annotations_skipped=skipped_count,
            skipped_subjects=skipped_subjects[:10],  # Limit to first 10
            processing_time_ms=processing_time_ms,
            download_url=f"/api/download/{converted_metadata.file_id}",
            message="Conversion completed successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Conversion failed: {str(e)}",
        )
```

### UPDATE backend/app/routers/download.py

- **IMPLEMENT**: Complete download endpoint with FileResponse
- **PATTERN**: Use FileResponse with media_type and headers
- **IMPORTS**: Add `from app.services.file_manager import file_manager`
- **GOTCHA**: Set Content-Disposition header for proper filename in browser
- **VALIDATE**: `source .venv/bin/activate && python -c "from app.routers.download import router; print('OK')"`

```python
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
```

### UPDATE backend/app/main.py

- **IMPLEMENT**: Register routers and update health check
- **PATTERN**: Use `app.include_router()` with prefix and tags
- **IMPORTS**: Add router imports and service imports for health check
- **GOTCHA**: Validate mapping file exists before loading
- **VALIDATE**: `source .venv/bin/activate && python -c "from app.main import app; print('OK')"`

```python
"""
FastAPI application entry point for Bluebeam PDF Map Converter.

This module initializes the FastAPI application, configures CORS,
registers API routers, and sets up the health check endpoint.
"""

import logging
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import upload, convert, download
from app.config import settings
from app.services.mapping_parser import MappingParser
from app.services.btx_loader import BTXReferenceLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bluebeam PDF Map Converter",
    description="Convert PDF venue maps from bid icons to deployment icons",
    version="1.0.0",
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
            mapping_count = len(mapping_parser.mappings.mappings)
        else:
            error_message = "mapping.md file not found"

        # Check BTX toolchest
        if settings.bid_tools_dir.exists() and settings.deployment_tools_dir.exists():
            btx_loader = BTXReferenceLoader()
            btx_loader.load_toolchest(
                settings.bid_tools_dir,
                settings.deployment_tools_dir,
            )
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
```

### UPDATE backend/app/utils/errors.py

- **IMPLEMENT**: Add any missing exception classes used in upload endpoint
- **PATTERN**: Follow existing error class pattern
- **IMPORTS**: None additional needed
- **VALIDATE**: `source .venv/bin/activate && python -c "from app.utils.errors import InvalidPDFError, MultiPagePDFError, NoAnnotationsFoundError; print('OK')"`

Check if the exceptions exist, and add any missing ones:

```python
"""Custom exception classes for the application."""


class BluebeamConverterError(Exception):
    """Base exception for all application errors."""
    pass


class InvalidPDFError(BluebeamConverterError):
    """Raised when PDF file is invalid or corrupted."""
    pass


class MultiPagePDFError(BluebeamConverterError):
    """Raised when PDF has multiple pages (MVP constraint)."""
    pass


class NoAnnotationsFoundError(BluebeamConverterError):
    """Raised when no markup annotations found in PDF."""
    pass


class MappingNotFoundError(BluebeamConverterError):
    """Raised when mapping configuration cannot be loaded."""
    pass


class BTXLoadError(BluebeamConverterError):
    """Raised when BTX file cannot be loaded or parsed."""
    pass


class ConversionError(BluebeamConverterError):
    """Raised when PDF conversion fails."""
    pass
```

### CREATE backend/tests/test_file_manager.py

- **IMPLEMENT**: Unit tests for FileManager service
- **PATTERN**: Follow existing test patterns from `backend/tests/`
- **IMPORTS**: pytest, tempfile, FileManager
- **VALIDATE**: `source .venv/bin/activate && python -m pytest tests/test_file_manager.py -v`

```python
"""Tests for FileManager service."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from app.services.file_manager import FileManager, FileMetadata


class TestFileMetadata:
    """Tests for FileMetadata class."""

    def test_is_expired_false(self):
        """Test file not expired within retention period."""
        metadata = FileMetadata(
            file_id="test-id",
            original_name="test.pdf",
            file_path=Path("/tmp/test.pdf"),
            created_at=datetime.now(),
            file_size=1000,
        )
        assert not metadata.is_expired(1)  # 1 hour retention

    def test_is_expired_true(self):
        """Test file expired after retention period."""
        metadata = FileMetadata(
            file_id="test-id",
            original_name="test.pdf",
            file_path=Path("/tmp/test.pdf"),
            created_at=datetime.now() - timedelta(hours=2),
            file_size=1000,
        )
        assert metadata.is_expired(1)  # 1 hour retention


class TestFileManager:
    """Tests for FileManager class."""

    def test_store_upload(self):
        """Test storing an uploaded file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(Path(temp_dir))
            content = b"PDF content here"

            metadata = manager.store_upload(content, "test.pdf")

            assert metadata.file_id is not None
            assert metadata.original_name == "test.pdf"
            assert metadata.file_path.exists()
            assert metadata.file_size == len(content)
            assert metadata.file_path.read_bytes() == content

    def test_store_converted(self):
        """Test storing a converted file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(Path(temp_dir))
            content = b"Converted PDF content"

            metadata = manager.store_converted(content, "original.pdf", "upload-123")

            assert metadata.file_id is not None
            assert metadata.original_name == "original_deployment.pdf"
            assert metadata.file_path.exists()
            assert "_deployment.pdf" in str(metadata.file_path)

    def test_get_file_exists(self):
        """Test retrieving an existing file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(Path(temp_dir))
            content = b"PDF content"
            stored = manager.store_upload(content, "test.pdf")

            retrieved = manager.get_file(stored.file_id)

            assert retrieved is not None
            assert retrieved.file_id == stored.file_id

    def test_get_file_not_exists(self):
        """Test retrieving non-existent file returns None."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(Path(temp_dir))

            result = manager.get_file("non-existent-id")

            assert result is None

    def test_get_file_path(self):
        """Test getting file path by ID."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(Path(temp_dir))
            content = b"PDF content"
            stored = manager.store_upload(content, "test.pdf")

            path = manager.get_file_path(stored.file_id)

            assert path is not None
            assert path == stored.file_path

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert FileManager._sanitize_filename("test.pdf") == "test.pdf"
        assert FileManager._sanitize_filename("/path/to/test.pdf") == "test.pdf"
        assert FileManager._sanitize_filename("../test.pdf") == "_.._test.pdf"
```

### ADD tests for API endpoints in backend/tests/test_api.py

- **IMPLEMENT**: Update existing test_api.py with endpoint tests
- **PATTERN**: Use TestClient from fastapi.testclient
- **IMPORTS**: TestClient, tempfile
- **VALIDATE**: `source .venv/bin/activate && python -m pytest tests/test_api.py -v`

Read the existing test_api.py first, then add tests for the new endpoints.

### RUN full test suite

- **VALIDATE**: `source .venv/bin/activate && cd backend && python -m pytest -v --tb=short`

Ensure all 110+ existing tests still pass plus new tests.

---

## TESTING STRATEGY

### Unit Tests

**Scope:** Test each service and component in isolation

- `test_file_manager.py`: FileManager storage, retrieval, expiration
- Update `test_api.py`: Add endpoint tests for upload, convert, download

**Test Patterns:**
- Use `tempfile.TemporaryDirectory()` for file operations
- Use `TestClient` from FastAPI for endpoint tests
- Mock external dependencies where appropriate

### Integration Tests

**Scope:** Test full conversion pipeline via API

1. Upload BidMap.pdf via `/api/upload`
2. Convert via `/api/convert/{upload_id}`
3. Download via `/api/download/{file_id}`
4. Verify downloaded PDF opens correctly

### Edge Cases

- Upload non-PDF file (expect 400)
- Upload PDF without annotations (expect 400)
- Upload multi-page PDF (expect 400)
- Convert with invalid upload_id (expect 404)
- Convert with unsupported direction (expect 400)
- Download with invalid file_id (expect 404)
- Download expired file (expect 404)

---

## VALIDATION COMMANDS

Execute every command to ensure zero regressions and 100% feature correctness.

### Level 1: Syntax & Import Validation

```bash
# Validate all new/modified files import correctly
source .venv/bin/activate
cd backend
python -c "from app.services.file_manager import FileManager; print('FileManager OK')"
python -c "from app.routers.upload import router; print('Upload router OK')"
python -c "from app.routers.convert import router; print('Convert router OK')"
python -c "from app.routers.download import router; print('Download router OK')"
python -c "from app.main import app; print('Main app OK')"
```

### Level 2: Unit Tests

```bash
source .venv/bin/activate
cd backend
python -m pytest tests/test_file_manager.py -v
python -m pytest tests/test_api.py -v
python -m pytest -v --tb=short  # Full suite
```

### Level 3: Integration Tests

```bash
# Start server in background
source .venv/bin/activate
cd backend
python -m uvicorn app.main:app --port 8000 &
SERVER_PID=$!
sleep 3

# Test health endpoint
curl -s http://localhost:8000/health | python -m json.tool

# Test upload (requires BidMap.pdf)
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@../samples/maps/BidMap.pdf" | python -m json.tool

# Stop server
kill $SERVER_PID
```

### Level 4: Manual Validation

1. Start API server: `python -m uvicorn app.main:app --reload`
2. Open Swagger UI: http://localhost:8000/docs
3. Test upload with BidMap.pdf
4. Test conversion with returned upload_id
5. Download converted file and open in PDF viewer
6. Verify icons render correctly

---

## ACCEPTANCE CRITERIA

- [ ] FileManager service stores and retrieves files correctly
- [ ] Upload endpoint validates PDF type, size, structure, annotations
- [ ] Upload endpoint returns proper error codes (400) for invalid inputs
- [ ] Convert endpoint processes bid→deployment correctly
- [ ] Convert endpoint returns proper error codes (404 for missing upload)
- [ ] Download endpoint returns PDF with correct Content-Disposition header
- [ ] Health endpoint validates mapping and BTX configuration
- [ ] All 110+ existing tests continue to pass
- [ ] New FileManager tests pass
- [ ] API endpoint tests pass
- [ ] Full BidMap.pdf conversion produces valid PDF output
- [ ] Converted PDF opens in PDF viewer without errors
- [ ] Icons render with correct visual appearance

---

## COMPLETION CHECKLIST

- [ ] FileManager service created and tested
- [ ] Upload router fully implemented
- [ ] Convert router fully implemented
- [ ] Download router fully implemented
- [ ] Main app registers all routers
- [ ] Health check validates configuration
- [ ] Error classes added to utils/errors.py
- [ ] Unit tests added for FileManager
- [ ] API endpoint tests added
- [ ] All validation commands pass
- [ ] Full test suite passes
- [ ] Manual testing confirms API works
- [ ] BidMap.pdf converts successfully
- [ ] Downloaded PDF renders correctly

---

## NOTES

### Design Decisions

1. **In-memory file tracking**: Using a dict for file metadata tracking. For production, consider using Redis or a database for persistence across restarts.

2. **Singleton FileManager**: Using a global `file_manager` instance for simplicity. This works for single-process deployment but would need adjustment for multi-process scenarios.

3. **Service re-initialization per request**: The convert endpoint reinitializes services (mapping_parser, btx_loader) per request. This ensures fresh data but adds ~100ms overhead. For production, consider caching loaded services.

4. **Limited skipped_subjects**: Returning only first 10 skipped subjects to avoid huge responses. Full list could be logged server-side.

### Performance Considerations

- File manager uses in-memory dict - suitable for MVP, not for production scale
- Services are loaded per-request in convert endpoint - could be cached
- Large PDFs (>20MB) may need streaming upload support

### Security Notes

- Filename sanitization prevents path traversal
- File content validated by magic number
- UUID-based naming prevents filename guessing
- Files auto-expire after 1 hour

### Future Enhancements

- Add background cleanup task for expired files
- Implement persistent file metadata storage
- Add WebSocket for real-time conversion progress
- Support multi-page PDFs
- Add deployment→bid reverse conversion
