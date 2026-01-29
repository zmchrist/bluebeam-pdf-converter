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
        # TODO: Implement subject extraction
        # Extract /Subj field from annotation dictionary
        raise NotImplementedError("Subject extraction not yet implemented")

    def translate_hex_subject(self, hex_subject: str) -> str:
        """
        Translate hex-encoded subject to string.

        Args:
            hex_subject: Hex-encoded subject name

        Returns:
            Decoded subject name

        Examples:
            "4150005f426964" -> "AP_Bid"
        """
        # TODO: Implement hex translation
        # Check if subject is hex-encoded
        # Decode hex to string if needed
        raise NotImplementedError("Hex translation not yet implemented")
