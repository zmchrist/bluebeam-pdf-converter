"""
PDF annotation parsing service.

Extracts markup annotations from PDF files to identify icon locations and subjects.
"""

from pathlib import Path
from PyPDF2 import PdfReader
from app.models.annotation import Annotation, AnnotationCoordinates
from app.services.subject_extractor import SubjectExtractor
from app.utils.errors import (
    InvalidFileTypeError,
    NoAnnotationsFoundError,
    MultiPagePDFError,
)


class PDFAnnotationParser:
    """
    Service for parsing PDF files and extracting annotation data.

    Uses PyPDF2 for PDF parsing.
    """

    def __init__(self):
        """Initialize PDF parser."""
        self.subject_extractor = SubjectExtractor()

    def validate_pdf(self, pdf_path: Path) -> bool:
        """
        Validate that file is a valid PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            True if valid PDF, False otherwise
        """
        if not pdf_path.exists():
            return False

        try:
            with pdf_path.open("rb") as f:
                header = f.read(4)
                return header == b"%PDF"
        except (IOError, PermissionError):
            return False

    def get_page_count(self, pdf_path: Path) -> int:
        """
        Get number of pages in PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Number of pages

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            InvalidFileTypeError: If file is not a valid PDF
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not self.validate_pdf(pdf_path):
            raise InvalidFileTypeError("File is not a valid PDF")

        reader = PdfReader(pdf_path)
        return len(reader.pages)

    def parse_pdf(self, pdf_path: Path) -> list[Annotation]:
        """
        Parse PDF file and extract all markup annotations.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of Annotation objects with coordinates and subjects

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            InvalidFileTypeError: If file is not a valid PDF
            MultiPagePDFError: If PDF has multiple pages (MVP limitation)
            NoAnnotationsFoundError: If no annotations found
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not self.validate_pdf(pdf_path):
            raise InvalidFileTypeError("File is not a valid PDF")

        reader = PdfReader(pdf_path)
        page_count = len(reader.pages)

        # MVP: Single page only
        if page_count > 1:
            raise MultiPagePDFError(
                f"Multi-page PDFs not supported (found {page_count} pages)"
            )

        annotations = []
        page = reader.pages[0]

        # Check if page has annotations
        if "/Annots" not in page:
            raise NoAnnotationsFoundError("No annotations found in PDF")

        annots = page["/Annots"]
        if not annots:
            raise NoAnnotationsFoundError("No annotations found in PDF")

        for annot_ref in annots:
            try:
                # Get the annotation object (dereference if needed)
                annot = annot_ref.get_object()

                # Extract subject from annotation
                subject_raw = self._extract_subject_from_annot(annot)
                subject = self.subject_extractor.extract_subject(
                    {"subject": subject_raw}
                )

                # Extract coordinates from /Rect field
                rect = annot.get("/Rect", [])
                if len(rect) < 4:
                    # Skip annotations without valid rect
                    continue

                # PDF rect format: [x1, y1, x2, y2] (lower-left, upper-right)
                x1 = float(rect[0])
                y1 = float(rect[1])
                x2 = float(rect[2])
                y2 = float(rect[3])

                coords = AnnotationCoordinates(
                    x=x1,
                    y=y1,
                    width=abs(x2 - x1),
                    height=abs(y2 - y1),
                    page=1,
                )

                # Extract annotation type
                annot_type = str(annot.get("/Subtype", "/Unknown"))

                # Create annotation object
                annotation = Annotation(
                    subject=subject,
                    coordinates=coords,
                    annotation_type=annot_type,
                    raw_data=self._annot_to_dict(annot),
                )
                annotations.append(annotation)

            except Exception:
                # Skip annotations that can't be parsed
                continue

        if not annotations:
            raise NoAnnotationsFoundError("No valid annotations found in PDF")

        return annotations

    def _extract_subject_from_annot(self, annot) -> str:
        """
        Extract subject string from annotation object.

        Args:
            annot: PyPDF2 annotation object

        Returns:
            Subject string or empty string if not found
        """
        # Try /Subject first (most common)
        subject = annot.get("/Subject")
        if subject:
            return str(subject)

        # Try /Subj (alternative key)
        subject = annot.get("/Subj")
        if subject:
            return str(subject)

        # Try /T (title field, sometimes used for stamps)
        subject = annot.get("/T")
        if subject:
            return str(subject)

        # Try /Contents (sometimes contains subject info)
        contents = annot.get("/Contents")
        if contents:
            return str(contents)

        return ""

    def _annot_to_dict(self, annot) -> dict | None:
        """
        Convert annotation object to dictionary for storage.

        Args:
            annot: PyPDF2 annotation object

        Returns:
            Dictionary representation or None if conversion fails
        """
        try:
            result = {}
            for key in annot.keys():
                try:
                    value = annot[key]
                    # Convert to string for serialization
                    result[str(key)] = str(value)
                except Exception:
                    pass
            return result if result else None
        except Exception:
            return None

    def get_annotation_summary(self, pdf_path: Path) -> dict:
        """
        Get a summary of annotations in the PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with annotation statistics
        """
        annotations = self.parse_pdf(pdf_path)

        # Count by type
        type_counts: dict[str, int] = {}
        for annot in annotations:
            annot_type = annot.annotation_type
            type_counts[annot_type] = type_counts.get(annot_type, 0) + 1

        # Get unique subjects
        subjects = list(set(a.subject for a in annotations if a.subject))

        return {
            "total_annotations": len(annotations),
            "type_counts": type_counts,
            "unique_subjects": subjects,
            "subject_count": len(subjects),
        }
