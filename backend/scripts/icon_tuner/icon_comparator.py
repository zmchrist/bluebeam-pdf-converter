"""
Icon comparison module.

Renders generated icons to PIL Images and computes pixel-level
similarity scores against reference icon crops.
"""

import io
import logging
from unittest.mock import patch

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    TextStringObject,
)

from app.services.icon_config import get_icon_config, GEAR_ICONS_DIR
from app.services.icon_renderer import IconRenderer

logger = logging.getLogger(__name__)

# Shared renderer instance
_renderer: IconRenderer | None = None


def _get_renderer() -> IconRenderer:
    """Get or create shared IconRenderer instance."""
    global _renderer
    if _renderer is None:
        _renderer = IconRenderer(GEAR_ICONS_DIR)
    return _renderer


def render_icon_to_image(
    subject: str,
    config_override: dict | None = None,
    rect: list[float] | None = None,
    id_label: str = "test",
    dpi: int = 300,
) -> Image.Image | None:
    """
    Render a generated icon to a PIL Image.

    Creates a PDF with the icon annotation, renders via PyMuPDF,
    and crops to the annotation area.

    Args:
        subject: Deployment subject name
        config_override: Optional parameter overrides for get_icon_config
        rect: Annotation rect [x1, y1, x2, y2], defaults to standard test rect
        id_label: ID label text for the icon
        dpi: Rendering resolution

    Returns:
        Cropped PIL Image of the rendered icon, or None on failure
    """
    if rect is None:
        rect = [100.0, 700.0, 125.0, 730.0]

    renderer = _get_renderer()

    # Get base config for annotation colors
    base_config = get_icon_config(subject)
    if not base_config:
        logger.warning(f"No config for subject: {subject}")
        return None

    try:
        if config_override:
            original_get_config = get_icon_config

            def mock_get_config(subj: str) -> dict:
                config = original_get_config(subj)
                if subj == subject and config:
                    config.update(config_override)
                return config

            with patch("app.services.icon_renderer.get_icon_config", side_effect=mock_get_config):
                return _render_and_capture(renderer, subject, rect, id_label, base_config, dpi)
        else:
            return _render_and_capture(renderer, subject, rect, id_label, base_config, dpi)

    except Exception:
        logger.exception(f"Failed to render icon: {subject}")
        return None


def _render_and_capture(
    renderer: IconRenderer,
    subject: str,
    rect: list[float],
    id_label: str,
    config: dict,
    dpi: int,
) -> Image.Image | None:
    """Internal: render icon to PDF, capture as image, crop to rect."""
    writer = PdfWriter()
    writer.add_blank_page(612, 792)
    page = writer.pages[0]

    appearance_ref = renderer.render_icon(writer, subject, rect, id_label=id_label)
    if not appearance_ref:
        return None

    # Create annotation (mirrors test_icon_render.py)
    annot = DictionaryObject()
    annot[NameObject("/Type")] = NameObject("/Annot")
    annot[NameObject("/Subtype")] = NameObject("/Circle")
    annot[NameObject("/Rect")] = ArrayObject([
        FloatObject(rect[0]),
        FloatObject(rect[1]),
        FloatObject(rect[2]),
        FloatObject(rect[3]),
    ])
    annot[NameObject("/Subj")] = TextStringObject(subject)
    annot[NameObject("/F")] = NumberObject(4)

    circle_color = config.get("circle_color", (0.5, 0.5, 0.5))
    annot[NameObject("/IC")] = ArrayObject([
        FloatObject(circle_color[0]),
        FloatObject(circle_color[1]),
        FloatObject(circle_color[2]),
    ])

    ap = DictionaryObject()
    ap[NameObject("/N")] = appearance_ref
    annot[NameObject("/AP")] = ap

    page[NameObject("/Annots")] = ArrayObject([annot])

    # Write to buffer
    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)

    # Render with PyMuPDF
    doc = fitz.open(stream=buf.read(), filetype="pdf")
    fitz_page = doc[0]
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = fitz_page.get_pixmap(matrix=mat)
    full_img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()

    # Crop to annotation rect (PDF y-axis is bottom-up, image is top-down)
    page_height = 792.0
    x1, y1, x2, y2 = rect

    # Convert PDF coords to image coords
    img_x1 = int(x1 * zoom)
    img_y1 = int((page_height - y2) * zoom)  # PDF y2 (top) -> image top
    img_x2 = int(x2 * zoom)
    img_y2 = int((page_height - y1) * zoom)  # PDF y1 (bottom) -> image bottom

    # Add padding to capture ID box above and model text below
    padding_y = int(6 * zoom)  # Extra padding for ID box + model text
    padding_x = int(2 * zoom)
    img_x1 = max(0, img_x1 - padding_x)
    img_y1 = max(0, img_y1 - padding_y)
    img_x2 = min(full_img.width, img_x2 + padding_x)
    img_y2 = min(full_img.height, img_y2 + padding_y)

    cropped = full_img.crop((img_x1, img_y1, img_x2, img_y2))
    return cropped


def _normalize_background(img: Image.Image, bg_color: tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
    """
    Normalize image background to a consistent color.

    Replaces near-white and near-gray backgrounds with the specified color
    to ensure fair comparison between reference (gray bg) and generated (white bg).

    Args:
        img: Input image
        bg_color: Target background color (default white)

    Returns:
        Image with normalized background
    """
    result = img.convert("RGB").copy()
    pixels = result.load()
    w, h = result.size

    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            # Replace near-white and light-gray pixels (background)
            max_c = max(r, g, b)
            min_c = min(r, g, b)
            saturation = max_c - min_c
            if lum > 200 and saturation < 30:
                pixels[x, y] = bg_color

    return result


def _trim_to_content(img: Image.Image, threshold: int = 240) -> Image.Image:
    """
    Trim image to content bounding box, removing background borders.

    Args:
        img: Input image
        threshold: Luminance threshold for background detection

    Returns:
        Trimmed image
    """
    gray = img.convert("L")
    w, h = gray.size
    pixels = gray.load()

    min_x, min_y = w, h
    max_x, max_y = 0, 0

    for y in range(h):
        for x in range(w):
            if pixels[x, y] < threshold:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if max_x <= min_x or max_y <= min_y:
        return img

    # Add small padding
    pad = 2
    min_x = max(0, min_x - pad)
    min_y = max(0, min_y - pad)
    max_x = min(w, max_x + pad)
    max_y = min(h, max_y + pad)

    return img.crop((min_x, min_y, max_x, max_y))


def compute_nmae(img1: Image.Image, img2: Image.Image) -> float:
    """
    Compute Normalized Mean Absolute Error between two images.

    Normalizes backgrounds and trims to content before comparing.

    Args:
        img1: First image
        img2: Second image

    Returns:
        NMAE score (0 = identical, 1 = maximum difference)
    """
    # Normalize backgrounds to white and trim to content
    n1 = _trim_to_content(_normalize_background(img1))
    n2 = _trim_to_content(_normalize_background(img2))

    # Resize to same dimensions
    target_w = max(n1.width, n2.width, 64)
    target_h = max(n1.height, n2.height, 64)

    r1 = n1.resize((target_w, target_h), Image.LANCZOS)
    r2 = n2.resize((target_w, target_h), Image.LANCZOS)

    p1 = r1.convert("RGB").tobytes()
    p2 = r2.convert("RGB").tobytes()

    total_diff = 0
    for a, b in zip(p1, p2):
        total_diff += abs(a - b)

    num_values = len(p1)
    if num_values == 0:
        return 0.0

    return total_diff / (255.0 * num_values)


def compute_histogram_similarity(img1: Image.Image, img2: Image.Image) -> float:
    """
    Compute color histogram intersection similarity.

    Normalizes backgrounds before comparing histograms.

    Args:
        img1: First image
        img2: Second image

    Returns:
        Similarity score (0 = no overlap, 1 = identical histograms)
    """
    # Normalize and trim before histogram comparison
    n1 = _trim_to_content(_normalize_background(img1))
    n2 = _trim_to_content(_normalize_background(img2))

    r1 = n1.resize((64, 64), Image.LANCZOS).convert("RGB")
    r2 = n2.resize((64, 64), Image.LANCZOS).convert("RGB")

    h1 = r1.histogram()
    h2 = r2.histogram()

    # Histogram intersection
    intersection = sum(min(a, b) for a, b in zip(h1, h2))
    total = sum(h1)

    if total == 0:
        return 0.0

    return intersection / total


def compute_region_similarity(
    img1: Image.Image,
    img2: Image.Image,
) -> dict[str, float]:
    """
    Compare specific regions of two icon images.

    Regions are defined as percentages of image height:
    - id_box: top 15%
    - circle: 10-95%
    - brand_zone: 15-35%
    - image_zone: 30-70%
    - model_zone: 70-90%

    Args:
        img1: First image (reference)
        img2: Second image (generated)

    Returns:
        Dict of region name -> similarity score (0-1)
    """
    # Normalize and trim before region comparison
    n1 = _trim_to_content(_normalize_background(img1))
    n2 = _trim_to_content(_normalize_background(img2))

    target_w = max(n1.width, n2.width, 64)
    target_h = max(n1.height, n2.height, 64)

    r1 = n1.resize((target_w, target_h), Image.LANCZOS)
    r2 = n2.resize((target_w, target_h), Image.LANCZOS)

    regions = {
        "id_box": (0.0, 0.0, 1.0, 0.15),
        "circle": (0.0, 0.10, 1.0, 0.95),
        "brand_zone": (0.1, 0.15, 0.9, 0.35),
        "image_zone": (0.1, 0.30, 0.9, 0.70),
        "model_zone": (0.1, 0.70, 0.9, 0.90),
    }

    scores = {}
    for name, (rx1, ry1, rx2, ry2) in regions.items():
        crop_box = (
            int(rx1 * target_w),
            int(ry1 * target_h),
            int(rx2 * target_w),
            int(ry2 * target_h),
        )
        c1 = r1.crop(crop_box)
        c2 = r2.crop(crop_box)
        nmae = compute_nmae(c1, c2)
        scores[name] = 1.0 - nmae

    return scores


def compute_similarity(
    ref_img: Image.Image,
    gen_img: Image.Image,
) -> dict:
    """
    Compute combined similarity metrics between reference and generated icons.

    Args:
        ref_img: Reference icon image
        gen_img: Generated icon image

    Returns:
        Dict with 'nmae', 'histogram', 'region_scores', 'region_avg', 'combined' keys
    """
    nmae = compute_nmae(ref_img, gen_img)
    histogram = compute_histogram_similarity(ref_img, gen_img)
    region_scores = compute_region_similarity(ref_img, gen_img)

    region_avg = sum(region_scores.values()) / max(len(region_scores), 1)

    combined = 0.3 * (1.0 - nmae) + 0.2 * histogram + 0.5 * region_avg

    return {
        "nmae": nmae,
        "histogram": histogram,
        "region_scores": region_scores,
        "region_avg": region_avg,
        "combined": combined,
    }


def create_comparison_image(
    ref_img: Image.Image,
    gen_img: Image.Image,
    subject: str,
    scores: dict,
) -> Image.Image:
    """
    Create side-by-side comparison image with reference, generated, and diff.

    Args:
        ref_img: Reference icon image
        gen_img: Generated icon image
        subject: Icon subject name
        scores: Similarity scores dict from compute_similarity()

    Returns:
        PIL Image with side-by-side comparison
    """
    # Resize both to same height
    target_h = max(ref_img.height, gen_img.height, 150)
    ref_w = int(ref_img.width * target_h / max(ref_img.height, 1))
    gen_w = int(gen_img.width * target_h / max(gen_img.height, 1))

    ref_resized = ref_img.resize((ref_w, target_h), Image.LANCZOS)
    gen_resized = gen_img.resize((gen_w, target_h), Image.LANCZOS)

    # Create diff image
    diff_w = max(ref_w, gen_w)
    diff_ref = ref_img.resize((diff_w, target_h), Image.LANCZOS).convert("RGB")
    diff_gen = gen_img.resize((diff_w, target_h), Image.LANCZOS).convert("RGB")

    diff_img = Image.new("RGB", (diff_w, target_h))
    ref_px = diff_ref.load()
    gen_px = diff_gen.load()
    diff_px = diff_img.load()

    for y in range(target_h):
        for x in range(diff_w):
            r = abs(ref_px[x, y][0] - gen_px[x, y][0])
            g = abs(ref_px[x, y][1] - gen_px[x, y][1])
            b = abs(ref_px[x, y][2] - gen_px[x, y][2])
            # Amplify differences
            diff_px[x, y] = (min(255, r * 3), min(255, g * 3), min(255, b * 3))

    # Layout: header + [reference | generated | diff]
    header_height = 50
    gap = 10
    total_w = ref_w + gen_w + diff_w + gap * 2
    total_h = target_h + header_height

    canvas = Image.new("RGB", (total_w, total_h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except (OSError, IOError):
        font = ImageFont.load_default()
        title_font = font

    # Title
    combined = scores.get("combined", 0)
    draw.text(
        (5, 5),
        f"{subject}  |  Combined: {combined:.3f}  NMAE: {scores.get('nmae', 0):.3f}  "
        f"Histogram: {scores.get('histogram', 0):.3f}",
        fill="black",
        font=title_font,
    )

    # Labels
    x_offset = 0
    draw.text((x_offset + 5, 30), "Reference", fill="blue", font=font)
    canvas.paste(ref_resized, (x_offset, header_height))
    x_offset += ref_w + gap

    draw.text((x_offset + 5, 30), "Generated", fill="green", font=font)
    canvas.paste(gen_resized, (x_offset, header_height))
    x_offset += gen_w + gap

    draw.text((x_offset + 5, 30), "Diff (3x)", fill="red", font=font)
    canvas.paste(diff_img, (x_offset, header_height))

    return canvas
