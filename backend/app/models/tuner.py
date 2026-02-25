"""Pydantic models for the Icon Tuner API."""

from typing import Literal

from pydantic import BaseModel


class IconConfigResponse(BaseModel):
    """Full icon configuration response."""

    subject: str
    category: str
    circle_color: tuple[float, float, float]
    circle_border_width: float
    circle_border_color: tuple[float, float, float]
    id_box_height: float
    id_box_width_ratio: float
    id_box_border_width: float
    id_font_size: float
    img_scale_ratio: float
    img_x_offset: float = 0.0
    img_y_offset: float = 0.0
    brand_text: str
    brand_font_size: float
    brand_y_offset: float
    brand_x_offset: float
    model_font_size: float
    model_y_offset: float
    model_x_offset: float
    model_text_override: str | None = None
    model_uppercase: bool = False
    font_name: str = "/Helvetica-Bold"
    text_color: tuple[float, float, float]
    id_text_color: tuple[float, float, float] | None = None
    no_image: bool = False
    image_path: str | None = None
    layer_order: list[str] = ["gear_image", "brand_text", "model_text"]
    source: str = "python"  # "python" | "json_override" | "custom"


class IconConfigUpdateRequest(BaseModel):
    """Partial update request - all fields optional."""

    category: str | None = None
    circle_color: tuple[float, float, float] | None = None
    circle_border_width: float | None = None
    circle_border_color: tuple[float, float, float] | None = None
    id_box_height: float | None = None
    id_box_width_ratio: float | None = None
    id_box_border_width: float | None = None
    id_font_size: float | None = None
    img_scale_ratio: float | None = None
    img_x_offset: float | None = None
    img_y_offset: float | None = None
    brand_text: str | None = None
    brand_font_size: float | None = None
    brand_y_offset: float | None = None
    brand_x_offset: float | None = None
    model_font_size: float | None = None
    model_y_offset: float | None = None
    model_x_offset: float | None = None
    model_text_override: str | None = None
    model_uppercase: bool | None = None
    font_name: str | None = None
    text_color: tuple[float, float, float] | None = None
    id_text_color: tuple[float, float, float] | None = None
    no_image: bool | None = None
    image_path: str | None = None
    layer_order: list[str] | None = None


class IconConfigCreateRequest(BaseModel):
    """Request to create a new icon config."""

    subject: str
    category: str
    clone_from: str | None = None  # Subject to clone config from


class GearImageInfo(BaseModel):
    """Info about a gear icon PNG."""

    filename: str
    category: str
    path: str
    thumbnail: str  # base64 encoded 64x64 thumbnail


class ApplyToAllRequest(BaseModel):
    """Request to apply field group settings to multiple icons."""

    field_group: Literal["circle", "id_box", "gear_image", "brand_text", "model_text"]
    scope: Literal["category", "all"]
    source_subject: str
    # Circle fields
    circle_color: tuple[float, float, float] | None = None
    circle_border_width: float | None = None
    circle_border_color: tuple[float, float, float] | None = None
    # ID Box fields
    id_box_height: float | None = None
    id_box_width_ratio: float | None = None
    id_box_border_width: float | None = None
    id_font_size: float | None = None
    # Gear Image fields
    img_scale_ratio: float | None = None
    img_x_offset: float | None = None
    img_y_offset: float | None = None
    # Brand Text fields
    brand_text: str | None = None
    brand_font_size: float | None = None
    brand_x_offset: float | None = None
    brand_y_offset: float | None = None
    text_color: tuple[float, float, float] | None = None
    # Model Text fields
    model_font_size: float | None = None
    model_x_offset: float | None = None
    model_y_offset: float | None = None
    model_uppercase: bool | None = None
    model_text_override: str | None = None


class ApplyToAllResponse(BaseModel):
    """Response from batch apply operation."""

    affected_count: int
    field_group: str
    scope: str


class CategoryInfo(BaseModel):
    """Category summary."""

    name: str
    icon_count: int
    defaults: dict
