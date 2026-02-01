"""
Appearance stream extractor service.

Extracts annotation appearance streams from reference PDF files
to enable visual appearance copying during conversion.
"""

import logging
from pathlib import Path
from typing import Any

from PyPDF2 import PdfReader
from PyPDF2.generic import (
    ArrayObject,
    DictionaryObject,
    IndirectObject,
    NameObject,
)

logger = logging.getLogger(__name__)


class AppearanceExtractor:
    """
    Service for extracting annotation appearance streams from reference PDFs.

    This allows copying the visual appearance of icons from one PDF
    (e.g., DeploymentMap.pdf) to annotations in another PDF.
    """

    def __init__(self):
        """Initialize appearance extractor."""
        self.appearances: dict[str, dict[str, Any]] = {}
        self._reader: PdfReader | None = None
        self._loaded = False

    def load_from_pdf(self, pdf_path: Path) -> int:
        """
        Load appearance streams from a reference PDF.

        Extracts the /AP (appearance) dictionary from each annotation
        and stores it keyed by subject name.

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
        self._reader = PdfReader(pdf_path)

        # Process all pages (though we expect single page for maps)
        for page_num, page in enumerate(self._reader.pages):
            self._extract_from_page(page, page_num)

        self._loaded = True
        logger.info(f"Loaded {len(self.appearances)} appearance streams from {pdf_path.name}")

        return len(self.appearances)

    def _extract_from_page(self, page: Any, page_num: int) -> None:
        """
        Extract appearances from a single page.

        Args:
            page: PDF page object
            page_num: Page number (0-indexed)
        """
        annots_ref = page.get("/Annots")
        if not annots_ref:
            return

        # Dereference if needed
        annots = annots_ref.get_object() if hasattr(annots_ref, "get_object") else annots_ref
        if not annots:
            return

        for annot_ref in annots:
            try:
                annot = annot_ref.get_object() if hasattr(annot_ref, "get_object") else annot_ref

                # Get subject
                subj = annot.get("/Subj") or annot.get("/Subject") or ""
                subj_str = str(subj).strip()

                if not subj_str:
                    continue

                # Skip if we already have this subject (use first occurrence)
                if subj_str in self.appearances:
                    continue

                # Check for appearance dictionary
                ap = annot.get("/AP")
                if not ap:
                    continue

                # Store the annotation data we need to copy
                self.appearances[subj_str] = {
                    "annot_ref": annot_ref,  # Keep reference for indirect objects
                    "subtype": str(annot.get("/Subtype", "/Circle")),
                    "ic": annot.get("/IC"),  # Interior color
                    "c": annot.get("/C"),  # Border color
                    "bs": annot.get("/BS"),  # Border style
                    "rd": annot.get("/RD"),  # Rect difference
                    "ap": ap,  # Appearance dictionary
                    "oc": annot.get("/OC"),  # Optional content
                    "page_num": page_num,
                }

                logger.debug(f"Extracted appearance for: {subj_str}")

            except Exception as e:
                logger.debug(f"Error extracting annotation appearance: {e}")
                continue

    def get_appearance_data(self, subject: str) -> dict[str, Any] | None:
        """
        Get appearance data for a given subject.

        Args:
            subject: Annotation subject name

        Returns:
            Dictionary with appearance data, or None if not found
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

    def get_reader(self) -> PdfReader | None:
        """
        Get the PDF reader for indirect object resolution.

        Returns:
            PdfReader instance or None if not loaded
        """
        return self._reader
