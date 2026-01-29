"""
PDF annotation parsing service.

Extracts markup annotations from PDF files to identify icon locations and subjects.
"""

from pathlib import Path
from app.models.annotation import Annotation, AnnotationCoordinates


class PDFAnnotationParser:
    """
    Service for parsing PDF files and extracting annotation data.

    Uses PyPDF2, pypdf, or pdfplumber (to be determined during implementation).
    """

    def __init__(self):
        """Initialize PDF parser."""
        pass

    def parse_pdf(self, pdf_path: Path) -> list[Annotation]:
        """
        Parse PDF file and extract all markup annotations.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of Annotation objects with coordinates and subjects

        Raises:
            ValueError: If PDF is invalid or corrupted
            FileNotFoundError: If PDF file doesn't exist
        """
        # TODO: Implement PDF parsing
        # 1. Open PDF file
        # 2. Iterate through pages (MVP: single page only)
        # 3. Find all markup annotations
        # 4. Extract coordinates, size, and subject for each
        # 5. Return list of Annotation objects
        raise NotImplementedError("PDF parsing not yet implemented")

    def get_page_count(self, pdf_path: Path) -> int:
        """
        Get number of pages in PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Number of pages

        Raises:
            ValueError: If PDF is invalid
        """
        # TODO: Implement page count
        raise NotImplementedError("Page count not yet implemented")

    def validate_pdf(self, pdf_path: Path) -> bool:
        """
        Validate that file is a valid PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            True if valid PDF, False otherwise
        """
        # TODO: Implement PDF validation
        # Check magic number (%PDF header)
        raise NotImplementedError("PDF validation not yet implemented")
