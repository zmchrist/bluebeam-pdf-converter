"""Icon Tuner API endpoints."""

import base64
import io
import logging
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, Response
from PIL import Image as PILImage
from pypdf import PdfWriter

from app.config import settings
from app.models.tuner import (
    ApplyToAllRequest,
    ApplyToAllResponse,
    CategoryInfo,
    GearImageInfo,
    IconConfigCreateRequest,
    IconConfigResponse,
    IconConfigUpdateRequest,
)
from app.services.icon_config import (
    CATEGORY_DEFAULTS,
    ICON_CATEGORIES,
    get_icon_config,
)
from app.services.icon_override_store import IconOverrideStore
from app.services.icon_renderer import IconRenderer

logger = logging.getLogger(__name__)
router = APIRouter()

# Lazily initialized singletons
_store: IconOverrideStore | None = None
_gear_image_cache: list[GearImageInfo] | None = None


def _get_store() -> IconOverrideStore:
    global _store
    if _store is None:
        _store = IconOverrideStore(settings.icon_overrides_file)
    return _store


def _decode_subject(subject: str) -> str:
    """URL-decode a subject parameter."""
    return unquote(subject)


# ─── Icon CRUD ───────────────────────────────────────────────────────


@router.get("/icons", response_model=list[IconConfigResponse])
async def list_icons():
    """List all icons with merged configs (Python + JSON overrides)."""
    store = _get_store()
    configs = store.get_all_configs()
    return [IconConfigResponse(**c) for c in configs]


@router.post("/icons/apply-to-all", response_model=ApplyToAllResponse)
async def apply_to_all(request: ApplyToAllRequest):
    """Apply field group settings from one icon to multiple icons."""
    store = _get_store()

    # Validate source icon exists and get its category
    source_config = store.get_icon(request.source_subject)
    if not source_config:
        py_config = get_icon_config(request.source_subject)
        if not py_config:
            raise HTTPException(
                status_code=404,
                detail=f"Source icon not found: {request.source_subject}",
            )
        source_category = py_config.get("category", "Misc")
    else:
        source_category = source_config.get("category", "Misc")

    # Get all icon configs to determine targets
    all_configs = store.get_all_configs()

    if request.scope == "category":
        targets = [
            c["subject"]
            for c in all_configs
            if c.get("category") == source_category
            and c["subject"] != request.source_subject
        ]
    else:
        targets = [
            c["subject"]
            for c in all_configs
            if c["subject"] != request.source_subject
        ]

    # Extract only the relevant field group's fields
    if request.field_group == "circle":
        updates = request.model_dump(
            include={"circle_color", "circle_border_width", "circle_border_color"},
            exclude_none=True,
        )
    elif request.field_group == "id_box":
        updates = request.model_dump(
            include={
                "id_box_height",
                "id_box_width_ratio",
                "id_box_border_width",
                "id_font_size",
            },
            exclude_none=True,
        )
    elif request.field_group == "gear_image":
        updates = request.model_dump(
            include={"img_scale_ratio", "img_x_offset", "img_y_offset"},
            exclude_none=True,
        )
    elif request.field_group == "brand_text":
        updates = request.model_dump(
            include={
                "brand_text",
                "brand_font_size",
                "brand_x_offset",
                "brand_y_offset",
                "text_color",
            },
            exclude_none=True,
        )
    else:  # model_text
        updates = request.model_dump(
            include={
                "model_font_size",
                "model_x_offset",
                "model_y_offset",
                "model_uppercase",
                "model_text_override",
            },
            exclude_none=True,
        )

    if not updates:
        return ApplyToAllResponse(
            affected_count=0,
            field_group=request.field_group,
            scope=request.scope,
        )

    count = store.apply_to_multiple(targets, updates)
    return ApplyToAllResponse(
        affected_count=count,
        field_group=request.field_group,
        scope=request.scope,
    )


@router.get("/icons/{subject:path}", response_model=IconConfigResponse)
async def get_icon(subject: str):
    """Get a single icon's full config."""
    subject = _decode_subject(subject)
    store = _get_store()

    # Check JSON override first
    json_config = store.get_icon(subject)
    if json_config:
        json_config["subject"] = subject
        json_config["source"] = "json_override"
        return IconConfigResponse(**json_config)

    # Fall back to Python config
    config = get_icon_config(subject)
    if not config:
        raise HTTPException(status_code=404, detail=f"Icon not found: {subject}")

    config["subject"] = subject
    config["source"] = "python"
    config.setdefault("img_x_offset", 0.0)
    config.setdefault("img_y_offset", 0.0)
    config.setdefault("model_text_override", None)
    config.setdefault("model_uppercase", False)
    config.setdefault("no_image", False)
    config.setdefault("layer_order", ["gear_image", "brand_text", "model_text"])
    return IconConfigResponse(**config)


@router.put("/icons/{subject:path}", response_model=IconConfigResponse)
async def save_icon(subject: str, update: IconConfigUpdateRequest):
    """Save/update an icon config to JSON."""
    subject = _decode_subject(subject)
    store = _get_store()

    # Build complete config from base + updates
    partial = update.model_dump(exclude_none=True)
    full_config = store.build_full_config(subject, partial)

    # Remove transient fields before saving
    save_config = {k: v for k, v in full_config.items() if k not in ("subject", "source")}
    store.set_icon(subject, save_config)

    full_config["source"] = "json_override"
    return IconConfigResponse(**full_config)


@router.post("/icons", response_model=IconConfigResponse, status_code=201)
async def create_icon(request: IconConfigCreateRequest):
    """Create a new icon config."""
    store = _get_store()
    subject = request.subject

    # Check it doesn't already exist
    existing = store.get_icon(subject)
    if existing or subject in ICON_CATEGORIES:
        raise HTTPException(status_code=409, detail=f"Icon already exists: {subject}")

    if request.clone_from:
        # Clone from existing icon
        base = get_icon_config(request.clone_from)
        if not base:
            clone_config = store.get_icon(request.clone_from)
            if not clone_config:
                raise HTTPException(
                    status_code=404,
                    detail=f"Clone source not found: {request.clone_from}",
                )
            base = clone_config.copy()
        base["category"] = request.category
    else:
        # Start from category defaults
        defaults = CATEGORY_DEFAULTS.get(request.category)
        if not defaults:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown category: {request.category}",
            )
        base = defaults.copy()
        base["category"] = request.category
        base["image_path"] = None

    # Set defaults
    base.setdefault("img_x_offset", 0.0)
    base.setdefault("img_y_offset", 0.0)
    base.setdefault("model_text_override", None)
    base.setdefault("model_uppercase", False)
    base.setdefault("no_image", False)
    base.setdefault("layer_order", ["gear_image", "brand_text", "model_text"])

    # Save (without transient fields)
    save_config = {k: v for k, v in base.items() if k not in ("subject", "source")}
    store.set_icon(subject, save_config)

    base["subject"] = subject
    base["source"] = "custom"
    return IconConfigResponse(**base)


@router.delete("/icons/{subject:path}", status_code=204)
async def delete_icon(subject: str):
    """Remove JSON override (reverts to Python defaults)."""
    subject = _decode_subject(subject)
    store = _get_store()
    store.delete_icon(subject)


# ─── Gear Images ─────────────────────────────────────────────────────


def _load_gear_images() -> list[GearImageInfo]:
    """Scan gear icons directory and create thumbnail cache."""
    global _gear_image_cache
    if _gear_image_cache is not None:
        return _gear_image_cache

    images: list[GearImageInfo] = []
    gear_dir = settings.gear_icons_dir

    if not gear_dir.exists():
        logger.warning(f"Gear icons directory not found: {gear_dir}")
        return images

    for category_dir in sorted(gear_dir.iterdir()):
        if not category_dir.is_dir():
            continue
        category = category_dir.name
        for png_file in sorted(category_dir.glob("*.png")):
            try:
                with PILImage.open(png_file) as img:
                    img.thumbnail((64, 64))
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    thumbnail_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

                images.append(
                    GearImageInfo(
                        filename=png_file.name,
                        category=category,
                        path=f"{category}/{png_file.name}",
                        thumbnail=thumbnail_b64,
                    )
                )
            except (OSError, ValueError) as e:
                logger.warning(f"Failed to process gear image {png_file}: {e}")

    _gear_image_cache = images
    return images


@router.get("/gear-images", response_model=list[GearImageInfo])
async def list_gear_images(category: str | None = None):
    """List gear PNGs with base64 thumbnails."""
    images = _load_gear_images()
    if category:
        images = [img for img in images if img.category == category]
    return images


@router.get("/gear-image-file/{image_path:path}")
async def get_gear_image_file(image_path: str):
    """Serve a full-resolution gear image PNG."""
    image_path = unquote(image_path)
    full_path = settings.gear_icons_dir / image_path
    # Security: validate path doesn't escape gear_icons_dir BEFORE checking existence
    try:
        resolved = full_path.resolve()
        resolved.relative_to(settings.gear_icons_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=404, detail="Image not found")
    if not resolved.exists() or not resolved.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    with open(resolved, "rb") as f:
        return Response(content=f.read(), media_type="image/png")


# ─── Categories ──────────────────────────────────────────────────────


@router.get("/categories", response_model=list[CategoryInfo])
async def list_categories():
    """List categories with defaults and icon counts."""
    store = _get_store()
    all_configs = store.get_all_configs()

    # Count icons per category
    counts: dict[str, int] = {}
    for config in all_configs:
        cat = config.get("category", "Unknown")
        counts[cat] = counts.get(cat, 0) + 1

    categories = []
    for name, defaults in CATEGORY_DEFAULTS.items():
        categories.append(
            CategoryInfo(
                name=name,
                icon_count=counts.get(name, 0),
                defaults=defaults,
            )
        )

    return categories


# ─── Render Test ─────────────────────────────────────────────────────


@router.post("/render-pdf")
async def render_test_pdf(
    subject: str,
    id_label: str = "j100",
    size: int = 400,
):
    """Render icon to PDF then convert to PNG for preview."""
    import fitz  # PyMuPDF

    if size < 50 or size > 2000:
        raise HTTPException(status_code=400, detail="Size must be between 50 and 2000")

    store = _get_store()

    # Get config (JSON override or Python)
    json_config = store.get_icon(subject)
    config = json_config if json_config else get_icon_config(subject)
    if not config:
        raise HTTPException(status_code=404, detail=f"Icon not found: {subject}")

    # Check for image
    image_path = config.get("image_path")
    if not image_path or config.get("no_image"):
        raise HTTPException(status_code=400, detail="Icon has no image to render")

    full_image_path = settings.gear_icons_dir / image_path
    # Security: validate path doesn't escape gear_icons_dir
    try:
        resolved_image = full_image_path.resolve()
        resolved_image.relative_to(settings.gear_icons_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid image path")
    if not resolved_image.exists():
        raise HTTPException(status_code=400, detail=f"Image not found: {image_path}")

    # Create PDF with icon
    rect = [0, 0, 25, 30]
    renderer = IconRenderer(settings.gear_icons_dir)
    writer = PdfWriter()
    writer.add_blank_page(width=25, height=30)

    ap_ref = renderer.render_icon(writer, subject, rect, id_label)
    if not ap_ref:
        raise HTTPException(status_code=500, detail="Failed to render icon")

    # Write PDF to bytes
    pdf_buf = io.BytesIO()
    writer.write(pdf_buf)
    pdf_bytes = pdf_buf.getvalue()

    # Convert to PNG with PyMuPDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    zoom = size / 30  # Scale to requested pixel size
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    png_bytes = pix.tobytes("png")
    doc.close()

    return Response(content=png_bytes, media_type="image/png")
