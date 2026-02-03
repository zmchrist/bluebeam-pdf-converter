"""
File management service for handling PDF uploads and downloads.

Manages temporary file storage with UUID-based naming and expiration tracking.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from app.config import settings

logger = logging.getLogger(__name__)


class FileMetadata:
    """Metadata for a stored file."""

    def __init__(
        self,
        file_id: str,
        original_name: str,
        file_path: Path,
        created_at: datetime,
        file_size: int,
        file_type: str = "upload",  # "upload" or "converted"
    ):
        self.file_id = file_id
        self.original_name = original_name
        self.file_path = file_path
        self.created_at = created_at
        self.file_size = file_size
        self.file_type = file_type

    def is_expired(self, retention_hours: int) -> bool:
        """Check if file has expired based on retention period."""
        expiry_time = self.created_at + timedelta(hours=retention_hours)
        return datetime.now() > expiry_time


class FileManager:
    """
    Service for managing PDF file storage and retrieval.

    Handles:
    - Storing uploaded PDFs with UUID-based naming
    - Tracking file metadata for retrieval
    - File expiration checking
    - Cleanup of expired files
    """

    def __init__(self, temp_dir: Path | None = None):
        """
        Initialize FileManager.

        Args:
            temp_dir: Directory for temporary file storage. Defaults to settings.temp_dir
        """
        self.temp_dir = temp_dir or settings.temp_dir
        self._files: dict[str, FileMetadata] = {}

        # Ensure temp directory exists
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def store_upload(self, content: bytes, original_name: str) -> FileMetadata:
        """
        Store an uploaded file.

        Args:
            content: File content as bytes
            original_name: Original filename from upload

        Returns:
            FileMetadata with file_id and storage info
        """
        file_id = str(uuid4())
        safe_name = self._sanitize_filename(original_name)
        file_path = self.temp_dir / f"{file_id}_{safe_name}"

        # Write file
        file_path.write_bytes(content)

        # Create and store metadata
        metadata = FileMetadata(
            file_id=file_id,
            original_name=original_name,
            file_path=file_path,
            created_at=datetime.now(),
            file_size=len(content),
            file_type="upload",
        )
        self._files[file_id] = metadata

        logger.info(f"Stored upload: {file_id} -> {file_path}")
        return metadata

    def store_converted(
        self,
        content: bytes,
        original_name: str,
        upload_id: str,
        custom_filename: str | None = None,
    ) -> FileMetadata:
        """
        Store a converted file.

        Args:
            content: File content as bytes
            original_name: Original filename (will add _deployment suffix if no custom name)
            upload_id: Related upload ID for tracking
            custom_filename: Optional custom output filename (sanitized, .pdf auto-appended)

        Returns:
            FileMetadata with file_id and storage info
        """
        file_id = str(uuid4())

        # Create deployment filename
        if custom_filename and custom_filename.strip():
            # Use custom filename (sanitize and ensure .pdf extension)
            sanitized = self._sanitize_filename(custom_filename.strip())
            # Remove .pdf extension if provided (we'll add it back)
            if sanitized.lower().endswith('.pdf'):
                sanitized = sanitized[:-4]
            converted_name = f"{sanitized}.pdf"
        else:
            # Default: original name + _deployment suffix
            base_name = Path(original_name).stem
            converted_name = f"{base_name}_deployment.pdf"
        file_path = self.temp_dir / f"{file_id}_{converted_name}"

        # Write file
        file_path.write_bytes(content)

        # Create and store metadata
        metadata = FileMetadata(
            file_id=file_id,
            original_name=converted_name,
            file_path=file_path,
            created_at=datetime.now(),
            file_size=len(content),
            file_type="converted",
        )
        self._files[file_id] = metadata

        logger.info(f"Stored converted: {file_id} -> {file_path}")
        return metadata

    def get_file(self, file_id: str) -> FileMetadata | None:
        """
        Get file metadata by ID.

        Args:
            file_id: UUID of the file

        Returns:
            FileMetadata if found and not expired, None otherwise
        """
        metadata = self._files.get(file_id)
        if metadata is None:
            return None

        # Check expiration
        if metadata.is_expired(settings.file_retention_hours):
            self._cleanup_file(file_id)
            return None

        # Check file still exists
        if not metadata.file_path.exists():
            del self._files[file_id]
            return None

        return metadata

    def get_file_path(self, file_id: str) -> Path | None:
        """
        Get file path by ID.

        Args:
            file_id: UUID of the file

        Returns:
            Path to file if found, None otherwise
        """
        metadata = self.get_file(file_id)
        return metadata.file_path if metadata else None

    def _cleanup_file(self, file_id: str) -> None:
        """Remove a file and its metadata."""
        metadata = self._files.get(file_id)
        if metadata:
            try:
                if metadata.file_path.exists():
                    metadata.file_path.unlink()
                logger.info(f"Cleaned up file: {file_id}")
            except Exception as e:
                logger.error(f"Error cleaning up file {file_id}: {e}")
            finally:
                del self._files[file_id]

    def cleanup_expired(self) -> int:
        """
        Remove all expired files.

        Returns:
            Number of files cleaned up
        """
        expired_ids = [
            file_id
            for file_id, metadata in self._files.items()
            if metadata.is_expired(settings.file_retention_hours)
        ]

        for file_id in expired_ids:
            self._cleanup_file(file_id)

        return len(expired_ids)

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Sanitize filename for safe storage."""
        # Remove path components and keep only filename
        safe_name = Path(name).name
        # Replace problematic characters
        for char in ['/', '\\', '..', '\x00']:
            safe_name = safe_name.replace(char, '_')
        return safe_name


# Global file manager instance (singleton pattern)
# NOTE: File metadata is stored in memory and will be lost on server restart.
# For MVP, this is acceptable since files expire after 1 hour anyway.
# For production, consider persisting metadata to disk or database.
file_manager = FileManager()
