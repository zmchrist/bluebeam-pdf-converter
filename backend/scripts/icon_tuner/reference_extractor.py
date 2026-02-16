"""
Reference PDF icon extraction.

Renders reference deployment PDF pages to images and extracts
individual icon crops using threshold-based blob detection.
"""

import logging
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

from scripts.icon_tuner.region_config import REFERENCE_REGIONS, REFERENCE_PDF_DIR

logger = logging.getLogger(__name__)

# Cache extracted icons to avoid re-rendering
_icon_cache: dict[str, dict[str, Image.Image]] = {}


def render_pdf_page_to_image(pdf_path: Path, page_num: int = 0, dpi: int = 300) -> Image.Image:
    """
    Render a PDF page to a PIL Image using PyMuPDF.

    Args:
        pdf_path: Path to the PDF file
        page_num: Page number (0-indexed)
        dpi: Resolution for rendering

    Returns:
        PIL Image of the rendered page
    """
    doc = fitz.open(str(pdf_path))
    page = doc[page_num]
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return img


def detect_icon_regions(
    image: Image.Image,
    min_size: int = 40,
    merge_distance: int = 5,
    luminance_threshold: int = 200,
) -> list[tuple[int, int, int, int]]:
    """
    Detect icon bounding boxes using threshold-based blob detection.

    Finds connected regions of non-background pixels and computes
    bounding boxes around them.

    Args:
        image: Rendered PDF page as PIL Image
        min_size: Minimum dimension to keep a detected region
        merge_distance: Max pixel gap to merge adjacent regions
        luminance_threshold: Pixels darker than this are considered content

    Returns:
        List of (x1, y1, x2, y2) bounding boxes, sorted top-to-bottom, left-to-right
    """
    gray = image.convert("L")
    width, height = gray.size
    pixels = gray.load()

    # Find rows that contain dark pixels
    row_ranges: list[tuple[int, int, int, int]] = []  # (min_x, min_y, max_x, max_y)

    # Scan for dark pixel blobs using row-based approach
    visited = set()

    def flood_fill_bbox(start_x: int, start_y: int) -> tuple[int, int, int, int]:
        """BFS flood fill to find bounding box of a connected dark region."""
        stack = [(start_x, start_y)]
        min_x, min_y = start_x, start_y
        max_x, max_y = start_x, start_y

        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            if x < 0 or x >= width or y < 0 or y >= height:
                continue
            if pixels[x, y] >= luminance_threshold:
                continue

            visited.add((x, y))
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

            # Check neighbors (4-connected with skip for speed)
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                    if pixels[nx, ny] < luminance_threshold:
                        stack.append((nx, ny))

        return (min_x, min_y, max_x, max_y)

    # Scan with step for speed (don't need to check every pixel)
    step = 3
    for y in range(0, height, step):
        for x in range(0, width, step):
            if (x, y) not in visited and pixels[x, y] < luminance_threshold:
                bbox = flood_fill_bbox(x, y)
                bw = bbox[2] - bbox[0]
                bh = bbox[3] - bbox[1]
                if bw >= min_size and bh >= min_size:
                    row_ranges.append(bbox)

    # Merge overlapping/close bounding boxes
    merged = _merge_bboxes(row_ranges, merge_distance)

    # Filter by aspect ratio (icons are roughly square or slightly tall)
    filtered = []
    for bbox in merged:
        bw = bbox[2] - bbox[0]
        bh = bbox[3] - bbox[1]
        aspect = bw / max(bh, 1)
        if 0.3 <= aspect <= 2.5:
            filtered.append(bbox)

    # Add padding
    padding = 10
    padded = []
    for x1, y1, x2, y2 in filtered:
        padded.append((
            max(0, x1 - padding),
            max(0, y1 - padding),
            min(width, x2 + padding),
            min(height, y2 + padding),
        ))

    # Sort: group by rows (similar y), then left-to-right within row
    return _sort_regions(padded)


def _merge_bboxes(
    bboxes: list[tuple[int, int, int, int]],
    gap: int,
) -> list[tuple[int, int, int, int]]:
    """Merge bounding boxes that overlap or are within gap pixels of each other."""
    if not bboxes:
        return []

    merged = list(bboxes)
    changed = True

    while changed:
        changed = False
        new_merged = []
        used = set()

        for i in range(len(merged)):
            if i in used:
                continue
            x1, y1, x2, y2 = merged[i]

            for j in range(i + 1, len(merged)):
                if j in used:
                    continue
                ox1, oy1, ox2, oy2 = merged[j]

                # Check overlap with gap tolerance
                if (x1 - gap <= ox2 and x2 + gap >= ox1 and
                        y1 - gap <= oy2 and y2 + gap >= oy1):
                    x1 = min(x1, ox1)
                    y1 = min(y1, oy1)
                    x2 = max(x2, ox2)
                    y2 = max(y2, oy2)
                    used.add(j)
                    changed = True

            new_merged.append((x1, y1, x2, y2))
            used.add(i)

        merged = new_merged

    return merged


def _sort_regions(
    regions: list[tuple[int, int, int, int]],
) -> list[tuple[int, int, int, int]]:
    """Sort regions top-to-bottom (row grouping), then left-to-right within rows."""
    if not regions:
        return []

    # Sort by y first
    by_y = sorted(regions, key=lambda r: r[1])

    # Group into rows (regions with similar y-center are in the same row)
    rows: list[list[tuple[int, int, int, int]]] = []
    current_row: list[tuple[int, int, int, int]] = [by_y[0]]
    row_y_center = (by_y[0][1] + by_y[0][3]) / 2

    for region in by_y[1:]:
        center_y = (region[1] + region[3]) / 2
        height = region[3] - region[1]
        # If this region's center is within half-height of the row, same row
        if abs(center_y - row_y_center) < height * 0.5:
            current_row.append(region)
        else:
            rows.append(current_row)
            current_row = [region]
            row_y_center = center_y

    rows.append(current_row)

    # Sort each row left-to-right, then flatten
    result = []
    for row in rows:
        row.sort(key=lambda r: r[0])
        result.extend(row)

    return result


def extract_reference_icons(
    pdf_path: Path,
    dpi: int = 300,
) -> dict[str, Image.Image]:
    """
    Extract individual icon images from a reference PDF.

    Renders the PDF page, detects icon regions, and maps them
    to deployment subjects using the region_config ordering.

    Args:
        pdf_path: Path to reference PDF
        dpi: Resolution for rendering

    Returns:
        Dict mapping subject name -> cropped PIL Image
    """
    cache_key = str(pdf_path)
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]

    pdf_name = pdf_path.name
    if pdf_name not in REFERENCE_REGIONS:
        logger.warning(f"No region config for PDF: {pdf_name}")
        return {}

    entries = REFERENCE_REGIONS[pdf_name]
    subjects = [subject for subject, _ in entries]
    manual_crops = {subject: crop for subject, crop in entries if crop is not None}

    # Render page
    page_img = render_pdf_page_to_image(pdf_path, dpi=dpi)

    # Detect regions
    regions = detect_icon_regions(page_img)

    logger.info(f"{pdf_name}: detected {len(regions)} regions, expected {len(subjects)}")

    # Map detected regions to subjects
    icons: dict[str, Image.Image] = {}

    for i, subject in enumerate(subjects):
        if subject in manual_crops:
            # Use manual crop box
            crop_box = manual_crops[subject]
            icons[subject] = page_img.crop(crop_box)
        elif i < len(regions):
            # Use auto-detected region
            icons[subject] = page_img.crop(regions[i])
        else:
            logger.warning(
                f"{pdf_name}: no region for subject #{i} '{subject}' "
                f"(detected {len(regions)}, need {len(subjects)})"
            )

    _icon_cache[cache_key] = icons
    return icons


def extract_all_reference_icons(dpi: int = 300) -> dict[str, Image.Image]:
    """
    Extract icons from all reference PDFs.

    Returns:
        Dict mapping subject name -> cropped PIL Image
    """
    all_icons: dict[str, Image.Image] = {}

    for pdf_name in REFERENCE_REGIONS:
        pdf_path = REFERENCE_PDF_DIR / pdf_name
        if not pdf_path.exists():
            logger.warning(f"Reference PDF not found: {pdf_path}")
            continue

        icons = extract_reference_icons(pdf_path, dpi=dpi)
        all_icons.update(icons)

    return all_icons


def save_annotated_reference(
    pdf_path: Path,
    output_dir: Path,
    dpi: int = 300,
) -> Path:
    """
    Save annotated reference image with detected bounding boxes and labels.

    Useful for debugging region detection.

    Args:
        pdf_path: Path to reference PDF
        output_dir: Directory to save annotated image
        dpi: Resolution for rendering

    Returns:
        Path to saved annotated image
    """
    pdf_name = pdf_path.name
    entries = REFERENCE_REGIONS.get(pdf_name, [])
    subjects = [subject for subject, _ in entries]

    # Render page
    page_img = render_pdf_page_to_image(pdf_path, dpi=dpi)

    # Detect regions
    regions = detect_icon_regions(page_img)

    # Draw bounding boxes
    draw = ImageDraw.Draw(page_img)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except (OSError, IOError):
        font = ImageFont.load_default()

    for i, region in enumerate(regions):
        x1, y1, x2, y2 = region
        color = "red" if i < len(subjects) else "gray"
        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)

        label = f"#{i}"
        if i < len(subjects):
            label = f"#{i}: {subjects[i]}"

        draw.text((x1, max(0, y1 - 16)), label, fill=color, font=font)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"annotated_{pdf_name.replace('.pdf', '.png')}"
    page_img.save(output_path)

    return output_path
