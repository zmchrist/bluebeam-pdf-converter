"""Tests for annotation replacer service."""

import tempfile
from pathlib import Path

import pytest
import pymupdf

from app.models.annotation import Annotation, AnnotationCoordinates
from app.models.mapping import IconData
from app.services.annotation_replacer import AnnotationReplacer


class MockMappingParser:
    """Mock mapping parser for testing."""

    def __init__(self, mappings: dict[str, str] | None = None):
        self.mappings = mappings or {}

    def get_deployment_subject(self, bid_subject: str) -> str | None:
        return self.mappings.get(bid_subject)

    def get_all_bid_subjects(self) -> list[str]:
        return list(self.mappings.keys())


class MockBTXLoader:
    """Mock BTX loader for testing."""

    def __init__(self, icons: dict[str, IconData] | None = None):
        self.icons = icons or {}

    def get_icon_data(self, subject: str, icon_type: str = "deployment") -> IconData | None:
        return self.icons.get(subject)


class MockAppearanceExtractor:
    """Mock appearance extractor for testing."""

    def __init__(self, appearances: dict[str, dict] | None = None):
        self.appearances = appearances or {}

    def has_appearance(self, subject: str) -> bool:
        return subject in self.appearances

    def get_appearance_data(self, subject: str) -> dict | None:
        return self.appearances.get(subject)


def create_test_pdf_with_annotations(
    pdf_path: Path,
    annotations: list[dict],
) -> None:
    """
    Create a test PDF with annotations.

    Args:
        pdf_path: Path to save the PDF
        annotations: List of annotation dictionaries with keys:
            - subject: str
            - x, y, width, height: float
            - type: str (e.g., "/Circle")
    """
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)  # Letter size

    for annot_data in annotations:
        rect = pymupdf.Rect(
            annot_data["x"],
            annot_data["y"],
            annot_data["x"] + annot_data["width"],
            annot_data["y"] + annot_data["height"],
        )

        annot_type = annot_data.get("type", "/Circle")
        if annot_type == "/Circle":
            annot = page.add_circle_annot(rect)
        elif annot_type == "/Square":
            annot = page.add_rect_annot(rect)
        else:
            annot = page.add_circle_annot(rect)

        # Set subject
        info = annot.info
        info["subject"] = annot_data["subject"]
        annot.set_info(info)

        # Set colors
        annot.set_colors(fill=(0.5, 0.5, 0.5), stroke=(0, 0, 0))
        annot.update()

    doc.save(pdf_path)
    doc.close()


class TestAnnotationReplacer:
    """Test suite for AnnotationReplacer service."""

    def test_init(self):
        """Test replacer initialization."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        assert replacer.mapping_parser == mapper
        assert replacer.btx_loader == loader
        assert replacer.appearance_extractor is None

    def test_init_with_appearance_extractor(self):
        """Test replacer initialization with appearance extractor."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        extractor = MockAppearanceExtractor()
        replacer = AnnotationReplacer(mapper, loader, extractor)

        assert replacer.appearance_extractor == extractor

    def test_create_deployment_annotation(self):
        """Test creating deployment annotation metadata."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        bid_annot = Annotation(
            subject="AP_Bid",
            coordinates=AnnotationCoordinates(
                x=100.0, y=200.0, width=50.0, height=50.0, page=1
            ),
            annotation_type="/Circle",
        )

        result = replacer.create_deployment_annotation(bid_annot, "AP_Deploy")

        assert result is not None
        assert result["subject"] == "AP_Deploy"
        assert result["x"] == 100.0
        assert result["y"] == 200.0
        assert result["width"] == 50.0
        assert result["height"] == 50.0
        assert result["type"] == "/Circle"

    def test_get_colors_default(self):
        """Test getting default colors when no appearance data available."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        fill, stroke, opacity = replacer._get_colors_for_annotation("Unknown", None)

        assert fill == (1.0, 0.5, 0.0)  # Default orange
        assert stroke == (0, 0, 0)  # Default black
        assert opacity == 1.0

    def test_get_colors_from_appearance_extractor(self):
        """Test getting colors from appearance extractor."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        extractor = MockAppearanceExtractor({
            "AP_Deploy": {
                "fill": (0.2, 0.4, 0.6),
                "stroke": (0.1, 0.1, 0.1),
                "opacity": 0.8,
            }
        })
        replacer = AnnotationReplacer(mapper, loader, extractor)

        fill, stroke, opacity = replacer._get_colors_for_annotation("AP_Deploy", None)

        assert fill == (0.2, 0.4, 0.6)
        assert stroke == (0.1, 0.1, 0.1)
        assert opacity == 0.8


class TestAnnotationReplacerWithPDF:
    """Tests that use actual PDF files."""

    def test_replace_annotations_empty_pdf(self):
        """Test replacement with PDF that has no annotations."""
        mapper = MockMappingParser({"AP_Bid": "AP_Deploy"})
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            output_pdf = Path(tmpdir) / "output.pdf"

            # Create empty PDF
            doc = pymupdf.open()
            doc.new_page()
            doc.save(input_pdf)
            doc.close()

            converted, skipped, skipped_subjs = replacer.replace_annotations(
                input_pdf, output_pdf
            )

            assert converted == 0
            assert skipped == 0
            assert skipped_subjs == []
            assert output_pdf.exists()

    def test_replace_annotations_with_mapping(self):
        """Test successful replacement with valid mapping."""
        mappings = {"AP_Bid": "AP_Deploy"}
        mapper = MockMappingParser(mappings)
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            output_pdf = Path(tmpdir) / "output.pdf"

            # Create PDF with annotation
            create_test_pdf_with_annotations(input_pdf, [
                {"subject": "AP_Bid", "x": 100, "y": 200, "width": 50, "height": 50}
            ])

            converted, skipped, skipped_subjs = replacer.replace_annotations(
                input_pdf, output_pdf
            )

            assert converted == 1
            assert skipped == 0
            assert skipped_subjs == []
            assert output_pdf.exists()

            # Verify output PDF has annotation with new subject
            doc = pymupdf.open(output_pdf)
            page = doc[0]
            annots = list(page.annots())
            assert len(annots) == 1
            assert annots[0].info.get("subject") == "AP_Deploy"
            doc.close()

    def test_replace_annotations_missing_mapping(self):
        """Test that annotations without mapping are skipped."""
        mapper = MockMappingParser({})  # Empty mappings
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            output_pdf = Path(tmpdir) / "output.pdf"

            create_test_pdf_with_annotations(input_pdf, [
                {"subject": "Unknown_Icon", "x": 100, "y": 200, "width": 50, "height": 50}
            ])

            converted, skipped, skipped_subjs = replacer.replace_annotations(
                input_pdf, output_pdf
            )

            assert converted == 0
            assert skipped == 1
            assert "Unknown_Icon" in skipped_subjs

    def test_replace_annotations_preserves_coordinates(self):
        """Test that coordinates are preserved during replacement."""
        mappings = {"AP_Bid": "AP_Deploy"}
        mapper = MockMappingParser(mappings)
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            output_pdf = Path(tmpdir) / "output.pdf"

            original_coords = {"x": 150.5, "y": 250.5, "width": 75.0, "height": 75.0}
            create_test_pdf_with_annotations(input_pdf, [
                {"subject": "AP_Bid", **original_coords}
            ])

            replacer.replace_annotations(input_pdf, output_pdf)

            # Verify coordinates preserved
            doc = pymupdf.open(output_pdf)
            page = doc[0]
            annot = next(page.annots())
            rect = annot.rect

            # PyMuPDF may adjust coordinates slightly for circle annotations
            # (by border width), so allow a tolerance of 3 points
            assert abs(rect.x0 - original_coords["x"]) < 3.0
            assert abs(rect.y0 - original_coords["y"]) < 3.0
            assert abs(rect.width - original_coords["width"]) < 5.0
            assert abs(rect.height - original_coords["height"]) < 5.0
            doc.close()

    def test_replace_annotations_multiple_mixed(self):
        """Test replacement with mix of valid and invalid mappings."""
        mappings = {
            "AP_Bid": "AP_Deploy",
            "Switch_Bid": "Switch_Deploy",
        }
        mapper = MockMappingParser(mappings)
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            output_pdf = Path(tmpdir) / "output.pdf"

            create_test_pdf_with_annotations(input_pdf, [
                {"subject": "AP_Bid", "x": 100, "y": 200, "width": 50, "height": 50},
                {"subject": "Unknown_Icon", "x": 200, "y": 300, "width": 50, "height": 50},
                {"subject": "Switch_Bid", "x": 300, "y": 400, "width": 50, "height": 50},
            ])

            converted, skipped, skipped_subjs = replacer.replace_annotations(
                input_pdf, output_pdf
            )

            assert converted == 2
            assert skipped == 1
            assert "Unknown_Icon" in skipped_subjs

            # Verify output has 3 annotations (2 converted + 1 unchanged)
            doc = pymupdf.open(output_pdf)
            page = doc[0]
            annots = list(page.annots())
            subjects = [a.info.get("subject") for a in annots]
            assert "AP_Deploy" in subjects
            assert "Switch_Deploy" in subjects
            assert "Unknown_Icon" in subjects
            doc.close()

    def test_replace_annotations_nonexistent_input(self):
        """Test handling of nonexistent input file."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "nonexistent.pdf"
            output_pdf = Path(tmpdir) / "output.pdf"

            converted, skipped, skipped_subjs = replacer.replace_annotations(
                input_pdf, output_pdf
            )

            assert converted == 0
            assert skipped == 0
            assert skipped_subjs == []
            assert not output_pdf.exists()

    def test_replace_annotations_has_appearance_stream(self):
        """Test that converted annotations have valid appearance streams."""
        mappings = {"AP_Bid": "AP_Deploy"}
        mapper = MockMappingParser(mappings)
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            output_pdf = Path(tmpdir) / "output.pdf"

            create_test_pdf_with_annotations(input_pdf, [
                {"subject": "AP_Bid", "x": 100, "y": 200, "width": 50, "height": 50}
            ])

            replacer.replace_annotations(input_pdf, output_pdf)

            # Verify annotation has appearance stream (AP dictionary)
            doc = pymupdf.open(output_pdf)
            page = doc[0]
            annot = next(page.annots())

            # Check that the annotation can render (has valid appearance)
            # If it has no appearance stream, this would fail
            pixmap = annot.get_pixmap()
            assert pixmap is not None
            assert pixmap.width > 0
            assert pixmap.height > 0
            doc.close()

    def test_replace_annotations_with_colors(self):
        """Test that colors are applied to converted annotations."""
        mappings = {"AP_Bid": "AP_Deploy"}
        mapper = MockMappingParser(mappings)
        loader = MockBTXLoader()
        extractor = MockAppearanceExtractor({
            "AP_Deploy": {
                "fill": (1.0, 0.0, 0.0),  # Red
                "stroke": (0.0, 1.0, 0.0),  # Green
                "opacity": 0.5,
            }
        })
        replacer = AnnotationReplacer(mapper, loader, extractor)

        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            output_pdf = Path(tmpdir) / "output.pdf"

            create_test_pdf_with_annotations(input_pdf, [
                {"subject": "AP_Bid", "x": 100, "y": 200, "width": 50, "height": 50}
            ])

            replacer.replace_annotations(input_pdf, output_pdf)

            # Verify colors were applied
            doc = pymupdf.open(output_pdf)
            page = doc[0]
            annot = next(page.annots())
            colors = annot.colors

            # Check fill color (red)
            assert colors["fill"] is not None
            assert abs(colors["fill"][0] - 1.0) < 0.01

            # Check stroke color (green)
            assert colors["stroke"] is not None
            assert abs(colors["stroke"][1] - 1.0) < 0.01

            doc.close()


class TestAnnotationReplacerIntegration:
    """Integration tests with real PDF and mapping files."""

    def test_with_real_mapping_parser(self):
        """Test with real mapping parser if available."""
        mapping_file = Path("backend/data/mapping.md")
        if not mapping_file.exists():
            mapping_file = Path("data/mapping.md")
        if not mapping_file.exists():
            pytest.skip("mapping.md not found")

        from app.services.mapping_parser import MappingParser

        parser = MappingParser(mapping_file)
        parser.load_mappings()

        loader = MockBTXLoader()
        replacer = AnnotationReplacer(parser, loader)

        # Get a real bid subject from mapping
        bid_subjects = parser.get_all_bid_subjects()
        if not bid_subjects:
            pytest.skip("No bid subjects in mapping")

        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            output_pdf = Path(tmpdir) / "output.pdf"

            create_test_pdf_with_annotations(input_pdf, [
                {"subject": bid_subjects[0], "x": 100, "y": 200, "width": 50, "height": 50}
            ])

            converted, skipped, skipped_subjs = replacer.replace_annotations(
                input_pdf, output_pdf
            )

            assert converted == 1
            assert skipped == 0
