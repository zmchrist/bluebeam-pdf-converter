"""Tests for FileManager service."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path


from app.services.file_manager import FileManager, FileMetadata


class TestFileMetadata:
    """Tests for FileMetadata class."""

    def test_is_expired_false(self):
        """Test file not expired within retention period."""
        metadata = FileMetadata(
            file_id="test-id",
            original_name="test.pdf",
            file_path=Path("/tmp/test.pdf"),
            created_at=datetime.now(),
            file_size=1000,
        )
        assert not metadata.is_expired(1)  # 1 hour retention

    def test_is_expired_true(self):
        """Test file expired after retention period."""
        metadata = FileMetadata(
            file_id="test-id",
            original_name="test.pdf",
            file_path=Path("/tmp/test.pdf"),
            created_at=datetime.now() - timedelta(hours=2),
            file_size=1000,
        )
        assert metadata.is_expired(1)  # 1 hour retention


class TestFileManager:
    """Tests for FileManager class."""

    def test_store_upload(self):
        """Test storing an uploaded file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(Path(temp_dir))
            content = b"PDF content here"

            metadata = manager.store_upload(content, "test.pdf")

            assert metadata.file_id is not None
            assert metadata.original_name == "test.pdf"
            assert metadata.file_path.exists()
            assert metadata.file_size == len(content)
            assert metadata.file_path.read_bytes() == content

    def test_store_converted(self):
        """Test storing a converted file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(Path(temp_dir))
            content = b"Converted PDF content"

            metadata = manager.store_converted(content, "original.pdf", "upload-123")

            assert metadata.file_id is not None
            assert metadata.original_name == "original_deployment.pdf"
            assert metadata.file_path.exists()
            assert "_deployment.pdf" in str(metadata.file_path)

    def test_store_converted_with_custom_filename(self):
        """Test storing a converted file with custom filename."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(Path(temp_dir))
            content = b"Converted PDF content"

            metadata = manager.store_converted(
                content, "original.pdf", "upload-123", custom_filename="my_custom_file"
            )

            assert metadata.file_id is not None
            assert metadata.original_name == "my_custom_file.pdf"
            assert metadata.file_path.exists()
            assert "my_custom_file.pdf" in str(metadata.file_path)

    def test_store_converted_custom_filename_with_pdf_extension(self):
        """Test custom filename already has .pdf extension."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(Path(temp_dir))
            content = b"Converted PDF content"

            metadata = manager.store_converted(
                content, "original.pdf", "upload-123", custom_filename="my_file.pdf"
            )

            assert metadata.original_name == "my_file.pdf"
            # Should not have double extension like my_file.pdf.pdf
            assert "my_file.pdf.pdf" not in str(metadata.file_path)

    def test_store_converted_empty_custom_filename(self):
        """Test empty custom filename falls back to default."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(Path(temp_dir))
            content = b"Converted PDF content"

            metadata = manager.store_converted(
                content, "original.pdf", "upload-123", custom_filename="   "
            )

            # Should use default naming
            assert metadata.original_name == "original_deployment.pdf"

    def test_get_file_exists(self):
        """Test retrieving an existing file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(Path(temp_dir))
            content = b"PDF content"
            stored = manager.store_upload(content, "test.pdf")

            retrieved = manager.get_file(stored.file_id)

            assert retrieved is not None
            assert retrieved.file_id == stored.file_id

    def test_get_file_not_exists(self):
        """Test retrieving non-existent file returns None."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(Path(temp_dir))

            result = manager.get_file("non-existent-id")

            assert result is None

    def test_get_file_path(self):
        """Test getting file path by ID."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = FileManager(Path(temp_dir))
            content = b"PDF content"
            stored = manager.store_upload(content, "test.pdf")

            path = manager.get_file_path(stored.file_id)

            assert path is not None
            assert path == stored.file_path

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert FileManager._sanitize_filename("test.pdf") == "test.pdf"
        assert FileManager._sanitize_filename("/path/to/test.pdf") == "test.pdf"
        # Path.name only extracts the last component, so ..test.pdf becomes _test.pdf
        # after sanitizing the leading dots
        result = FileManager._sanitize_filename("..test.pdf")
        assert ".." not in result or result == "_test.pdf"
