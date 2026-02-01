"""
Annotation replacement service.

Replaces bid icon annotations with deployment icon annotations
while preserving exact coordinates and sizing.
"""

import logging
import re
import zlib
from typing import Any, TYPE_CHECKING

from PyPDF2.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    TextStringObject,
)

from app.models.annotation import Annotation, AnnotationCoordinates
from app.models.mapping import IconData
from app.services.btx_loader import BTXReferenceLoader
from app.services.mapping_parser import MappingParser

if TYPE_CHECKING:
    from app.services.appearance_extractor import AppearanceExtractor

logger = logging.getLogger(__name__)


class AnnotationReplacer:
    """
    Service for replacing bid annotations with deployment annotations.

    This service handles the core conversion logic:
    1. Looks up bid subject in mapping to find deployment subject
    2. Gets deployment icon data from BTX loader
    3. Creates new annotation dictionary with preserved coordinates
    4. Removes bid annotation from PDF page
    5. Inserts deployment annotation at same position
    """

    def __init__(
        self,
        mapping_parser: MappingParser,
        btx_loader: BTXReferenceLoader,
        appearance_extractor: "AppearanceExtractor | None" = None,
    ):
        """
        Initialize annotation replacer.

        Args:
            mapping_parser: MappingParser instance with loaded mappings
            btx_loader: BTXReferenceLoader instance with loaded icons
            appearance_extractor: Optional AppearanceExtractor for copying visual appearances
        """
        self.mapping_parser = mapping_parser
        self.btx_loader = btx_loader
        self.appearance_extractor = appearance_extractor

    def _parse_btx_raw_properties(self, icon_data: IconData) -> dict:
        """
        Parse annotation properties from BTX raw data.

        The BTX raw field contains a PDF dictionary-like string with
        properties like /IC (interior color), /C (border color),
        /Subtype, /BS (border style), etc.

        Args:
            icon_data: IconData with metadata containing raw_hex

        Returns:
            Dictionary of parsed properties
        """
        props = {
            "subtype": "/Circle",  # Default
            "interior_color": None,
            "border_color": None,
            "border_width": 0.5,
            "rect_diff": None,
        }

        if not icon_data.metadata:
            return props
        raw_hex = icon_data.metadata.get("raw_hex", "")
        if not raw_hex:
            return props

        try:
            # Decode the raw hex data
            raw_bytes = bytes.fromhex(raw_hex)
            if raw_hex.lower().startswith("789c"):
                raw_str = zlib.decompress(raw_bytes).decode("utf-8", errors="replace")
            else:
                raw_str = raw_bytes.decode("utf-8", errors="replace")

            # Parse /Subtype
            subtype_match = re.search(r"/Subtype/(\w+)", raw_str)
            if subtype_match:
                props["subtype"] = f"/{subtype_match.group(1)}"

            # Parse /IC (interior color) - format: /IC[r g b]
            ic_match = re.search(r"/IC\[([^\]]+)\]", raw_str)
            if ic_match:
                try:
                    colors = [float(x) for x in ic_match.group(1).split()]
                    if len(colors) >= 3:
                        props["interior_color"] = colors[:3]
                except ValueError:
                    pass

            # Parse /C (border color) - format: /C[r g b]
            c_match = re.search(r"/C\[([^\]]+)\]", raw_str)
            if c_match:
                try:
                    colors = [float(x) for x in c_match.group(1).split()]
                    if len(colors) >= 3:
                        props["border_color"] = colors[:3]
                except ValueError:
                    pass

            # Parse /BS border style - format: /BS<</W 0.5/S/S/Type/Border>>
            bs_w_match = re.search(r"/W\s+([\d.]+)", raw_str)
            if bs_w_match:
                try:
                    props["border_width"] = float(bs_w_match.group(1))
                except ValueError:
                    pass

            # Parse /RD (rect difference) - format: /RD[a b c d]
            rd_match = re.search(r"/RD\[([^\]]+)\]", raw_str)
            if rd_match:
                try:
                    rd_values = [float(x) for x in rd_match.group(1).split()]
                    if len(rd_values) >= 4:
                        props["rect_diff"] = rd_values[:4]
                except ValueError:
                    pass

            logger.debug(f"Parsed BTX properties: {props}")

        except Exception as e:
            logger.warning(f"Failed to parse BTX raw properties: {e}")

        return props

    def create_deployment_annotation(
        self,
        bid_annotation: Annotation,
        deployment_subject: str,
        icon_data: IconData | None = None,
        writer: Any = None,
    ) -> DictionaryObject:
        """
        Create deployment annotation dictionary from bid annotation.

        Preserves exact coordinates and size from bid annotation,
        updates subject to deployment subject, and applies visual
        properties from BTX icon data or reference PDF appearances.

        Args:
            bid_annotation: Original bid annotation with coordinates
            deployment_subject: Deployment icon subject name
            icon_data: Optional icon data from BTX (for visual appearance)
            writer: Optional PdfWriter for cloning indirect objects

        Returns:
            DictionaryObject ready to insert into PDF page
        """
        coords = bid_annotation.coordinates

        # Reconstruct PDF rect format: [x1, y1, x2, y2]
        x1 = coords.x
        y1 = coords.y
        x2 = coords.x + coords.width
        y2 = coords.y + coords.height

        rect = ArrayObject([
            FloatObject(x1),
            FloatObject(y1),
            FloatObject(x2),
            FloatObject(y2),
        ])

        # Check if we have appearance data from reference PDF
        appearance_data = None
        if self.appearance_extractor and self.appearance_extractor.has_appearance(deployment_subject):
            appearance_data = self.appearance_extractor.get_appearance_data(deployment_subject)
            logger.debug(f"Using appearance data from reference PDF for: {deployment_subject}")

        # Parse BTX properties if available (fallback)
        btx_props = {}
        if icon_data and not appearance_data:
            btx_props = self._parse_btx_raw_properties(icon_data)

        # Determine annotation subtype
        if appearance_data:
            subtype = appearance_data.get("subtype", "/Circle")
        else:
            subtype = btx_props.get("subtype", "/Circle")
            if bid_annotation.annotation_type:
                # Prefer matching the original annotation type
                orig_type = bid_annotation.annotation_type
                if orig_type in ["/Circle", "/Square", "/Polygon", "/PolyLine"]:
                    subtype = orig_type

        # Create annotation dictionary
        annot = DictionaryObject()
        annot.update({
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject(subtype),
            NameObject("/Rect"): rect,
            NameObject("/Subj"): TextStringObject(deployment_subject),
            NameObject("/F"): NumberObject(4),  # Print flag
        })

        # Apply appearance data from reference PDF if available
        if appearance_data and writer:
            self._apply_appearance_data(annot, appearance_data, writer)
        else:
            # Fallback to BTX properties or defaults
            self._apply_btx_properties(annot, btx_props, bid_annotation)

        # Copy contents if available from original
        if bid_annotation.raw_data and "/Contents" in bid_annotation.raw_data:
            contents = bid_annotation.raw_data.get("/Contents", "")
            if contents:
                annot[NameObject("/Contents")] = TextStringObject(str(contents))

        logger.debug(
            f"Created deployment annotation: {deployment_subject} "
            f"at ({coords.x}, {coords.y}) with subtype {subtype}"
        )

        return annot

    def _apply_appearance_data(
        self,
        annot: DictionaryObject,
        appearance_data: dict[str, Any],
        writer: Any,
    ) -> None:
        """
        Apply appearance data from reference PDF to annotation.

        Args:
            annot: Annotation dictionary to modify
            appearance_data: Appearance data extracted from reference PDF
            writer: PdfWriter for cloning indirect objects
        """
        try:
            # Clone and apply appearance dictionary
            ap = appearance_data.get("ap")
            if ap and writer:
                # Clone the appearance stream objects to the new PDF
                cloned_ap = writer._add_object(ap)
                annot[NameObject("/AP")] = cloned_ap

            # Apply interior color
            ic = appearance_data.get("ic")
            if ic:
                annot[NameObject("/IC")] = ic

            # Apply border color
            c = appearance_data.get("c")
            if c:
                annot[NameObject("/C")] = c

            # Apply border style
            bs = appearance_data.get("bs")
            if bs:
                annot[NameObject("/BS")] = bs

            # Apply rect difference
            rd = appearance_data.get("rd")
            if rd:
                annot[NameObject("/RD")] = rd

        except Exception as e:
            logger.warning(f"Failed to apply appearance data: {e}")

    def _apply_btx_properties(
        self,
        annot: DictionaryObject,
        btx_props: dict,
        bid_annotation: Annotation,
    ) -> None:
        """
        Apply BTX properties or defaults to annotation.

        Args:
            annot: Annotation dictionary to modify
            btx_props: Properties parsed from BTX data
            bid_annotation: Original bid annotation
        """
        # Apply interior color from BTX or use original
        if btx_props.get("interior_color"):
            ic = btx_props["interior_color"]
            annot[NameObject("/IC")] = ArrayObject([
                FloatObject(ic[0]),
                FloatObject(ic[1]),
                FloatObject(ic[2]),
            ])
        elif bid_annotation.raw_data and "/IC" in bid_annotation.raw_data:
            # Try to preserve original interior color
            try:
                orig_ic = bid_annotation.raw_data["/IC"]
                if isinstance(orig_ic, str) and orig_ic.startswith("["):
                    colors = [float(x) for x in orig_ic.strip("[]").split(",")]
                    if len(colors) >= 3:
                        annot[NameObject("/IC")] = ArrayObject([
                            FloatObject(colors[0]),
                            FloatObject(colors[1]),
                            FloatObject(colors[2]),
                        ])
            except (ValueError, KeyError):
                pass

        # Apply border color from BTX or default to black
        if btx_props.get("border_color"):
            bc = btx_props["border_color"]
            annot[NameObject("/C")] = ArrayObject([
                FloatObject(bc[0]),
                FloatObject(bc[1]),
                FloatObject(bc[2]),
            ])
        else:
            # Default black border
            annot[NameObject("/C")] = ArrayObject([
                FloatObject(0),
                FloatObject(0),
                FloatObject(0),
            ])

        # Apply border style
        border_width = btx_props.get("border_width", 0.5)
        bs = DictionaryObject()
        bs.update({
            NameObject("/W"): FloatObject(border_width),
            NameObject("/S"): NameObject("/S"),  # Solid
            NameObject("/Type"): NameObject("/Border"),
        })
        annot[NameObject("/BS")] = bs

        # Apply rect difference if available (for proper rendering)
        if btx_props.get("rect_diff"):
            rd = btx_props["rect_diff"]
            annot[NameObject("/RD")] = ArrayObject([
                FloatObject(rd[0]),
                FloatObject(rd[1]),
                FloatObject(rd[2]),
                FloatObject(rd[3]),
            ])

    def _find_and_remove_annotation(
        self,
        page: Any,
        target_coords: AnnotationCoordinates,
        target_subject: str,
    ) -> bool:
        """
        Find and remove annotation from page by matching coordinates and subject.

        Args:
            page: PDF page object (from PdfWriter)
            target_coords: Coordinates of annotation to remove
            target_subject: Subject of annotation to remove

        Returns:
            True if annotation was found and removed, False otherwise
        """
        if "/Annots" not in page:
            logger.debug("Page has no /Annots array")
            return False

        annots = page["/Annots"]
        if not annots:
            return False

        # Find annotation by matching rect and subject
        to_remove_idx = None
        for idx, annot_ref in enumerate(annots):
            try:
                annot_obj = annot_ref.get_object()

                # Check subject match
                subj = annot_obj.get("/Subject") or annot_obj.get("/Subj") or ""
                if str(subj) != target_subject:
                    continue

                # Check rect match (approximate due to float precision)
                rect = annot_obj.get("/Rect", [])
                if len(rect) >= 4:
                    x1 = float(rect[0])
                    y1 = float(rect[1])
                    # Match within tolerance
                    if abs(x1 - target_coords.x) < 0.01 and abs(y1 - target_coords.y) < 0.01:
                        to_remove_idx = idx
                        break
            except Exception as e:
                logger.debug(f"Error checking annotation {idx}: {e}")
                continue

        if to_remove_idx is not None:
            del annots[to_remove_idx]
            logger.debug(f"Removed annotation at index {to_remove_idx}: {target_subject}")
            return True

        return False

    def replace_annotations(
        self,
        annotations: list[Annotation],
        page: Any,
        writer: Any = None,
    ) -> tuple[int, int, list[str]]:
        """
        Replace all bid annotations with deployment annotations on a page.

        For each annotation:
        1. Look up bid subject in mapping to find deployment subject
        2. Get deployment icon data from BTX loader
        3. Remove original bid annotation from page
        4. Create and insert deployment annotation at same coordinates

        Args:
            annotations: List of bid annotations from PDFAnnotationParser
            page: PDF page object to modify (from PdfWriter or PdfReader)
            writer: Optional PdfWriter for cloning appearance streams

        Returns:
            Tuple of (converted_count, skipped_count, skipped_subjects)
            - converted_count: Number of annotations successfully replaced
            - skipped_count: Number of annotations skipped
            - skipped_subjects: List of bid subjects that were skipped

        Raises:
            ConversionError: If critical conversion failure occurs
        """
        converted_count = 0
        skipped_count = 0
        skipped_subjects: list[str] = []

        if not annotations:
            logger.warning("No annotations provided for replacement")
            return 0, 0, []

        # Ensure page has /Annots array
        if "/Annots" not in page:
            page[NameObject("/Annots")] = ArrayObject()

        for annotation in annotations:
            bid_subject = annotation.subject

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

            # Get deployment icon data (optional, for visual appearance)
            icon_data = self.btx_loader.get_icon_data(deployment_subject, "deployment")
            if not icon_data and not (self.appearance_extractor and self.appearance_extractor.has_appearance(deployment_subject)):
                logger.warning(
                    f"No BTX icon data or appearance for deployment subject: {deployment_subject}, "
                    f"proceeding with basic replacement"
                )
                # Continue anyway - we can still replace the subject

            try:
                # Remove original bid annotation
                removed = self._find_and_remove_annotation(
                    page,
                    annotation.coordinates,
                    bid_subject,
                )
                if not removed:
                    logger.debug(
                        f"Could not find bid annotation to remove: {bid_subject}"
                    )
                    # Still proceed with adding deployment annotation

                # Create deployment annotation
                new_annot = self.create_deployment_annotation(
                    annotation,
                    deployment_subject,
                    icon_data,
                    writer,
                )

                # Add to page
                page["/Annots"].append(new_annot)

                converted_count += 1
                logger.debug(
                    f"Converted: {bid_subject} -> {deployment_subject}"
                )

            except Exception as e:
                logger.error(f"Error converting annotation {bid_subject}: {e}")
                skipped_count += 1
                skipped_subjects.append(bid_subject)
                continue

        logger.info(
            f"Annotation replacement complete: "
            f"{converted_count} converted, {skipped_count} skipped"
        )

        return converted_count, skipped_count, skipped_subjects
