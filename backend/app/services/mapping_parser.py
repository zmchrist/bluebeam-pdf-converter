"""
Mapping configuration parser service.

Parses mapping.md markdown table to create bid↔deployment icon mappings.
"""

from pathlib import Path
from app.models.mapping import IconMapping, MappingEntry


class MappingParser:
    """Service for parsing mapping.md configuration file."""

    def __init__(self, mapping_file: Path):
        """
        Initialize mapping parser.

        Args:
            mapping_file: Path to mapping.md file
        """
        self.mapping_file = mapping_file
        self.mappings: dict[str, str] = {}
        self.categories: dict[str, str] = {}

    def load_mappings(self) -> IconMapping:
        """
        Load and parse mapping.md file.

        Returns:
            IconMapping object with bid→deployment mappings

        Raises:
            FileNotFoundError: If mapping.md doesn't exist
            ValueError: If mapping.md format is invalid
        """
        # TODO: Implement mapping parsing
        # 1. Read mapping.md file
        # 2. Parse markdown table (skip header row)
        # 3. Extract bid subject, deployment subject, category
        # 4. Build mappings dictionary
        # 5. Validate no duplicate bid subjects
        # 6. Return IconMapping object
        raise NotImplementedError("Mapping parsing not yet implemented")

    def get_deployment_subject(self, bid_subject: str) -> str | None:
        """
        Look up deployment subject for given bid subject.

        Args:
            bid_subject: Bid icon subject name

        Returns:
            Deployment icon subject name, or None if not found
        """
        return self.mappings.get(bid_subject)

    def validate_mappings(self) -> bool:
        """
        Validate mapping configuration.

        Returns:
            True if valid, False otherwise
        """
        # TODO: Implement validation
        # Check all rows have 3 columns
        # Check no duplicate bid subjects
        # Check no empty subjects
        raise NotImplementedError("Mapping validation not yet implemented")
