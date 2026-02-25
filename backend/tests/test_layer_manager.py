"""Tests for the LayerManager service."""

from pathlib import Path

import pytest
from pypdf import PdfWriter
from pypdf.generic import IndirectObject

from app.services.layer_manager import LayerManager
from app.config import settings


# Path to the EVENT26 reference PDF
EVENT26_PATH = settings.layer_reference_pdf
HAS_EVENT26 = EVENT26_PATH.exists()


class TestLayerManagerWithReference:
    """Tests that require the EVENT26 reference PDF."""

    @pytest.mark.skipif(not HAS_EVENT26, reason="EVENT26 reference PDF not available")
    def test_apply_with_real_event26(self):
        """Verify all 169 OCGs are cloned and lookup is populated."""
        manager = LayerManager(EVENT26_PATH)
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)

        result = manager.apply_to_writer(writer)

        assert result is True
        assert manager.is_loaded is True
        assert manager.layer_count == 169

    @pytest.mark.skipif(not HAS_EVENT26, reason="EVENT26 reference PDF not available")
    def test_known_subject_lookup(self):
        """Verify a known deployment subject resolves to an IndirectObject."""
        manager = LayerManager(EVENT26_PATH)
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        manager.apply_to_writer(writer)

        ref = manager.get_ocg_ref("AP - Cisco MR36H")

        assert ref is not None
        assert isinstance(ref, IndirectObject)

    @pytest.mark.skipif(not HAS_EVENT26, reason="EVENT26 reference PDF not available")
    def test_unknown_subject_lookup(self):
        """Verify an unknown subject returns None."""
        manager = LayerManager(EVENT26_PATH)
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        manager.apply_to_writer(writer)

        ref = manager.get_ocg_ref("NONEXISTENT - Device")

        assert ref is None

    @pytest.mark.skipif(not HAS_EVENT26, reason="EVENT26 reference PDF not available")
    def test_fiber_names_resolve(self):
        """Verify renamed fiber connector subjects resolve in EVENT26."""
        manager = LayerManager(EVENT26_PATH)
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        manager.apply_to_writer(writer)

        for subject in ["HL - LC Fiber", "HL - SC Fiber", "HL - ST Fiber"]:
            ref = manager.get_ocg_ref(subject)
            assert ref is not None, f"{subject} should have a layer in EVENT26"


class TestLayerManagerWithoutReference:
    """Tests that work without the reference PDF."""

    def test_missing_reference_pdf(self):
        """Missing reference PDF returns False and get_ocg_ref returns None."""
        manager = LayerManager(Path("/nonexistent/file.pdf"))
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)

        result = manager.apply_to_writer(writer)

        assert result is False
        assert manager.is_loaded is False
        assert manager.get_ocg_ref("AP - Cisco MR36H") is None

    def test_before_apply(self):
        """get_ocg_ref returns None before apply_to_writer is called."""
        manager = LayerManager(EVENT26_PATH)

        ref = manager.get_ocg_ref("AP - Cisco MR36H")

        assert ref is None
        assert manager.is_loaded is False
        assert manager.layer_count == 0
