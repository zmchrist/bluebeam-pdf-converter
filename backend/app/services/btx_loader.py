"""
BTX reference file loader service.

Loads icon visual data from toolchest BTX files.
BTX files are XML-based Bluebeam toolchest files containing icon definitions
with zlib-compressed hex-encoded data fields.
"""

import logging
import re
import zlib
from pathlib import Path

from lxml import etree

from app.models.mapping import IconData

logger = logging.getLogger(__name__)


class BTXReferenceLoader:
    """Service for loading BTX toolset files and extracting icon data."""

    # Zlib magic number prefix (hex-encoded)
    ZLIB_MAGIC = "789c"

    def __init__(self, toolchest_dir: Path):
        """
        Initialize BTX loader.

        Args:
            toolchest_dir: Path to toolchest directory
        """
        self.toolchest_dir = toolchest_dir
        self.bid_icons: dict[str, IconData] = {}
        self.deployment_icons: dict[str, IconData] = {}
        self._loaded = False

    @staticmethod
    def decode_hex_zlib(hex_string: str) -> str | None:
        """
        Decode hex-encoded zlib-compressed data to string.

        BTX files contain fields that are hex-encoded zlib-compressed text.
        These fields start with '789c' (zlib magic number).

        Args:
            hex_string: Hex-encoded zlib-compressed string

        Returns:
            Decoded text string, or None if decoding fails

        Example:
            >>> BTXReferenceLoader.decode_hex_zlib('789c73ca4c5108c9cfcf2956d030323032d304002a93047c')
            'Bid Tools 01-2026'
        """
        if not hex_string:
            return None

        # Normalize to lowercase for comparison
        hex_lower = hex_string.lower()

        # Check for zlib magic number
        if not hex_lower.startswith(BTXReferenceLoader.ZLIB_MAGIC):
            logger.debug(f"Hex string does not start with zlib magic: {hex_string[:20]}...")
            return None

        try:
            # Convert hex to bytes
            compressed = bytes.fromhex(hex_string)

            # Decompress using zlib
            decompressed = zlib.decompress(compressed)

            # Decode to UTF-8 text
            text = decompressed.decode("utf-8")

            return text.strip()

        except ValueError as e:
            logger.debug(f"Invalid hex string: {e}")
            return None
        except zlib.error as e:
            logger.debug(f"Zlib decompression failed: {e}")
            return None
        except UnicodeDecodeError as e:
            logger.debug(f"UTF-8 decode failed: {e}")
            # Try latin-1 as fallback
            try:
                text = decompressed.decode("latin-1")
                return text.strip()
            except Exception:
                return None
        except Exception as e:
            logger.debug(f"Unexpected error decoding hex zlib: {e}")
            return None

    @staticmethod
    def is_hex_zlib(value: str) -> bool:
        """
        Check if a string is hex-encoded zlib-compressed data.

        Args:
            value: String to check

        Returns:
            True if string appears to be hex-encoded zlib data
        """
        if not value or len(value) < 8:
            return False
        return value.lower().startswith(BTXReferenceLoader.ZLIB_MAGIC)

    def _parse_btx_file(self, btx_path: Path) -> list[dict]:
        """
        Parse a BTX file and extract ToolChestItem data.

        Args:
            btx_path: Path to BTX file

        Returns:
            List of dictionaries containing tool item data with keys:
            - name: Internal name (not the display subject)
            - type: Annotation type (e.g., 'Bluebeam.PDF.Annotations.AnnotationCircle')
            - raw: Decoded Raw field content
            - raw_hex: Original hex-encoded Raw field
            - resources: List of resource data
            - x, y: Position coordinates
            - index: Tool index
            - children: List of child items

        Raises:
            FileNotFoundError: If BTX file doesn't exist
            ValueError: If BTX file is invalid XML
        """
        if not btx_path.exists():
            raise FileNotFoundError(f"BTX file not found: {btx_path}")

        items = []

        try:
            # Read file content and handle UTF-8 BOM
            content = btx_path.read_bytes()

            # Remove UTF-8 BOM if present
            if content.startswith(b"\xef\xbb\xbf"):
                content = content[3:]

            # Parse XML
            root = etree.fromstring(content)

            # Find all ToolChestItem elements
            for item_elem in root.findall(".//ToolChestItem"):
                item_data = self._parse_tool_item(item_elem)
                if item_data:
                    items.append(item_data)

            logger.debug(f"Parsed {len(items)} tool items from {btx_path.name}")

        except etree.XMLSyntaxError as e:
            raise ValueError(f"Invalid XML in BTX file {btx_path}: {e}")
        except Exception as e:
            logger.error(f"Error parsing BTX file {btx_path}: {e}")
            raise

        return items

    def _parse_tool_item(self, elem: etree._Element) -> dict | None:
        """
        Parse a single ToolChestItem element.

        Args:
            elem: ToolChestItem XML element

        Returns:
            Dictionary with tool item data, or None if parsing fails
        """
        try:
            item = {
                "name": elem.findtext("Name", ""),
                "type": elem.findtext("Type", ""),
                "raw_hex": elem.findtext("Raw", ""),
                "x": float(elem.findtext("X", "0")),
                "y": float(elem.findtext("Y", "0")),
                "index": int(elem.findtext("Index", "0")),
                "resources": [],
                "children": [],
            }

            # Decode Raw field if present
            if item["raw_hex"] and self.is_hex_zlib(item["raw_hex"]):
                item["raw"] = self.decode_hex_zlib(item["raw_hex"])
            else:
                item["raw"] = item["raw_hex"]

            # Parse Resources
            for resource_elem in elem.findall("Resources"):
                resource = {
                    "id_hex": resource_elem.findtext("ID", ""),
                    "data_hex": resource_elem.findtext("Data", ""),
                }
                # Decode ID if zlib-compressed
                if resource["id_hex"] and self.is_hex_zlib(resource["id_hex"]):
                    resource["id"] = self.decode_hex_zlib(resource["id_hex"])
                else:
                    resource["id"] = resource["id_hex"]
                item["resources"].append(resource)

            # Parse Child elements recursively
            for child_elem in elem.findall("Child"):
                child_data = self._parse_child_item(child_elem)
                if child_data:
                    item["children"].append(child_data)

            return item

        except Exception as e:
            logger.debug(f"Error parsing tool item: {e}")
            return None

    def _parse_child_item(self, elem: etree._Element) -> dict | None:
        """
        Parse a Child element within a ToolChestItem.

        Args:
            elem: Child XML element

        Returns:
            Dictionary with child item data
        """
        try:
            return {
                "type": elem.findtext("Type", ""),
                "raw_hex": elem.findtext("Raw", ""),
                "raw": self.decode_hex_zlib(elem.findtext("Raw", ""))
                if self.is_hex_zlib(elem.findtext("Raw", ""))
                else elem.findtext("Raw", ""),
                "x": float(elem.findtext("X", "0")),
                "y": float(elem.findtext("Y", "0")),
                "index": int(elem.findtext("Index", "0")),
            }
        except Exception as e:
            logger.debug(f"Error parsing child item: {e}")
            return None

    @staticmethod
    def _extract_subject_from_raw(raw_content: str) -> str | None:
        """
        Extract subject name from decoded Raw field content.

        The Raw field contains a PDF dictionary-like structure with the Subject
        in the format: /Subj(Subject Name Here)

        Args:
            raw_content: Decoded Raw field content

        Returns:
            Extracted subject name, or None if not found

        Example:
            >>> BTXReferenceLoader._extract_subject_from_raw(
            ...     '<</IC[...]/Subj(INFRAS - Edge Switch)/TempNameID/...'
            ... )
            'INFRAS - Edge Switch'
        """
        if not raw_content:
            return None

        # Pattern to match /Subj(...) or Subj(...)
        # The subject is in parentheses after /Subj or Subj
        # Handle nested parentheses by matching balanced parens
        patterns = [
            r"/Subj\(([^)]+)\)",  # /Subj(Subject Name)
            r"Subj\(([^)]+)\)",   # Subj(Subject Name)
            r"/Subject\(([^)]+)\)",  # /Subject(Subject Name)
        ]

        for pattern in patterns:
            match = re.search(pattern, raw_content)
            if match:
                subject = match.group(1).strip()
                if subject:
                    return subject

        logger.debug(f"No subject found in raw content: {raw_content[:100]}...")
        return None

    def _extract_category_from_filename(self, filename: str) -> str:
        """
        Extract category name from BTX filename.

        BTX files follow naming convention: "CDS Bluebeam <Category> [date].btx"

        Args:
            filename: BTX filename

        Returns:
            Category name extracted from filename

        Example:
            >>> loader._extract_category_from_filename("CDS Bluebeam Access Points [01-01-2026].btx")
            'Access Points'
        """
        # Remove "CDS Bluebeam " prefix and date suffix
        name = filename.replace("CDS Bluebeam ", "").replace(".btx", "")

        # Remove date pattern [MM-DD-YYYY] or [DD-MM-YYYY]
        name = re.sub(r"\s*\[[\d-]+\]\s*$", "", name)

        return name.strip()

    def load_toolchest(self) -> None:
        """
        Load all BTX files from toolchest directories.

        Loads bid icons from toolchest/bidTools/ and
        deployment icons from toolchest/deploymentTools/.

        Raises:
            FileNotFoundError: If toolchest directory doesn't exist
        """
        if not self.toolchest_dir.exists():
            raise FileNotFoundError(f"Toolchest directory not found: {self.toolchest_dir}")

        # Clear existing data
        self.bid_icons.clear()
        self.deployment_icons.clear()

        # Load bid icons
        bid_dir = self.toolchest_dir / "bidTools"
        if bid_dir.exists():
            self._load_btx_directory(bid_dir, "bid")
        else:
            logger.warning(f"Bid tools directory not found: {bid_dir}")

        # Load deployment icons
        deployment_dir = self.toolchest_dir / "deploymentTools"
        if deployment_dir.exists():
            self._load_btx_directory(deployment_dir, "deployment")
        else:
            logger.warning(f"Deployment tools directory not found: {deployment_dir}")

        self._loaded = True
        logger.info(
            f"Loaded {len(self.bid_icons)} bid icons, "
            f"{len(self.deployment_icons)} deployment icons"
        )

    def _load_btx_directory(self, directory: Path, icon_type: str) -> None:
        """
        Load all BTX files from a directory.

        Args:
            directory: Directory containing BTX files
            icon_type: Either "bid" or "deployment"
        """
        target_dict = self.bid_icons if icon_type == "bid" else self.deployment_icons

        btx_files = list(directory.glob("*.btx"))
        logger.debug(f"Found {len(btx_files)} BTX files in {directory}")

        for btx_path in btx_files:
            try:
                category = self._extract_category_from_filename(btx_path.name)
                items = self._parse_btx_file(btx_path)

                for item in items:
                    # Extract subject from Raw field
                    subject = self._extract_subject_from_raw(item.get("raw", ""))

                    if not subject:
                        logger.debug(
                            f"No subject found for item {item.get('name')} in {btx_path.name}"
                        )
                        continue

                    # Skip if subject already exists (avoid duplicates)
                    if subject in target_dict:
                        logger.debug(f"Duplicate subject '{subject}' in {btx_path.name}")
                        continue

                    # Create IconData object
                    icon_data = IconData(
                        subject=subject,
                        category=category,
                        visual_data=None,  # Store raw_hex for later if needed
                        metadata={
                            "name": item.get("name", ""),
                            "type": item.get("type", ""),
                            "raw_hex": item.get("raw_hex", ""),
                            "x": item.get("x", 0),
                            "y": item.get("y", 0),
                            "index": item.get("index", 0),
                            "resources": item.get("resources", []),
                            "source_file": btx_path.name,
                        },
                    )

                    target_dict[subject] = icon_data
                    logger.debug(f"Loaded {icon_type} icon: {subject}")

            except Exception as e:
                logger.error(f"Error loading BTX file {btx_path}: {e}")
                continue

    def get_icon_data(self, subject: str, icon_type: str = "deployment") -> IconData | None:
        """
        Get icon visual data for given subject.

        Args:
            subject: Icon subject name
            icon_type: "bid" or "deployment"

        Returns:
            IconData object or None if not found
        """
        icons = self.deployment_icons if icon_type == "deployment" else self.bid_icons
        return icons.get(subject)

    def get_bid_icon_count(self) -> int:
        """
        Get the number of loaded bid icons.

        Returns:
            Number of bid icons
        """
        return len(self.bid_icons)

    def get_deployment_icon_count(self) -> int:
        """
        Get the number of loaded deployment icons.

        Returns:
            Number of deployment icons
        """
        return len(self.deployment_icons)

    def get_all_subjects(self) -> list[str]:
        """
        Get all loaded subject names (bid and deployment combined).

        Returns:
            Sorted list of all subject names
        """
        all_subjects = set(self.bid_icons.keys()) | set(self.deployment_icons.keys())
        return sorted(all_subjects)

    def get_bid_subjects(self) -> list[str]:
        """
        Get all loaded bid subject names.

        Returns:
            Sorted list of bid subject names
        """
        return sorted(self.bid_icons.keys())

    def get_deployment_subjects(self) -> list[str]:
        """
        Get all loaded deployment subject names.

        Returns:
            Sorted list of deployment subject names
        """
        return sorted(self.deployment_icons.keys())

    def is_loaded(self) -> bool:
        """
        Check if toolchest has been loaded.

        Returns:
            True if load_toolchest() has been called successfully
        """
        return self._loaded
