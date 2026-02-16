"""
Annotation replacement service.

Replaces bid icon annotations with deployment icon annotations
while preserving exact coordinates and sizing.

Uses pypdf for rich icon rendering with embedded images,
brand text, and model text.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    TextStringObject,
)

from app.models.annotation import Annotation
from app.models.mapping import IconData
from app.services.btx_loader import BTXReferenceLoader
from app.services.icon_config import IconIdAssigner
from app.services.mapping_parser import MappingParser

if TYPE_CHECKING:
    from app.services.appearance_extractor import AppearanceExtractor
    from app.services.icon_renderer import IconRenderer

logger = logging.getLogger(__name__)

# Default colors for annotations when no appearance data is available
DEFAULT_FILL_COLOR = (0.22, 0.34, 0.65)  # Navy blue - matches deployment icons
DEFAULT_STROKE_COLOR = (0.0, 0.0, 0.0)  # Black border
DEFAULT_BORDER_WIDTH = 0.5


class AnnotationReplacer:
    """
    Service for replacing bid annotations with deployment annotations.

    This service handles the core conversion logic:
    1. Looks up bid subject in mapping to find deployment subject
    2. Gets deployment icon data from BTX loader
    3. Creates new annotation with preserved coordinates using pypdf
    4. Removes bid annotation from PDF page
    5. Inserts deployment annotation at same position with rich appearance stream
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
        self.id_assigner = IconIdAssigner()

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
        writer: PdfWriter,
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

    def _create_simple_appearance(
        self,
        writer: PdfWriter,
        rect: list[float],
        fill_color: tuple[float, float, float],
        stroke_color: tuple[float, float, float],
        annotation_type: str,
    ):
        """
        Create a simple appearance stream for annotations without rich rendering.

        Args:
            writer: PdfWriter to add objects to
            rect: Annotation rect [x1, y1, x2, y2]
            fill_color: RGB fill color (0-1 range)
            stroke_color: RGB stroke color (0-1 range)
            annotation_type: Type of annotation (/Circle, /Square, etc.)

        Returns:
            IndirectObject reference to appearance stream
        """
        from pypdf.generic import StreamObject

        x1, y1, x2, y2 = rect
        width = x2 - x1
        height = y2 - y1
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        radius = min(width, height) / 2 - 0.5

        r, g, b = fill_color
        sr, sg, sb = stroke_color

        content_parts = []

        # Set colors
        content_parts.append(f"{sr:.4f} {sg:.4f} {sb:.4f} RG")
        content_parts.append(f"{DEFAULT_BORDER_WIDTH:.4f} w")
        content_parts.append(f"{r:.4f} {g:.4f} {b:.4f} rg")

        if annotation_type == "/Circle":
            # Draw circle using Bezier curves
            k = 0.5522847498
            x0, y0 = cx + radius, cy
            content_parts.append(f"{x0:.3f} {y0:.3f} m")
            content_parts.append(f"{cx + radius:.3f} {cy + radius * k:.3f} {cx + radius * k:.3f} {cy + radius:.3f} {cx:.3f} {cy + radius:.3f} c")
            content_parts.append(f"{cx - radius * k:.3f} {cy + radius:.3f} {cx - radius:.3f} {cy + radius * k:.3f} {cx - radius:.3f} {cy:.3f} c")
            content_parts.append(f"{cx - radius:.3f} {cy - radius * k:.3f} {cx - radius * k:.3f} {cy - radius:.3f} {cx:.3f} {cy - radius:.3f} c")
            content_parts.append(f"{cx + radius * k:.3f} {cy - radius:.3f} {cx + radius:.3f} {cy - radius * k:.3f} {cx + radius:.3f} {cy:.3f} c")
            content_parts.append("h")
            content_parts.append("B")
        else:
            # Draw rectangle
            content_parts.append(f"{x1:.3f} {y1:.3f} {width:.3f} {height:.3f} re")
            content_parts.append("B")

        content_string = "\n".join(content_parts)
        content_bytes = content_string.encode("latin-1")

        ap_stream = StreamObject()
        ap_stream[NameObject("/Type")] = NameObject("/XObject")
        ap_stream[NameObject("/Subtype")] = NameObject("/Form")
        ap_stream[NameObject("/FormType")] = NumberObject(1)
        ap_stream[NameObject("/BBox")] = ArrayObject([
            FloatObject(x1),
            FloatObject(y1),
            FloatObject(x2),
            FloatObject(y2),
        ])
        ap_stream._data = content_bytes

        return writer._add_object(ap_stream)

    def _create_deployment_annotation_dict(
        self,
        rect: list[float],
        deployment_subject: str,
        appearance_ref,
        fill_color: tuple[float, float, float],
        stroke_color: tuple[float, float, float],
        annotation_type: str = "/Circle",
    ) -> DictionaryObject:
        """
        Create a deployment annotation dictionary with appearance stream.

        Args:
            rect: Annotation rect [x1, y1, x2, y2]
            deployment_subject: Deployment subject name
            appearance_ref: Reference to appearance stream
            fill_color: RGB fill color
            stroke_color: RGB stroke color
            annotation_type: Type of annotation

        Returns:
            DictionaryObject for the annotation
        """
        x1, y1, x2, y2 = rect

        annot = DictionaryObject()
        annot[NameObject("/Type")] = NameObject("/Annot")
        annot[NameObject("/Subtype")] = NameObject(annotation_type)
        annot[NameObject("/Rect")] = ArrayObject([
            FloatObject(x1),
            FloatObject(y1),
            FloatObject(x2),
            FloatObject(y2),
        ])
        annot[NameObject("/Subj")] = TextStringObject(deployment_subject)
        annot[NameObject("/F")] = NumberObject(4)  # Print flag

        # Colors (fallback if appearance not used)
        annot[NameObject("/IC")] = ArrayObject([
            FloatObject(fill_color[0]),
            FloatObject(fill_color[1]),
            FloatObject(fill_color[2]),
        ])
        annot[NameObject("/C")] = ArrayObject([
            FloatObject(stroke_color[0]),
            FloatObject(stroke_color[1]),
            FloatObject(stroke_color[2]),
        ])

        # Border style
        bs = DictionaryObject()
        bs[NameObject("/W")] = FloatObject(DEFAULT_BORDER_WIDTH)
        bs[NameObject("/S")] = NameObject("/S")
        annot[NameObject("/BS")] = bs

        # Appearance dictionary - THIS IS THE KEY
        ap = DictionaryObject()
        ap[NameObject("/N")] = appearance_ref
        annot[NameObject("/AP")] = ap

        return annot

    def replace_annotations(
        self,
        input_pdf: Path,
        output_pdf: Path,
    ) -> tuple[int, int, list[str]]:
        """
        Replace bid annotations with deployment annotations in a PDF.

        Uses pypdf for rich icon rendering with embedded images.

        Args:
            input_pdf: Path to input PDF with bid annotations
            output_pdf: Path to save converted PDF

        Returns:
            Tuple of (converted_count, skipped_count, skipped_subjects)
        """
        converted_count = 0
        skipped_count = 0
        skipped_subjects: list[str] = []

        # Reset ID counters for new conversion
        self.id_assigner.reset()

        if not input_pdf.exists():
            logger.error(f"Input PDF not found: {input_pdf}")
            return 0, 0, []

        # Open PDF with pypdf
        reader = PdfReader(str(input_pdf))
        writer = PdfWriter()

        # Copy all pages to writer
        for page in reader.pages:
            writer.add_page(page)

        # Process each page
        for page_num, page in enumerate(writer.pages):
            annots_ref = page.get("/Annots")
            if not annots_ref:
                continue

            annots = annots_ref.get_object() if hasattr(annots_ref, 'get_object') else annots_ref
            if not annots:
                continue

            # Collect annotations to process
            annotations_to_replace: list[dict] = []
            annotations_to_delete: list[int] = []  # Indices of legends to delete

            for idx, annot_ref in enumerate(annots):
                try:
                    annot = annot_ref.get_object() if hasattr(annot_ref, 'get_object') else annot_ref
                    bid_subject = str(annot.get("/Subj", ""))

                    if not bid_subject:
                        logger.debug("Skipping annotation with empty subject")
                        skipped_count += 1
                        skipped_subjects.append("(empty subject)")
                        continue

                    # Delete legend and gear list annotations
                    if "Legend" in bid_subject or "CLAIR GEAR LIST" in bid_subject:
                        logger.debug(f"Marking for deletion: {bid_subject}")
                        annotations_to_delete.append(idx)
                        continue

                    # Preserve line annotations (e.g., P2P link lines) as-is
                    annot_subtype = str(annot.get("/Subtype", ""))
                    if annot_subtype == "/Line":
                        logger.debug(f"Preserving line annotation: {bid_subject}")
                        continue

                    # Look up deployment subject
                    deployment_subject = self.mapping_parser.get_deployment_subject(bid_subject)
                    if not deployment_subject:
                        logger.debug(f"No mapping found for bid subject: {bid_subject}")
                        skipped_count += 1
                        skipped_subjects.append(bid_subject)
                        continue

                    # Get annotation details
                    rect_obj = annot.get("/Rect", [])
                    rect = [float(r) for r in rect_obj] if rect_obj else None
                    if not rect or len(rect) != 4:
                        logger.warning(f"Invalid rect for annotation: {bid_subject}")
                        skipped_count += 1
                        skipped_subjects.append(bid_subject)
                        continue

                    subtype = str(annot.get("/Subtype", "/Circle"))

                    annotations_to_replace.append({
                        "index": idx,
                        "bid_subject": bid_subject,
                        "deployment_subject": deployment_subject,
                        "rect": rect,
                        "subtype": subtype,
                    })

                except Exception as e:
                    logger.error(f"Error reading annotation at index {idx}: {e}")
                    skipped_count += 1
                    skipped_subjects.append(f"(error at index {idx})")

            # Replace annotations (process in reverse order to preserve indices)
            for annot_info in reversed(annotations_to_replace):
                try:
                    deployment_subject = annot_info["deployment_subject"]
                    rect = annot_info["rect"]
                    subtype = annot_info["subtype"]
                    idx = annot_info["index"]

                    # Get colors
                    icon_data = self.btx_loader.get_icon_data(deployment_subject, "deployment")
                    fill_color, stroke_color, _ = self._get_colors_for_annotation(
                        deployment_subject, icon_data
                    )

                    # Get dynamic ID for this device (or empty string if none configured)
                    id_label = self.id_assigner.get_next_id(deployment_subject) or ""

                    # Try rich icon rendering first
                    appearance_ref = self._render_rich_icon(
                        writer, deployment_subject, rect, id_label=id_label
                    )

                    # Fall back to simple appearance if rich rendering not available
                    if appearance_ref is None:
                        appearance_ref = self._create_simple_appearance(
                            writer, rect, fill_color, stroke_color, subtype
                        )

                    # Create new annotation
                    new_annot = self._create_deployment_annotation_dict(
                        rect=rect,
                        deployment_subject=deployment_subject,
                        appearance_ref=appearance_ref,
                        fill_color=fill_color,
                        stroke_color=stroke_color,
                        annotation_type=subtype,
                    )

                    # Replace in annotations array
                    del annots[idx]
                    annots.append(new_annot)

                    converted_count += 1
                    logger.debug(f"Converted: {annot_info['bid_subject']} -> {deployment_subject}")

                except Exception as e:
                    logger.error(f"Error converting annotation {annot_info['bid_subject']}: {e}")
                    skipped_count += 1
                    skipped_subjects.append(annot_info["bid_subject"])

            # Delete legend annotations (in reverse order to preserve indices)
            deleted_count = 0
            for idx in reversed(annotations_to_delete):
                try:
                    del annots[idx]
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting legend at index {idx}: {e}")

            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} legend annotations")

        # Save the output PDF
        with open(output_pdf, "wb") as f:
            writer.write(f)

        logger.info(
            f"Saved converted PDF to {output_pdf}: "
            f"{converted_count} converted, {skipped_count} skipped"
        )

        return converted_count, skipped_count, skipped_subjects

    def _get_annotation_type(self, subtype: str) -> str:
        """
        Normalize annotation type string.

        Args:
            subtype: PDF subtype string

        Returns:
            Normalized type string
        """
        if not subtype.startswith("/"):
            subtype = "/" + subtype
        return subtype

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
        """
        logger.warning(
            "replace_annotations_legacy is deprecated. "
            "Use replace_annotations(input_pdf, output_pdf) instead."
        )
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
