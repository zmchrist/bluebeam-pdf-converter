"""Tests for annotation replacer service."""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import ArrayObject, DictionaryObject, NameObject

from app.models.annotation import Annotation, AnnotationCoordinates
from app.models.mapping import IconData
from app.services.annotation_replacer import AnnotationReplacer


class MockMappingParser:
    """Mock mapping parser for testing."""

    def __init__(self, mappings: dict[str, str] | None = None):
        self.mappings = mappings or {}

    def get_deployment_subject(self, bid_subject: str) -> str | None:
        return self.mappings.get(bid_subject)


class MockBTXLoader:
    """Mock BTX loader for testing."""

    def __init__(self, icons: dict[str, IconData] | None = None):
        self.icons = icons or {}

    def get_icon_data(self, subject: str, icon_type: str = "deployment") -> IconData | None:
        return self.icons.get(subject)


class TestAnnotationReplacer:
    """Test suite for AnnotationReplacer service."""

    # Test initialization

    def test_init(self):
        """Test replacer initialization."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        assert replacer.mapping_parser == mapper
        assert replacer.btx_loader == loader

    # Test create_deployment_annotation

    def test_create_deployment_annotation_basic(self):
        """Test creating deployment annotation with basic data."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        bid_annot = Annotation(
            subject="AP_Bid",
            coordinates=AnnotationCoordinates(
                x=100.0, y=200.0, width=50.0, height=50.0, page=1
            ),
            annotation_type="/Circle",  # Use Circle, common for icons
        )

        result = replacer.create_deployment_annotation(bid_annot, "AP_Deploy")

        assert result is not None
        assert result["/Type"] == "/Annot"
        assert result["/Subtype"] == "/Circle"  # Matches original annotation type
        assert str(result["/Subj"]) == "AP_Deploy"  # Uses /Subj key

        # Check rect preserves coordinates
        rect = result["/Rect"]
        assert float(rect[0]) == 100.0  # x1
        assert float(rect[1]) == 200.0  # y1
        assert float(rect[2]) == 150.0  # x2 = x + width
        assert float(rect[3]) == 250.0  # y2 = y + height

    def test_create_deployment_annotation_with_icon_data(self):
        """Test creating annotation with BTX icon data."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        icon_data = IconData(
            subject="AP_Deploy",
            category="Access Points",
            metadata={"source_file": "test.btx", "raw_hex": ""},
        )

        bid_annot = Annotation(
            subject="AP_Bid",
            coordinates=AnnotationCoordinates(
                x=100.0, y=200.0, width=50.0, height=50.0, page=1
            ),
            annotation_type="/Circle",
        )

        result = replacer.create_deployment_annotation(
            bid_annot, "AP_Deploy", icon_data
        )

        assert result is not None
        assert str(result["/Subj"]) == "AP_Deploy"

    def test_create_deployment_annotation_preserves_contents(self):
        """Test that Contents field is preserved from original annotation."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        bid_annot = Annotation(
            subject="AP_Bid",
            coordinates=AnnotationCoordinates(
                x=100.0, y=200.0, width=50.0, height=50.0, page=1
            ),
            annotation_type="/Stamp",
            raw_data={"/Contents": "Original content"},
        )

        result = replacer.create_deployment_annotation(bid_annot, "AP_Deploy")

        assert "/Contents" in result
        assert "Original content" in str(result["/Contents"])

    # Test replace_annotations

    def test_replace_annotations_empty_list(self):
        """Test replacement with empty annotations list."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        # Create a mock page with /Annots
        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject()

        converted, skipped, skipped_subjs = replacer.replace_annotations([], page)

        assert converted == 0
        assert skipped == 0
        assert skipped_subjs == []

    def test_replace_annotations_with_mapping(self):
        """Test successful replacement with valid mapping."""
        mappings = {"AP_Bid": "AP_Deploy"}
        icons = {
            "AP_Deploy": IconData(
                subject="AP_Deploy",
                category="Access Points",
                metadata={"source_file": "test.btx", "raw_hex": ""},
            )
        }
        mapper = MockMappingParser(mappings)
        loader = MockBTXLoader(icons)
        replacer = AnnotationReplacer(mapper, loader)

        # Create mock page
        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject()

        annotations = [
            Annotation(
                subject="AP_Bid",
                coordinates=AnnotationCoordinates(
                    x=100.0, y=200.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Circle",
            )
        ]

        converted, skipped, skipped_subjs = replacer.replace_annotations(
            annotations, page
        )

        assert converted == 1
        assert skipped == 0
        assert skipped_subjs == []
        # Check annotation was added
        assert len(page["/Annots"]) == 1

    def test_replace_annotations_missing_mapping(self):
        """Test that annotations without mapping are skipped."""
        mapper = MockMappingParser({})  # Empty mappings
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject()

        annotations = [
            Annotation(
                subject="Unknown_Icon",
                coordinates=AnnotationCoordinates(
                    x=100.0, y=200.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            )
        ]

        converted, skipped, skipped_subjs = replacer.replace_annotations(
            annotations, page
        )

        assert converted == 0
        assert skipped == 1
        assert "Unknown_Icon" in skipped_subjs

    def test_replace_annotations_missing_btx_data_still_converts(self):
        """Test that missing BTX data doesn't prevent conversion."""
        mappings = {"AP_Bid": "AP_Deploy"}
        mapper = MockMappingParser(mappings)
        loader = MockBTXLoader({})  # No BTX data

        replacer = AnnotationReplacer(mapper, loader)

        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject()

        annotations = [
            Annotation(
                subject="AP_Bid",
                coordinates=AnnotationCoordinates(
                    x=100.0, y=200.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            )
        ]

        converted, skipped, skipped_subjs = replacer.replace_annotations(
            annotations, page
        )

        # Should still convert (just without visual appearance)
        assert converted == 1
        assert skipped == 0

    def test_replace_annotations_empty_subject_skipped(self):
        """Test that annotations with empty subject are skipped."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject()

        annotations = [
            Annotation(
                subject="",  # Empty subject
                coordinates=AnnotationCoordinates(
                    x=100.0, y=200.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            )
        ]

        converted, skipped, skipped_subjs = replacer.replace_annotations(
            annotations, page
        )

        assert converted == 0
        assert skipped == 1
        assert "(empty subject)" in skipped_subjs

    def test_replace_annotations_multiple_mixed(self):
        """Test replacement with mix of valid and invalid mappings."""
        mappings = {
            "AP_Bid": "AP_Deploy",
            "Switch_Bid": "Switch_Deploy",
        }
        mapper = MockMappingParser(mappings)
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject()

        annotations = [
            Annotation(
                subject="AP_Bid",
                coordinates=AnnotationCoordinates(
                    x=100.0, y=200.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            ),
            Annotation(
                subject="Unknown_Icon",  # No mapping
                coordinates=AnnotationCoordinates(
                    x=200.0, y=300.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            ),
            Annotation(
                subject="Switch_Bid",
                coordinates=AnnotationCoordinates(
                    x=300.0, y=400.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            ),
        ]

        converted, skipped, skipped_subjs = replacer.replace_annotations(
            annotations, page
        )

        assert converted == 2
        assert skipped == 1
        assert "Unknown_Icon" in skipped_subjs
        assert len(page["/Annots"]) == 2

    def test_replace_annotations_creates_annots_array_if_missing(self):
        """Test that /Annots array is created if page doesn't have one."""
        mappings = {"AP_Bid": "AP_Deploy"}
        mapper = MockMappingParser(mappings)
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        # Page without /Annots
        page = DictionaryObject()

        annotations = [
            Annotation(
                subject="AP_Bid",
                coordinates=AnnotationCoordinates(
                    x=100.0, y=200.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            )
        ]

        converted, skipped, skipped_subjs = replacer.replace_annotations(
            annotations, page
        )

        assert converted == 1
        assert "/Annots" in page
        assert len(page["/Annots"]) == 1

    # Test _find_and_remove_annotation

    def test_find_and_remove_annotation_found(self):
        """Test finding and removing annotation by coordinates."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        # Create page with annotation
        from PyPDF2.generic import FloatObject, TextStringObject

        annot = DictionaryObject()
        annot[NameObject("/Subject")] = TextStringObject("AP_Bid")
        annot[NameObject("/Rect")] = ArrayObject([
            FloatObject(100.0),
            FloatObject(200.0),
            FloatObject(150.0),
            FloatObject(250.0),
        ])

        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject([annot])

        coords = AnnotationCoordinates(
            x=100.0, y=200.0, width=50.0, height=50.0, page=1
        )

        result = replacer._find_and_remove_annotation(page, coords, "AP_Bid")

        assert result is True
        assert len(page["/Annots"]) == 0

    def test_find_and_remove_annotation_not_found(self):
        """Test when annotation is not found."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject()

        coords = AnnotationCoordinates(
            x=100.0, y=200.0, width=50.0, height=50.0, page=1
        )

        result = replacer._find_and_remove_annotation(page, coords, "Nonexistent")

        assert result is False

    def test_find_and_remove_annotation_no_annots(self):
        """Test when page has no /Annots array."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        page = DictionaryObject()

        coords = AnnotationCoordinates(
            x=100.0, y=200.0, width=50.0, height=50.0, page=1
        )

        result = replacer._find_and_remove_annotation(page, coords, "AP_Bid")

        assert result is False


class TestAnnotationReplacerIntegration:
    """Integration tests with real PDF and BTX files."""

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

        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject()

        # Use a real bid subject from mapping
        bid_subjects = parser.get_all_bid_subjects()
        if not bid_subjects:
            pytest.skip("No bid subjects in mapping")

        annotations = [
            Annotation(
                subject=bid_subjects[0],
                coordinates=AnnotationCoordinates(
                    x=100.0, y=200.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            )
        ]

        converted, skipped, skipped_subjs = replacer.replace_annotations(
            annotations, page
        )

        assert converted == 1
        assert skipped == 0
