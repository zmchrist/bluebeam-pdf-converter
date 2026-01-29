"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestUploadEndpoint:
    """Test suite for /api/upload endpoint."""

    def test_upload_valid_pdf(self):
        """Test uploading valid PDF."""
        pytest.skip("Not yet implemented")


class TestConvertEndpoint:
    """Test suite for /api/convert endpoint."""

    def test_convert_bid_to_deployment(self):
        """Test bid→deployment conversion."""
        pytest.skip("Not yet implemented")


class TestDownloadEndpoint:
    """Test suite for /api/download endpoint."""

    def test_download_converted_pdf(self):
        """Test downloading converted PDF."""
        pytest.skip("Not yet implemented")
