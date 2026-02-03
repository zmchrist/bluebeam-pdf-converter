"""
PDF conversion endpoint.

Handles PDF annotation conversion from bid to deployment icons.
"""

import logging
import time

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
        logger.info(f"Loaded {len(mapping_parser.mappings)} mappings")

        # 4. Load BTX reference data
        btx_loader = BTXReferenceLoader(settings.toolchest_dir)
        btx_loader.load_toolchest()
        logger.info(
            f"Loaded BTX: {btx_loader.get_bid_icon_count()} bid, "
            f"{btx_loader.get_deployment_icon_count()} deployment icons"
        )

        # 5. Optional: Load appearance extractor
        appearance_extractor = None
        deployment_map = settings.deployment_map_path
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
        custom_filename = request.output_filename if request else None
        converted_metadata = file_manager.store_converted(
            converted_content,
            upload_metadata.original_name,
            upload_id,
            custom_filename=custom_filename,
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
