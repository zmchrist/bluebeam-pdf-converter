"""Tests for PDF annotation parser."""

import pytest
from pathlib import Path
import tempfile
from app.services.pdf_parser import PDFAnnotationParser
from app.utils.errors import (
    InvalidFileTypeError,
    NoAnnotationsFoundError,
    MultiPagePDFError,
)


class TestPDFAnnotationParser:
    """Test suite for PDFAnnotationParser service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDFAnnotationParser()
        self.sample_pdf = Path("samples/maps/BidMap.pdf")

    # Tests for validate_pdf()

    def test_validate_pdf_with_valid_pdf(self):
        """Test PDF validation with a valid PDF file."""
        if not self.sample_pdf.exists():
            pytest.skip("Sample PDF not found")

        result = self.parser.validate_pdf(self.sample_pdf)
        assert result is True

    def test_validate_pdf_with_nonexistent_file(self):
        """Test PDF validation with non-existent file."""
        result = self.parser.validate_pdf(Path("nonexistent.pdf"))
        assert result is False

    def test_validate_pdf_with_non_pdf_file(self):
        """Test PDF validation with non-PDF file."""
        # Create a temp file that's not a PDF
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("This is not a PDF")
            temp_path = Path(f.name)

        try:
            result = self.parser.validate_pdf(temp_path)
            assert result is False
        finally:
            temp_path.unlink()

    # Tests for get_page_count()

    def test_get_page_count_valid_pdf(self):
        """Test getting page count from valid PDF."""
        if not self.sample_pdf.exists():
            pytest.skip("Sample PDF not found")

        count = self.parser.get_page_count(self.sample_pdf)
        assert count >= 1

    def test_get_page_count_nonexistent_file(self):
        """Test getting page count from non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.parser.get_page_count(Path("nonexistent.pdf"))

    def test_get_page_count_invalid_pdf(self):
        """Test getting page count from invalid PDF."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".pdf", delete=False
        ) as f:
            f.write("This is not a PDF")
            temp_path = Path(f.name)

        try:
            with pytest.raises(InvalidFileTypeError):
                self.parser.get_page_count(temp_path)
        finally:
            temp_path.unlink()

    # Tests for parse_pdf()

    def test_parse_pdf_extracts_annotations(self):
        """Test that parse_pdf extracts annotations from BidMap.pdf."""
        if not self.sample_pdf.exists():
            pytest.skip("Sample PDF not found")

        annotations = self.parser.parse_pdf(self.sample_pdf)
        assert len(annotations) > 0

    def test_parse_pdf_annotations_have_coordinates(self):
        """Test that extracted annotations have valid coordinates."""
        if not self.sample_pdf.exists():
            pytest.skip("Sample PDF not found")

        annotations = self.parser.parse_pdf(self.sample_pdf)
        for annot in annotations:
            assert annot.coordinates is not None
            assert annot.coordinates.width >= 0
            assert annot.coordinates.height >= 0
            assert annot.coordinates.page == 1

    def test_parse_pdf_annotations_have_type(self):
        """Test that extracted annotations have annotation type."""
        if not self.sample_pdf.exists():
            pytest.skip("Sample PDF not found")

        annotations = self.parser.parse_pdf(self.sample_pdf)
        for annot in annotations:
            assert annot.annotation_type is not None
            assert annot.annotation_type != ""

    def test_parse_pdf_nonexistent_file(self):
        """Test parsing non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_pdf(Path("nonexistent.pdf"))

    def test_parse_pdf_invalid_file(self):
        """Test parsing invalid PDF raises error."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".pdf", delete=False
        ) as f:
            f.write("This is not a PDF")
            temp_path = Path(f.name)

        try:
            with pytest.raises(InvalidFileTypeError):
                self.parser.parse_pdf(temp_path)
        finally:
            temp_path.unlink()

    # Tests for get_annotation_summary()

    def test_get_annotation_summary(self):
        """Test getting annotation summary."""
        if not self.sample_pdf.exists():
            pytest.skip("Sample PDF not found")

        summary = self.parser.get_annotation_summary(self.sample_pdf)

        assert "total_annotations" in summary
        assert "type_counts" in summary
        assert "unique_subjects" in summary
        assert "subject_count" in summary

        assert summary["total_annotations"] > 0
        assert isinstance(summary["type_counts"], dict)
        assert isinstance(summary["unique_subjects"], list)

    # Tests for internal methods

    def test_annot_to_dict_handles_none(self):
        """Test that _annot_to_dict handles None gracefully."""
        # This tests internal error handling
        result = self.parser._annot_to_dict(None)
        assert result is None

    # Integration tests

    def test_parse_and_validate_roundtrip(self):
        """Test that we can validate, get page count, and parse in sequence."""
        if not self.sample_pdf.exists():
            pytest.skip("Sample PDF not found")

        # Validate
        is_valid = self.parser.validate_pdf(self.sample_pdf)
        assert is_valid is True

        # Get page count
        page_count = self.parser.get_page_count(self.sample_pdf)
        assert page_count >= 1

        # Parse
        annotations = self.parser.parse_pdf(self.sample_pdf)
        assert len(annotations) > 0

        # Summary
        summary = self.parser.get_annotation_summary(self.sample_pdf)
        assert summary["total_annotations"] == len(annotations)


class TestPDFAnnotationParserWithDeploymentMap:
    """Additional tests with DeploymentMap.pdf if available."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDFAnnotationParser()
        self.deployment_pdf = Path("samples/maps/DeploymentMap.pdf")

    def test_parse_deployment_map(self):
        """Test parsing DeploymentMap.pdf if it exists."""
        if not self.deployment_pdf.exists():
            pytest.skip("DeploymentMap.pdf not found")

        annotations = self.parser.parse_pdf(self.deployment_pdf)
        assert len(annotations) > 0


class TestPDFAnnotationParserEdgeCases:
    """Edge case tests for PDFAnnotationParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDFAnnotationParser()

    def test_parse_pdf_with_empty_subject(self):
        """Verify parser handles annotations with empty subjects."""
        sample_pdf = Path("samples/maps/BidMap.pdf")
        if not sample_pdf.exists():
            pytest.skip("Sample PDF not found")

        # Parse should succeed even if some annotations have empty subjects
        annotations = self.parser.parse_pdf(sample_pdf)
        # At least some annotations should exist
        assert len(annotations) > 0
        # All annotations should have a subject field (may be empty string)
        for annot in annotations:
            assert annot.subject is not None

    def test_coordinates_are_positive_or_zero(self):
        """Verify coordinates are non-negative."""
        sample_pdf = Path("samples/maps/BidMap.pdf")
        if not sample_pdf.exists():
            pytest.skip("Sample PDF not found")

        annotations = self.parser.parse_pdf(sample_pdf)
        for annot in annotations:
            # Width and height should be non-negative
            assert annot.coordinates.width >= 0
            assert annot.coordinates.height >= 0
