"""Integration tests for API endpoints."""

import io
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestHealthEndpoint:
    """Test suite for /health endpoint."""

    def test_health_check_returns_status(self):
        """Test health endpoint returns status info."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "mapping_loaded" in data
        assert "mapping_count" in data
        assert "toolchest_bid_icons" in data
        assert "toolchest_deployment_icons" in data


class TestRootEndpoint:
    """Test suite for / endpoint."""

    def test_root_returns_api_info(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data


class TestUploadEndpoint:
    """Test suite for /api/upload endpoint."""

    def test_upload_non_pdf_file(self):
        """Test uploading non-PDF file returns 400."""
        content = b"This is not a PDF"
        response = client.post(
            "/api/upload",
            files={"file": ("test.txt", content, "text/plain")},
        )
        assert response.status_code == 400
        assert "not a PDF" in response.json()["detail"]

    def test_upload_pdf_without_extension(self):
        """Test uploading file without .pdf extension returns 400."""
        content = b"%PDF-1.4 fake pdf content"
        response = client.post(
            "/api/upload",
            files={"file": ("test", content, "application/octet-stream")},
        )
        assert response.status_code == 400
        assert "not a PDF" in response.json()["detail"]

    def test_upload_non_pdf_with_pdf_extension(self):
        """Test uploading non-PDF content with .pdf extension returns 400."""
        content = b"This is not a PDF content"
        response = client.post(
            "/api/upload",
            files={"file": ("fake.pdf", content, "application/pdf")},
        )
        assert response.status_code == 400
        assert "not a valid PDF" in response.json()["detail"]


class TestConvertEndpoint:
    """Test suite for /api/convert endpoint."""

    def test_convert_invalid_upload_id(self):
        """Test convert with invalid upload_id returns 404."""
        response = client.post(
            "/api/convert/invalid-uuid-here",
            json={"direction": "bid_to_deployment"},
        )
        assert response.status_code == 404
        assert "not found or expired" in response.json()["detail"]

    def test_convert_invalid_direction(self):
        """Test convert with invalid direction returns 400."""
        # First need to mock a valid upload
        from app.services.file_manager import file_manager, FileMetadata
        from datetime import datetime

        # Create mock metadata
        mock_metadata = FileMetadata(
            file_id="test-upload-id",
            original_name="test.pdf",
            file_path=Path("/tmp/test.pdf"),
            created_at=datetime.now(),
            file_size=1000,
        )

        with patch.object(file_manager, 'get_file', return_value=mock_metadata):
            response = client.post(
                "/api/convert/test-upload-id",
                json={"direction": "deployment_to_bid"},
            )
            assert response.status_code == 400
            assert "Invalid conversion direction" in response.json()["detail"]


class TestDownloadEndpoint:
    """Test suite for /api/download endpoint."""

    def test_download_invalid_file_id(self):
        """Test download with invalid file_id returns 404."""
        response = client.get("/api/download/invalid-uuid-here")
        assert response.status_code == 404
        assert "not found or expired" in response.json()["detail"]

    def test_download_valid_file(self):
        """Test download with valid file returns PDF."""
        from app.services.file_manager import file_manager
        import tempfile

        # Create a real temp file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4 test content")
            temp_path = Path(f.name)

        try:
            # Store file via file_manager
            content = b"%PDF-1.4 test content"
            metadata = file_manager.store_upload(content, "test.pdf")

            # Download it
            response = client.get(f"/api/download/{metadata.file_id}")
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"
            assert "attachment" in response.headers.get("content-disposition", "")
        finally:
            temp_path.unlink(missing_ok=True)
