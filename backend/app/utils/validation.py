"""Input validation utilities."""

from pathlib import Path


def validate_pdf_file(file_path: Path) -> bool:
    """
    Validate that file is a valid PDF.

    Args:
        file_path: Path to file

    Returns:
        True if valid PDF

    Raises:
        ValueError: If file is not a valid PDF
    """
    # TODO: Implement PDF validation
    # Check magic number (%PDF header)
    with open(file_path, "rb") as f:
        header = f.read(4)
        if header != b"%PDF":
            raise ValueError("File is not a valid PDF")
    return True


def validate_file_size(file_size: int, max_size_mb: int = 50) -> bool:
    """
    Validate file size.

    Args:
        file_size: File size in bytes
        max_size_mb: Maximum allowed size in MB

    Returns:
        True if size is valid

    Raises:
        ValueError: If file is too large
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise ValueError(f"PDF file too large (max {max_size_mb}MB)")
    return True


def validate_conversion_direction(direction: str) -> bool:
    """
    Validate conversion direction parameter.

    Args:
        direction: Conversion direction

    Returns:
        True if valid

    Raises:
        ValueError: If direction is invalid or not supported in MVP
    """
    valid_directions = ["bid_to_deployment"]
    if direction not in valid_directions:
        raise ValueError(
            f"Invalid conversion direction. MVP supports 'bid_to_deployment' only."
        )
    return True
