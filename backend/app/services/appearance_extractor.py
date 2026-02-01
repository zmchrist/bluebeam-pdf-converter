"""
Appearance stream extractor service.

Extracts annotation color information from reference PDF files
to enable visual appearance matching during conversion.

Uses PyMuPDF for reliable color extraction.
"""

import logging
from pathlib import Path
from typing import Any

import pymupdf

logger = logging.getLogger(__name__)


class AppearanceExtractor:
    """
    Service for extracting annotation appearance data from reference PDFs.

    This extracts color information (fill, stroke, opacity) from annotations
    in a reference PDF (e.g., DeploymentMap.pdf) so the converted annotations
    can match the expected visual appearance.
    """

    def __init__(self):
        """Initialize appearance extractor."""
        self.appearances: dict[str, dict[str, Any]] = {}
        self._loaded = False

    def load_from_pdf(self, pdf_path: Path) -> int:
        """
        Load appearance data from a reference PDF.

        Extracts color information from each annotation and stores it
        keyed by subject name.

        Args:
            pdf_path: Path to reference PDF file

        Returns:
            Number of unique appearances extracted

        Raises:
            FileNotFoundError: If PDF file doesn't exist
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"Reference PDF not found: {pdf_path}")

        self.appearances.clear()

        doc = pymupdf.open(pdf_path)

        try:
            for page_num, page in enumerate(doc):
                self._extract_from_page(page, page_num)
        finally:
            doc.close()

        self._loaded = True
        logger.info(f"Loaded {len(self.appearances)} appearance streams from {pdf_path.name}")

        return len(self.appearances)

    def _extract_from_page(self, page: pymupdf.Page, page_num: int) -> None:
        """
        Extract appearances from a single page.

        Args:
            page: PyMuPDF page object
            page_num: Page number (0-indexed)
        """
        for annot in page.annots():
            if annot is None:
                continue

            try:
                # Get subject
                info = annot.info
                subj_str = info.get("subject", "").strip()

                if not subj_str:
                    continue

                # Skip if we already have this subject (use first occurrence)
                if subj_str in self.appearances:
                    continue

                # Extract colors
                colors = annot.colors
                fill_color = colors.get("fill")
                stroke_color = colors.get("stroke")

                # Get opacity
                opacity = annot.opacity

                # Only store if we have color data
                if fill_color is None and stroke_color is None:
                    continue

                # Convert colors to tuples
                fill_tuple = tuple(fill_color) if fill_color else None
                stroke_tuple = tuple(stroke_color) if stroke_color else None

                # Store the appearance data
                self.appearances[subj_str] = {
                    "fill": fill_tuple,
                    "stroke": stroke_tuple,
                    "opacity": opacity if opacity is not None else 1.0,
                    "subtype": self._get_annotation_subtype(annot),
                    "page_num": page_num,
                }

                logger.debug(
                    f"Extracted appearance for: {subj_str} "
                    f"fill={fill_tuple} stroke={stroke_tuple}"
                )

            except Exception as e:
                logger.debug(f"Error extracting annotation appearance: {e}")
                continue

    def _get_annotation_subtype(self, annot: pymupdf.Annot) -> str:
        """
        Get the annotation subtype in PDF format.

        Args:
            annot: PyMuPDF annotation object

        Returns:
            PDF annotation subtype string (e.g., "/Circle")
        """
        type_map = {
            pymupdf.PDF_ANNOT_CIRCLE: "/Circle",
            pymupdf.PDF_ANNOT_SQUARE: "/Square",
            pymupdf.PDF_ANNOT_POLYGON: "/Polygon",
            pymupdf.PDF_ANNOT_POLY_LINE: "/PolyLine",
            pymupdf.PDF_ANNOT_STAMP: "/Stamp",
            pymupdf.PDF_ANNOT_TEXT: "/Text",
        }
        return type_map.get(annot.type[0], "/Circle")

    def get_appearance_data(self, subject: str) -> dict[str, Any] | None:
        """
        Get appearance data for a given subject.

        Args:
            subject: Annotation subject name

        Returns:
            Dictionary with appearance data:
                - fill: RGB tuple (0-1 range) or None
                - stroke: RGB tuple (0-1 range) or None
                - opacity: Float 0-1
                - subtype: PDF annotation subtype
            Or None if not found
        """
        return self.appearances.get(subject)

    def get_available_subjects(self) -> list[str]:
        """
        Get list of subjects with available appearances.

        Returns:
            Sorted list of subject names
        """
        return sorted(self.appearances.keys())

    def has_appearance(self, subject: str) -> bool:
        """
        Check if appearance is available for subject.

        Args:
            subject: Annotation subject name

        Returns:
            True if appearance data is available
        """
        return subject in self.appearances

    def is_loaded(self) -> bool:
        """
        Check if appearances have been loaded.

        Returns:
            True if load_from_pdf() has been called successfully
        """
        return self._loaded
