"""PDF annotation data models."""

from pydantic import BaseModel


class AnnotationCoordinates(BaseModel):
    """Represents annotation coordinates on PDF page."""

    x: float
    y: float
    width: float
    height: float
    page: int = 1


class Annotation(BaseModel):
    """Represents a PDF markup annotation (icon)."""

    subject: str  # Icon subject name (e.g., "AP_Bid", "Switch_48Port_Bid")
    coordinates: AnnotationCoordinates
    annotation_type: str  # Type of annotation (stamp, callout, etc.)
    raw_data: dict | None = None  # Raw annotation dictionary from PDF


class AnnotationMapping(BaseModel):
    """Represents a bid→deployment annotation mapping."""

    bid_subject: str
    deployment_subject: str
    coordinates: AnnotationCoordinates
    mapped: bool = False
    error: str | None = None
