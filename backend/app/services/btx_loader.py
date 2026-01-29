"""
BTX reference file loader service.

Loads icon visual data from toolchest BTX files.
"""

from pathlib import Path
from app.models.mapping import IconData


class BTXReferenceLoader:
    """Service for loading BTX toolset files and extracting icon data."""

    def __init__(self, toolchest_dir: Path):
        """
        Initialize BTX loader.

        Args:
            toolchest_dir: Path to toolchest directory
        """
        self.toolchest_dir = toolchest_dir
        self.bid_icons: dict[str, IconData] = {}
        self.deployment_icons: dict[str, IconData] = {}

    def load_toolchest(self):
        """
        Load all BTX files from toolchest directories.

        Loads bid icons from toolchest/bidTools/ and
        deployment icons from toolchest/deploymentTools/.
        """
        # TODO: Implement BTX loading
        # 1. Scan toolchest/bidTools/ for BTX files
        # 2. Scan toolchest/deploymentTools/ for BTX files
        # 3. Parse each BTX file (XML structure)
        # 4. Extract icon definitions
        # 5. Decompress zlib icon data
        # 6. Build icon dictionaries
        raise NotImplementedError("BTX loading not yet implemented")

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
