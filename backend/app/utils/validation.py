"""Input validation utilities."""

from pathlib import Path


def validate_pdf_file(file_path: Path) -> tuple[bool, str]:
    """
    Validate that file is a valid PDF.

    Args:
        file_path: Path to file

    Returns:
        Tuple of (is_valid, message)
        - If valid: (True, "Valid")
        - If invalid: (False, error message)
    """
    if not file_path.exists():
        return False, "File not found"

    try:
        with file_path.open("rb") as f:
            header = f.read(4)
            if header != b"%PDF":
                return False, "File is not a valid PDF"
    except (IOError, PermissionError) as e:
        return False, f"Cannot read file: {str(e)}"

    return True, "Valid"


def validate_file_size(file_size: int, max_size_mb: int = 50) -> tuple[bool, str]:
    """
    Validate file size is within limits.

    Args:
        file_size: File size in bytes
        max_size_mb: Maximum allowed size in MB

    Returns:
        Tuple of (is_valid, message)
        - If valid: (True, "Valid")
        - If too large: (False, error message)
    """
    if file_size < 0:
        return False, "Invalid file size"

    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        return False, f"File too large (max {max_size_mb}MB)"

    return True, "Valid"


def validate_conversion_direction(direction: str) -> tuple[bool, str]:
    """
    Validate conversion direction parameter.

    Args:
        direction: Conversion direction string

    Returns:
        Tuple of (is_valid, message)
        - If valid: (True, "Valid")
        - If invalid: (False, error message)
    """
    if direction == "bid_to_deployment":
        return True, "Valid"

    if direction == "deployment_to_bid":
        return False, "Deployment to bid conversion not yet supported"

    return False, f"Invalid direction: {direction}"
