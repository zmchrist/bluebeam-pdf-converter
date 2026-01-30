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
        self.entries: list[MappingEntry] = []

    def load_mappings(self) -> IconMapping:
        """
        Load and parse mapping.md file.

        Returns:
            IconMapping object with bid→deployment mappings

        Raises:
            FileNotFoundError: If mapping.md doesn't exist
            ValueError: If mapping.md format is invalid
        """
        if not self.mapping_file.exists():
            raise FileNotFoundError(f"Mapping file not found: {self.mapping_file}")

        with self.mapping_file.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find the start of the table (line starting with |)
        table_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith("|"):
                table_start = i
                break

        if table_start is None:
            raise ValueError("No markdown table found in mapping file")

        # Skip header row (table_start) and separator row (table_start + 1)
        # Data starts at table_start + 2
        data_lines = [
            line.strip()
            for line in lines[table_start + 2 :]
            if line.strip() and line.strip().startswith("|")
        ]

        if not data_lines:
            raise ValueError("No mapping data found in table")

        # Clear any previous data
        self.mappings = {}
        self.categories = {}
        self.entries = []

        for line in data_lines:
            # Parse markdown table row: | Bid | Deployment | Category |
            parts = [p.strip() for p in line.split("|")]

            # Should have at least 4 parts: ['', 'Bid', 'Deployment', 'Category', '']
            if len(parts) >= 4:
                bid_subject = parts[1].strip()
                deployment_subject = parts[2].strip()
                category = parts[3].strip() if len(parts) > 3 else ""

                if bid_subject and deployment_subject:
                    # Check for duplicates
                    if bid_subject in self.mappings:
                        raise ValueError(
                            f"Duplicate bid subject found: {bid_subject}"
                        )

                    self.mappings[bid_subject] = deployment_subject
                    self.categories[bid_subject] = category

                    # Create entry for validation
                    self.entries.append(
                        MappingEntry(
                            bid_icon_subject=bid_subject,
                            deployment_icon_subject=deployment_subject,
                            category=category,
                        )
                    )

        return IconMapping(
            mappings=self.mappings,
            categories=self.categories,
            total_mappings=len(self.mappings),
        )

    def get_deployment_subject(self, bid_subject: str) -> str | None:
        """
        Look up deployment subject for given bid subject.

        Args:
            bid_subject: Bid icon subject name

        Returns:
            Deployment icon subject name, or None if not found
        """
        return self.mappings.get(bid_subject)

    def get_category(self, bid_subject: str) -> str | None:
        """
        Look up category for given bid subject.

        Args:
            bid_subject: Bid icon subject name

        Returns:
            Category name, or None if not found
        """
        return self.categories.get(bid_subject)

    def validate_mappings(self) -> tuple[bool, list[str]]:
        """
        Validate mapping configuration.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check if mappings were loaded
        if not self.mappings:
            errors.append("No mappings loaded")
            return False, errors

        # Check each entry for valid data
        for entry in self.entries:
            if not entry.bid_icon_subject:
                errors.append("Empty bid icon subject found")
            if not entry.deployment_icon_subject:
                errors.append(
                    f"Empty deployment subject for bid: {entry.bid_icon_subject}"
                )

        return len(errors) == 0, errors

    def get_all_bid_subjects(self) -> list[str]:
        """
        Get list of all bid subjects.

        Returns:
            List of bid subject names
        """
        return list(self.mappings.keys())

    def get_all_deployment_subjects(self) -> list[str]:
        """
        Get list of all deployment subjects.

        Returns:
            List of deployment subject names
        """
        return list(self.mappings.values())
