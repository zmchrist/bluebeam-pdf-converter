"""
Subject name extraction and translation service.

Extracts icon subject names from annotations and translates hex-encoded subjects.
"""


class SubjectExtractor:
    """Service for extracting and translating annotation subject names."""

    def extract_subject(self, annotation_dict: dict) -> str:
        """
        Extract subject name from annotation dictionary.

        Args:
            annotation_dict: Raw annotation dictionary from PDF

        Returns:
            Subject name as string
        """
        # Try different possible keys for subject
        subject = annotation_dict.get("subject", "")
        if not subject:
            subject = annotation_dict.get("Subject", "")
        if not subject:
            subject = annotation_dict.get("Subj", "")
        if not subject:
            subject = annotation_dict.get("/Subject", "")
        if not subject:
            subject = annotation_dict.get("/Subj", "")

        # Convert to string if needed
        subject = str(subject) if subject else ""

        # Check if hex-encoded and translate
        if subject and self.is_hex_encoded(subject):
            return self.translate_hex_subject(subject)

        return subject

    @staticmethod
    def is_hex_encoded(subject: str) -> bool:
        """
        Check if subject string is hex-encoded.

        Args:
            subject: Subject string to check

        Returns:
            True if the string appears to be hex-encoded
        """
        # Empty strings are not hex-encoded
        if not subject:
            return False

        # Hex strings must have even length
        if len(subject) % 2 != 0:
            return False

        # Must be at least 4 characters for a reasonable subject name
        if len(subject) < 4:
            return False

        # Check if all characters are valid hex digits
        try:
            int(subject, 16)
            # Additional check: if it contains only letters and underscores,
            # it's probably a plain text subject like "AP_Bid"
            if subject.replace("_", "").isalpha():
                return False
            return True
        except ValueError:
            return False

    def translate_hex_subject(self, hex_subject: str) -> str:
        """
        Translate hex-encoded subject to string.

        Attempts to decode using various encodings:
        - First checks if it looks like UTF-16-BE (has null bytes pattern)
        - Otherwise tries UTF-8/ASCII first
        - Falls back to UTF-16-BE, then latin-1

        Args:
            hex_subject: Hex-encoded subject name

        Returns:
            Decoded subject name

        Examples:
            "4150005f426964" -> "AP_Bid" (UTF-16-BE with null bytes)
            "41505f426964" -> "AP_Bid" (ASCII/UTF-8)
        """
        try:
            bytes_data = bytes.fromhex(hex_subject)

            # Check if this looks like UTF-16-BE (null byte pattern: 00XX00YY)
            # UTF-16-BE for ASCII chars has null bytes in odd positions
            has_null_pattern = (
                len(bytes_data) >= 2
                and len(bytes_data) % 2 == 0
                and bytes_data[0] == 0
            )

            if has_null_pattern:
                # Try UTF-16-BE first for null-byte patterns
                try:
                    decoded = bytes_data.decode("utf-16-be")
                    result = decoded.replace("\x00", "")
                    if result and result.isprintable():
                        return result
                except UnicodeDecodeError:
                    pass

            # Try UTF-8/ASCII first for non-null-byte patterns
            try:
                result = bytes_data.decode("utf-8")
                if result and result.isprintable():
                    return result
            except UnicodeDecodeError:
                pass

            # Try UTF-16-BE as fallback
            try:
                decoded = bytes_data.decode("utf-16-be")
                result = decoded.replace("\x00", "")
                if result and result.isprintable():
                    return result
            except UnicodeDecodeError:
                pass

            # Try latin-1 as last resort (accepts any byte)
            try:
                result = bytes_data.decode("latin-1")
                result = result.replace("\x00", "")
                if result and result.isprintable():
                    return result
            except UnicodeDecodeError:
                pass

            # Fallback: return original hex string
            return hex_subject

        except (ValueError, Exception):
            # If hex conversion fails, return original
            return hex_subject
