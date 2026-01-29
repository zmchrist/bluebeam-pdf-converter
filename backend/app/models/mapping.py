"""Icon mapping data models."""

from pydantic import BaseModel


class MappingEntry(BaseModel):
    """Represents a single bid→deployment icon mapping entry."""

    bid_icon_subject: str
    deployment_icon_subject: str
    category: str


class IconMapping(BaseModel):
    """Represents the complete icon mapping configuration."""

    mappings: dict[str, str]  # {bid_subject: deployment_subject}
    categories: dict[str, str]  # {bid_subject: category}
    total_mappings: int


class IconData(BaseModel):
    """Represents icon visual data from BTX files."""

    subject: str
    category: str
    visual_data: bytes | None = None
    metadata: dict | None = None
