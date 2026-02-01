"""
Annotation replacement service.

Replaces bid icon annotations with deployment icon annotations
while preserving exact coordinates and sizing.

Uses PyMuPDF (fitz) for proper annotation creation with valid
appearance streams that render correctly in PDF viewers.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pymupdf

from app.models.annotation import Annotation, AnnotationCoordinates
from app.models.mapping import IconData
from app.services.btx_loader import BTXReferenceLoader
from app.services.mapping_parser import MappingParser

if TYPE_CHECKING:
    from app.services.appearance_extractor import AppearanceExtractor
    from app.services.icon_renderer import IconRenderer

logger = logging.getLogger(__name__)

# Default colors for annotations when no appearance data is available
DEFAULT_FILL_COLOR = (1.0, 0.5, 0.0)  # Orange - visible on most backgrounds
DEFAULT_STROKE_COLOR = (0, 0, 0)  # Black border
DEFAULT_BORDER_WIDTH = 0.5


class AnnotationReplacer:
    """
    Service for replacing bid annotations with deployment annotations.

    This service handles the core conversion logic:
    1. Looks up bid subject in mapping to find deployment subject
    2. Gets deployment icon data from BTX loader
    3. Creates new annotation with preserved coordinates using PyMuPDF
    4. Removes bid annotation from PDF page
    5. Inserts deployment annotation at same position with valid appearance stream
    """

    def __init__(
        self,
        mapping_parser: MappingParser,
        btx_loader: BTXReferenceLoader,
        appearance_extractor: "AppearanceExtractor | None" = None,
        icon_renderer: "IconRenderer | None" = None,
    ):
        """
        Initialize annotation replacer.

        Args:
            mapping_parser: MappingParser instance with loaded mappings
            btx_loader: BTXReferenceLoader instance with loaded icons
            appearance_extractor: Optional AppearanceExtractor for copying visual appearances
            icon_renderer: Optional IconRenderer for rich icon rendering with gear images
        """
        self.mapping_parser = mapping_parser
        self.btx_loader = btx_loader
        self.appearance_extractor = appearance_extractor
        self.icon_renderer = icon_renderer

    def _get_colors_for_annotation(
        self,
        deployment_subject: str,
        icon_data: IconData | None,
    ) -> tuple[tuple[float, float, float], tuple[float, float, float], float]:
        """
        Get fill and stroke colors for an annotation.

        Tries to get colors from:
        1. Appearance extractor (reference PDF)
        2. BTX icon data
        3. Default colors

        Args:
            deployment_subject: Subject name for lookup
            icon_data: Optional BTX icon data

        Returns:
            Tuple of (fill_color, stroke_color, opacity)
        """
        fill_color = DEFAULT_FILL_COLOR
        stroke_color = DEFAULT_STROKE_COLOR
        opacity = 1.0

        # Try appearance extractor first
        if self.appearance_extractor and self.appearance_extractor.has_appearance(deployment_subject):
            appearance_data = self.appearance_extractor.get_appearance_data(deployment_subject)
            if appearance_data:
                if appearance_data.get("fill"):
                    fill_color = appearance_data["fill"]
                if appearance_data.get("stroke"):
                    stroke_color = appearance_data["stroke"]
                if appearance_data.get("opacity") is not None:
                    opacity = appearance_data["opacity"]
                logger.debug(f"Using appearance colors for: {deployment_subject}")
                return fill_color, stroke_color, opacity

        # Try BTX icon data for color hints (if available in future)
        if icon_data and icon_data.metadata:
            # BTX colors would be extracted here if available
            pass

        logger.debug(f"Using default colors for: {deployment_subject}")
        return fill_color, stroke_color, opacity

    def _render_rich_icon(
        self,
        writer,
        deployment_subject: str,
        rect: list[float],
        id_label: str = "j100",
    ):
        """
        Render a rich deployment icon with full visual appearance.

        Uses the IconRenderer to create a PDF appearance stream with
        gear images, brand text, and model text.

        Args:
            writer: PdfWriter to add objects to
            deployment_subject: Deployment subject name
            rect: Annotation rect [x1, y1, x2, y2]
            id_label: ID label for the icon

        Returns:
            IndirectObject reference to appearance stream, or None if can't render
        """
        if not self.icon_renderer:
            return None

        if not self.icon_renderer.can_render(deployment_subject):
            return None

        return self.icon_renderer.render_icon(writer, deployment_subject, rect, id_label)

    def _create_annotation_on_page(
        self,
        page: pymupdf.Page,
        coords: AnnotationCoordinates,
        deployment_subject: str,
        annotation_type: str,
        fill_color: tuple[float, float, float],
        stroke_color: tuple[float, float, float],
        opacity: float = 1.0,
        contents: str = "",
    ) -> pymupdf.Annot | None:
        """
        Create a new annotation on the page using PyMuPDF.

        Args:
            page: PyMuPDF page object
            coords: Annotation coordinates
            deployment_subject: Subject name for the annotation
            annotation_type: Type of annotation (/Circle, /Square, etc.)
            fill_color: RGB fill color (0-1 range)
            stroke_color: RGB stroke color (0-1 range)
            opacity: Annotation opacity (0-1)
            contents: Optional contents text

        Returns:
            Created annotation object, or None if creation failed
        """
        # Create rect from coordinates
        # PyMuPDF uses (x0, y0, x1, y1) format
        x0 = coords.x
        y0 = coords.y
        x1 = coords.x + coords.width
        y1 = coords.y + coords.height

        rect = pymupdf.Rect(x0, y0, x1, y1)

        try:
            # Create annotation based on type
            if annotation_type == "/Circle":
                annot = page.add_circle_annot(rect)
            elif annotation_type == "/Square":
                annot = page.add_rect_annot(rect)
            elif annotation_type in ["/Polygon", "/PolyLine"]:
                # For polygon/polyline, use rect corners as simple polygon
                points = [
                    pymupdf.Point(x0, y0),
                    pymupdf.Point(x1, y0),
                    pymupdf.Point(x1, y1),
                    pymupdf.Point(x0, y1),
                ]
                if annotation_type == "/Polygon":
                    annot = page.add_polygon_annot(points)
                else:
                    annot = page.add_polyline_annot(points)
            else:
                # Default to circle for unknown types
                annot = page.add_circle_annot(rect)
                logger.debug(f"Unknown annotation type {annotation_type}, defaulting to Circle")

            # Set annotation properties
            annot.set_colors(fill=fill_color, stroke=stroke_color)
            annot.set_border(width=DEFAULT_BORDER_WIDTH)
            annot.set_opacity(opacity)

            # Set info dictionary for subject
            info = annot.info
            info["subject"] = deployment_subject
            if contents:
                info["content"] = contents
            annot.set_info(info)

            # CRITICAL: Call update() to generate valid appearance stream
            annot.update()

            logger.debug(
                f"Created annotation: {deployment_subject} at ({coords.x}, {coords.y}) "
                f"type={annotation_type}"
            )

            return annot

        except Exception as e:
            logger.error(f"Failed to create annotation {deployment_subject}: {e}")
            return None

    def replace_annotations(
        self,
        input_pdf: Path,
        output_pdf: Path,
    ) -> tuple[int, int, list[str]]:
        """
        Replace bid annotations with deployment annotations in a PDF.

        Opens the input PDF, iterates through all annotations,
        replaces bid annotations with deployment annotations at the
        same coordinates, and saves to output PDF.

        Args:
            input_pdf: Path to input PDF with bid annotations
            output_pdf: Path to save converted PDF

        Returns:
            Tuple of (converted_count, skipped_count, skipped_subjects)
            - converted_count: Number of annotations successfully replaced
            - skipped_count: Number of annotations skipped
            - skipped_subjects: List of bid subjects that were skipped
        """
        converted_count = 0
        skipped_count = 0
        skipped_subjects: list[str] = []

        if not input_pdf.exists():
            logger.error(f"Input PDF not found: {input_pdf}")
            return 0, 0, []

        # Open PDF with PyMuPDF
        doc = pymupdf.open(input_pdf)

        try:
            for page_num, page in enumerate(doc):
                # Collect annotations to process (can't modify during iteration)
                annotations_to_process: list[dict] = []

                for annot in page.annots():
                    if annot is None:
                        continue

                    # Get annotation info
                    info = annot.info
                    bid_subject = info.get("subject", "")

                    if not bid_subject:
                        logger.debug("Skipping annotation with empty subject")
                        skipped_count += 1
                        skipped_subjects.append("(empty subject)")
                        continue

                    # Look up deployment subject
                    deployment_subject = self.mapping_parser.get_deployment_subject(bid_subject)
                    if not deployment_subject:
                        logger.info(f"No mapping found for bid subject: {bid_subject}")
                        skipped_count += 1
                        skipped_subjects.append(bid_subject)
                        continue

                    # Get annotation details before deleting
                    rect = annot.rect
                    annot_type = self._get_annotation_type(annot)
                    contents = info.get("content", "")
                    # Store xref for later deletion (more reliable than annot reference)
                    annot_xref = annot.xref

                    # Store info for later creation
                    annotations_to_process.append({
                        "xref": annot_xref,
                        "bid_subject": bid_subject,
                        "deployment_subject": deployment_subject,
                        "rect": rect,
                        "type": annot_type,
                        "contents": contents,
                        "page_num": page_num,
                    })

                # Process collected annotations (delete old, create new)
                for annot_info in annotations_to_process:
                    try:
                        # Get colors for deployment annotation
                        icon_data = self.btx_loader.get_icon_data(
                            annot_info["deployment_subject"], "deployment"
                        )
                        fill_color, stroke_color, opacity = self._get_colors_for_annotation(
                            annot_info["deployment_subject"], icon_data
                        )

                        # Find and delete original annotation by xref
                        annot_to_delete = None
                        for annot in page.annots():
                            if annot and annot.xref == annot_info["xref"]:
                                annot_to_delete = annot
                                break
                        if annot_to_delete:
                            page.delete_annot(annot_to_delete)

                        # Create coordinates object
                        rect = annot_info["rect"]
                        coords = AnnotationCoordinates(
                            x=rect.x0,
                            y=rect.y0,
                            width=rect.width,
                            height=rect.height,
                            page=page_num + 1,
                        )

                        # Create new deployment annotation
                        new_annot = self._create_annotation_on_page(
                            page=page,
                            coords=coords,
                            deployment_subject=annot_info["deployment_subject"],
                            annotation_type=annot_info["type"],
                            fill_color=fill_color,
                            stroke_color=stroke_color,
                            opacity=opacity,
                            contents=annot_info["contents"],
                        )

                        if new_annot:
                            converted_count += 1
                            logger.debug(
                                f"Converted: {annot_info['bid_subject']} -> "
                                f"{annot_info['deployment_subject']}"
                            )
                        else:
                            skipped_count += 1
                            skipped_subjects.append(annot_info["bid_subject"])

                    except Exception as e:
                        logger.error(
                            f"Error converting annotation {annot_info['bid_subject']}: {e}"
                        )
                        skipped_count += 1
                        skipped_subjects.append(annot_info["bid_subject"])

            # Save the modified PDF
            doc.save(output_pdf)
            logger.info(
                f"Saved converted PDF to {output_pdf}: "
                f"{converted_count} converted, {skipped_count} skipped"
            )

        finally:
            doc.close()

        logger.info(
            f"Annotation replacement complete: "
            f"{converted_count} converted, {skipped_count} skipped"
        )

        return converted_count, skipped_count, skipped_subjects

    def _get_annotation_type(self, annot: pymupdf.Annot) -> str:
        """
        Get the annotation type in PDF format (e.g., /Circle, /Square).

        Args:
            annot: PyMuPDF annotation object

        Returns:
            PDF annotation type string
        """
        # PyMuPDF annotation types are integers
        # Map to PDF type names
        type_map = {
            pymupdf.PDF_ANNOT_CIRCLE: "/Circle",
            pymupdf.PDF_ANNOT_SQUARE: "/Square",
            pymupdf.PDF_ANNOT_POLYGON: "/Polygon",
            pymupdf.PDF_ANNOT_POLY_LINE: "/PolyLine",
            pymupdf.PDF_ANNOT_STAMP: "/Stamp",
            pymupdf.PDF_ANNOT_TEXT: "/Text",
        }
        return type_map.get(annot.type[0], "/Circle")

    # Legacy method for backward compatibility with old API
    def replace_annotations_legacy(
        self,
        annotations: list[Annotation],
        page_dict: dict,
        writer=None,
    ) -> tuple[int, int, list[str]]:
        """
        Legacy method for backward compatibility.

        This method is deprecated. Use replace_annotations() with file paths instead.

        Args:
            annotations: List of bid annotations from PDFAnnotationParser
            page_dict: PDF page dictionary object
            writer: Optional PdfWriter (ignored)

        Returns:
            Tuple of (converted_count, skipped_count, skipped_subjects)
        """
        logger.warning(
            "replace_annotations_legacy is deprecated. "
            "Use replace_annotations(input_pdf, output_pdf) instead."
        )
        # This method cannot work properly without file paths
        # Return zeros to indicate no processing
        return 0, 0, []

    def create_deployment_annotation(
        self,
        bid_annotation: Annotation,
        deployment_subject: str,
        icon_data: IconData | None = None,
        writer=None,
    ) -> dict:
        """
        Create deployment annotation data from bid annotation.

        This is a simplified version that returns annotation metadata.
        The actual annotation creation happens in _create_annotation_on_page()
        when using the new file-based API.

        Args:
            bid_annotation: Original bid annotation with coordinates
            deployment_subject: Deployment icon subject name
            icon_data: Optional icon data from BTX
            writer: Ignored (legacy parameter)

        Returns:
            Dictionary with annotation metadata
        """
        coords = bid_annotation.coordinates

        return {
            "subject": deployment_subject,
            "x": coords.x,
            "y": coords.y,
            "width": coords.width,
            "height": coords.height,
            "type": bid_annotation.annotation_type or "/Circle",
        }
