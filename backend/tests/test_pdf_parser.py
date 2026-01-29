"""Tests for PDF annotation parser."""

import pytest
from app.services.pdf_parser import PDFAnnotationParser


class TestPDFAnnotationParser:
    """Test suite for PDFAnnotationParser service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PDFAnnotationParser()

    def test_parse_pdf(self):
        """Test PDF parsing extracts annotations correctly."""
        # TODO: Implement test
        # Use samples/maps/BidMap.pdf as test input
        pytest.skip("Not yet implemented")

    def test_validate_pdf(self):
        """Test PDF validation."""
        # TODO: Implement test
        pytest.skip("Not yet implemented")

    def test_get_page_count(self):
        """Test page count extraction."""
        # TODO: Implement test
        pytest.skip("Not yet implemented")
