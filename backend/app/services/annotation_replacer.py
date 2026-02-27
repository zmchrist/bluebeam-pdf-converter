"""
Annotation replacement service.

Replaces bid icon annotations with deployment icon annotations
while preserving exact coordinates and sizing.

Uses pypdf for rich icon rendering with embedded images,
brand text, and model text.

Supports compound annotation groups (7 linked annotations per icon)
matching Bluebeam's native structure for move-survivable icons.
"""

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    IndirectObject,
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
    from app.services.layer_manager import LayerManager

logger = logging.getLogger(__name__)

# Default colors for annotations when no appearance data is available
DEFAULT_FILL_COLOR = (0.22, 0.34, 0.65)  # Navy blue - matches deployment icons
DEFAULT_STROKE_COLOR = (0.0, 0.0, 0.0)  # Black border
DEFAULT_BORDER_WIDTH = 0.5

# Only these annotation subtypes represent bid icons eligible for conversion.
# /Popup annotations share the same /Subj as their parent /Circle but must be
# skipped — converting them produces a smaller duplicate icon.
CONVERTIBLE_SUBTYPES = {"/Circle", "/Square"}

# Standard deployment icon rect size (PDF points).
# Used only for fallback single-annotation mode when compound rendering
# is unavailable. Compound icons compute their own per-component rects.
STANDARD_ICON_SIZE = 14.6


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
        layer_manager: "LayerManager | None" = None,
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
        self.layer_manager = layer_manager
        self.id_assigner = IconIdAssigner()
        self._sequence_counter = 0
        self._sequence_iid = ""

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
        # Zero-origin local coordinates so appearance survives annotation moves
        cx = width / 2
        cy = height / 2
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
            # Draw rectangle in local coordinates
            content_parts.append(f"0.000 0.000 {width:.3f} {height:.3f} re")
            content_parts.append("B")

        content_string = "\n".join(content_parts)
        content_bytes = content_string.encode("latin-1")

        ap_stream = StreamObject()
        ap_stream[NameObject("/Type")] = NameObject("/XObject")
        ap_stream[NameObject("/Subtype")] = NameObject("/Form")
        ap_stream[NameObject("/FormType")] = NumberObject(1)
        ap_stream[NameObject("/BBox")] = ArrayObject([
            FloatObject(0),
            FloatObject(0),
            FloatObject(width),
            FloatObject(height),
        ])
        ap_stream._data = content_bytes

        return writer._add_object(ap_stream)

    def _create_compound_annotation_group(
        self,
        writer: PdfWriter,
        components: list[dict],
        deployment_subject: str,
        ocg_ref=None,
    ) -> list[IndirectObject]:
        """
        Create a compound annotation group (3-7 linked annotations).

        Matches Bluebeam's native compound icon structure:
        - Root annotation (first component, no /IRT)
        - Child annotations (remaining, with /IRT → root)
        - All share /GroupNesting, /Subj, /OC, timestamps

        Args:
            writer: PdfWriter to register objects with
            components: List of component dicts from render_compound_icon()
            deployment_subject: Deployment subject name
            ocg_ref: Optional OCG layer reference

        Returns:
            List of IndirectObject refs (all must be appended to page /Annots)
        """
        # Generate unique /NM for each component
        nms = [uuid.uuid4().hex[:16].upper() for _ in components]

        # Build /GroupNesting array: [subject, /NM1, /NM2, ..., /NMn]
        group_nesting = ArrayObject()
        group_nesting.append(TextStringObject(deployment_subject))
        for nm in nms:
            group_nesting.append(TextStringObject(f"/{nm}"))

        # Shared timestamp
        now = datetime.now(timezone.utc).strftime("D:%Y%m%d%H%M%S+00'00'")

        refs: list[IndirectObject] = []
        root_ref: IndirectObject | None = None

        for i, component in enumerate(components):
            annot = DictionaryObject()
            annot[NameObject("/Type")] = NameObject("/Annot")
            annot[NameObject("/Subtype")] = NameObject(component["subtype"])

            rect = component["rect"]
            annot[NameObject("/Rect")] = ArrayObject([
                FloatObject(rect[0]), FloatObject(rect[1]),
                FloatObject(rect[2]), FloatObject(rect[3]),
            ])

            # Shared properties across all components
            annot[NameObject("/Subj")] = TextStringObject(deployment_subject)
            annot[NameObject("/F")] = NumberObject(4)
            annot[NameObject("/NM")] = TextStringObject(nms[i])
            annot[NameObject("/M")] = TextStringObject(now)
            annot[NameObject("/CreationDate")] = TextStringObject(now)
            annot[NameObject("/T")] = TextStringObject("PDF Converter")
            annot[NameObject("/GroupNesting")] = group_nesting

            if ocg_ref is not None:
                annot[NameObject("/OC")] = ocg_ref

            # Appearance stream
            ap = DictionaryObject()
            ap[NameObject("/N")] = component["ap_ref"]
            annot[NameObject("/AP")] = ap

            # Apply per-component extra properties
            extra = component.get("extra_props", {})
            if "/DA" in extra:
                annot[NameObject("/DA")] = TextStringObject(extra["/DA"])
            if "/Contents" in extra:
                annot[NameObject("/Contents")] = TextStringObject(extra["/Contents"])
            if "/IC" in extra:
                annot[NameObject("/IC")] = ArrayObject(
                    [FloatObject(v) for v in extra["/IC"]]
                )
            if "/C" in extra:
                annot[NameObject("/C")] = ArrayObject(
                    [FloatObject(v) for v in extra["/C"]]
                )
            if "/BS" in extra:
                bs = DictionaryObject()
                bs[NameObject("/W")] = FloatObject(extra["/BS"].get("W", 0))
                bs[NameObject("/S")] = NameObject("/S")
                annot[NameObject("/BS")] = bs
            if "/RD" in extra:
                rd_val = extra["/RD"]
                annot[NameObject("/RD")] = ArrayObject([
                    FloatObject(rd_val), FloatObject(rd_val),
                    FloatObject(rd_val), FloatObject(rd_val),
                ])

            if i == 0:
                # Root annotation — /Sequence, NO /IRT
                annot[NameObject("/Sequence")] = DictionaryObject({
                    NameObject("/IID"): TextStringObject(self._sequence_iid),
                    NameObject("/Index"): NumberObject(self._sequence_counter),
                })
                self._sequence_counter += 1

                ref = writer._add_object(annot)
                root_ref = ref
            else:
                # Child annotation — /IRT points to root
                annot[NameObject("/IRT")] = root_ref
                ref = writer._add_object(annot)

            refs.append(ref)

        return refs

    def _create_deployment_annotation_dict(
        self,
        rect: list[float],
        deployment_subject: str,
        appearance_ref,
        fill_color: tuple[float, float, float],
        stroke_color: tuple[float, float, float],
        annotation_type: str = "/Circle",
        ocg_ref=None,
    ) -> DictionaryObject:
        """
        Create a single deployment annotation (fallback when compound is unavailable).

        Args:
            rect: Annotation rect [x1, y1, x2, y2]
            deployment_subject: Deployment subject name
            appearance_ref: Reference to appearance stream
            fill_color: RGB fill color
            stroke_color: RGB stroke color
            annotation_type: Type of annotation
            ocg_ref: Optional OCG layer reference

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

        if ocg_ref is not None:
            annot[NameObject("/OC")] = ocg_ref

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

        bs = DictionaryObject()
        bs[NameObject("/W")] = FloatObject(DEFAULT_BORDER_WIDTH)
        bs[NameObject("/S")] = NameObject("/S")
        annot[NameObject("/BS")] = bs

        annot[NameObject("/NM")] = TextStringObject(uuid.uuid4().hex[:16].upper())

        now = datetime.now(timezone.utc).strftime("D:%Y%m%d%H%M%S+00'00'")
        annot[NameObject("/M")] = TextStringObject(now)
        annot[NameObject("/CreationDate")] = TextStringObject(now)

        annot[NameObject("/T")] = TextStringObject("PDF Converter")

        rd_inset = DEFAULT_BORDER_WIDTH / 2
        annot[NameObject("/RD")] = ArrayObject([
            FloatObject(rd_inset), FloatObject(rd_inset),
            FloatObject(rd_inset), FloatObject(rd_inset),
        ])

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

        Uses a single-pass array rebuild per page to avoid index management
        bugs and prevent duplicate annotations from /Popup conversion.

        Args:
            input_pdf: Path to input PDF with bid annotations
            output_pdf: Path to save converted PDF

        Returns:
            Tuple of (converted_count, skipped_count, skipped_subjects)
        """
        converted_count = 0
        skipped_count = 0
        skipped_subjects: list[str] = []

        # Reset counters for new conversion
        self.id_assigner.reset()
        self._sequence_counter = 0
        self._sequence_iid = uuid.uuid4().hex[:16].upper()

        if not input_pdf.exists():
            logger.error(f"Input PDF not found: {input_pdf}")
            return 0, 0, []

        # Open PDF with pypdf
        reader = PdfReader(str(input_pdf))
        writer = PdfWriter()

        # Copy all pages to writer
        for page in reader.pages:
            writer.add_page(page)

        # Apply layer structure from reference PDF (if available)
        if self.layer_manager:
            self.layer_manager.apply_to_writer(writer)

        # Process each page — single-pass array rebuild
        for page_num, page in enumerate(writer.pages):
            annots_ref = page.get("/Annots")
            if not annots_ref:
                continue

            annots = annots_ref.get_object() if hasattr(annots_ref, 'get_object') else annots_ref
            if not annots:
                continue

            new_annots = ArrayObject()
            deleted_count = 0

            for idx, annot_ref in enumerate(annots):
                try:
                    annot = annot_ref.get_object() if hasattr(annot_ref, 'get_object') else annot_ref
                    bid_subject = str(annot.get("/Subj", ""))
                    annot_subtype = str(annot.get("/Subtype", ""))

                    # --- SKIP: legend and gear list annotations (don't append) ---
                    if bid_subject and ("Legend" in bid_subject or "CLAIR GEAR LIST" in bid_subject):
                        logger.debug(f"Deleting: {bid_subject}")
                        deleted_count += 1
                        continue

                    # --- PRESERVE: annotations without a subject ---
                    if not bid_subject:
                        new_annots.append(annot_ref)
                        continue

                    # --- Check mapping early: needed for both IRT drop and conversion ---
                    deployment_subject = self.mapping_parser.get_deployment_subject(bid_subject)

                    # --- DROP: child component of a compound Bluebeam bid icon ---
                    # Bluebeam creates compound icons (Circle+Square, Circle+FreeText)
                    # linked via /IRT (In Reply To). All children with a valid bid mapping
                    # are visual sub-elements and must be removed regardless of subtype.
                    if annot.get("/IRT") is not None and deployment_subject:
                        logger.debug(f"Dropping IRT child annotation: {annot_subtype} {bid_subject}")
                        continue

                    # --- PRESERVE: non-convertible subtypes (e.g. /Popup, /Line, /FreeText) ---
                    if annot_subtype not in CONVERTIBLE_SUBTYPES:
                        logger.debug(f"Preserving {annot_subtype} annotation: {bid_subject}")
                        new_annots.append(annot_ref)
                        continue

                    # --- SKIP (preserve): no mapping for this bid subject ---
                    if not deployment_subject:
                        logger.debug(f"No mapping found for bid subject: {bid_subject}")
                        skipped_count += 1
                        skipped_subjects.append(bid_subject)
                        new_annots.append(annot_ref)
                        continue

                    # --- CONVERT: root convertible annotation with valid mapping ---
                    rect_obj = annot.get("/Rect", [])
                    raw_rect = [float(r) for r in rect_obj] if rect_obj else None
                    if not raw_rect or len(raw_rect) != 4:
                        logger.warning(f"Invalid rect for annotation: {bid_subject}")
                        skipped_count += 1
                        skipped_subjects.append(bid_subject)
                        new_annots.append(annot_ref)
                        continue

                    # Center position of the original bid annotation
                    cx = (raw_rect[0] + raw_rect[2]) / 2
                    cy = (raw_rect[1] + raw_rect[3]) / 2

                    # Get dynamic ID for this device
                    id_label = self.id_assigner.get_next_id(deployment_subject) or ""

                    # Look up OCG layer reference for this deployment subject
                    ocg_ref = self.layer_manager.get_ocg_ref(deployment_subject) if self.layer_manager else None

                    # Try compound annotation group (Bluebeam-native structure)
                    components = None
                    if self.icon_renderer:
                        components = self.icon_renderer.render_compound_icon(
                            writer, deployment_subject, (cx, cy), id_label=id_label
                        )

                    if components:
                        # Compound group: 3-7 linked annotations
                        annot_refs = self._create_compound_annotation_group(
                            writer, components, deployment_subject, ocg_ref=ocg_ref
                        )
                        new_annots.extend(annot_refs)
                        converted_count += 1
                        logger.debug(
                            f"Converted (compound {len(annot_refs)}): "
                            f"{bid_subject} -> {deployment_subject}"
                        )
                    else:
                        # Fallback: single annotation (no icon config or no renderer)
                        half = STANDARD_ICON_SIZE / 2
                        rect = [cx - half, cy - half, cx + half, cy + half]

                        icon_data = self.btx_loader.get_icon_data(
                            deployment_subject, "deployment"
                        )
                        fill_color, stroke_color, _ = self._get_colors_for_annotation(
                            deployment_subject, icon_data
                        )

                        appearance_ref = self._render_rich_icon(
                            writer, deployment_subject, rect, id_label=id_label
                        )
                        if appearance_ref is None:
                            appearance_ref = self._create_simple_appearance(
                                writer, rect, fill_color, stroke_color, annot_subtype
                            )

                        new_annot = self._create_deployment_annotation_dict(
                            rect=rect,
                            deployment_subject=deployment_subject,
                            appearance_ref=appearance_ref,
                            fill_color=fill_color,
                            stroke_color=stroke_color,
                            annotation_type=annot_subtype,
                            ocg_ref=ocg_ref,
                        )
                        new_annot_ref = writer._add_object(new_annot)
                        new_annots.append(new_annot_ref)
                        converted_count += 1
                        logger.debug(f"Converted (single): {bid_subject} -> {deployment_subject}")

                except Exception as e:
                    logger.error(f"Error processing annotation at index {idx}: {e}")
                    skipped_count += 1
                    skipped_subjects.append(f"(error at index {idx})")
                    # Preserve the original annotation on error
                    new_annots.append(annot_ref)

            # Replace the page's annotation array with the rebuilt one
            page[NameObject("/Annots")] = new_annots

            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} legend annotations on page {page_num + 1}")

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
