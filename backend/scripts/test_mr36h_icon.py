"""
Test script to convert a single MR36H bid icon to deployment icon with proper visual appearance.

This script:
1. Finds ONE "Artist - Indoor Wi-Fi Access Point" annotation in BidMap.pdf
2. Replaces it with "AP - Cisco MR36H" that has a proper appearance stream
3. Saves the result for visual verification against accessPoints.pdf reference

The appearance stream includes:
- Blue circle background (navy blue)
- "CISCO" text header (white)
- Product image (MR36H.png from gearIcons)
- "MR36H" model text (white)
"""

import zlib
from pathlib import Path
from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    IndirectObject,
    NameObject,
    NumberObject,
    StreamObject,
    TextStringObject,
)

# Paths - use samples/icons/gearIcons (NOT toolchest)
PROJECT_ROOT = Path(__file__).parent.parent.parent
SAMPLE_PDF = PROJECT_ROOT / "samples" / "maps" / "BidMap.pdf"
GEAR_ICON = PROJECT_ROOT / "samples" / "icons" / "gearIcons" / "APs" / "AP - Cisco MR36H.png"
REFERENCE_PDF = PROJECT_ROOT / "samples" / "icons" / "deploymentIcons" / "accessPoints.pdf"
OUTPUT_PDF = PROJECT_ROOT / "samples" / "maps" / "test_mr36h_output.pdf"

# Target annotation
BID_SUBJECT = "Artist - Indoor Wi-Fi Access Point"
DEPLOYMENT_SUBJECT = "AP - Cisco MR36H"

# Visual settings - Navy blue to match reference (j100 icon in accessPoints.pdf)
# Reference specifies: RGB (0.22, 0.34, 0.65)
CIRCLE_COLOR_RGB = (0.22, 0.34, 0.65)
CIRCLE_BORDER_WIDTH = 0.5
CIRCLE_BORDER_COLOR = (0.0, 0.0, 0.0)  # Black border


def load_image_as_xobject(image_path: Path, bg_color: tuple[int, int, int] = None) -> tuple[bytes, int, int]:
    """
    Load a PNG image and prepare it for PDF embedding.

    Args:
        image_path: Path to the PNG image
        bg_color: Background color RGB (0-255) for transparent areas.
                  If None, uses the circle fill color.

    Returns:
        Tuple of (image_data, width, height)
    """
    # Default to circle fill color (converted from 0-1 to 0-255)
    if bg_color is None:
        bg_color = (
            int(CIRCLE_COLOR_RGB[0] * 255),
            int(CIRCLE_COLOR_RGB[1] * 255),
            int(CIRCLE_COLOR_RGB[2] * 255),
        )

    with Image.open(image_path) as img:
        # Convert to RGB with proper background color for transparency
        if img.mode in ('RGBA', 'P'):
            # Create background with the circle's blue color (not white!)
            background = Image.new('RGB', img.size, bg_color)
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[3])  # Use alpha as mask
            else:
                img = img.convert('RGBA')
                background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        width, height = img.size

        # Get raw RGB bytes
        raw_data = img.tobytes()

        return raw_data, width, height


def create_image_xobject(writer: PdfWriter, image_data: bytes, width: int, height: int) -> IndirectObject:
    """
    Create a PDF XObject Image from raw RGB data.
    """
    # Compress the image data
    compressed = zlib.compress(image_data)

    # Create the image XObject
    img_dict = DictionaryObject()
    img_dict[NameObject("/Type")] = NameObject("/XObject")
    img_dict[NameObject("/Subtype")] = NameObject("/Image")
    img_dict[NameObject("/Width")] = NumberObject(width)
    img_dict[NameObject("/Height")] = NumberObject(height)
    img_dict[NameObject("/ColorSpace")] = NameObject("/DeviceRGB")
    img_dict[NameObject("/BitsPerComponent")] = NumberObject(8)
    img_dict[NameObject("/Filter")] = NameObject("/FlateDecode")
    img_dict[NameObject("/Length")] = NumberObject(len(compressed))

    # Create stream object
    img_stream = StreamObject()
    img_stream.update(img_dict)
    img_stream._data = compressed

    return writer._add_object(img_stream)


def create_appearance_stream(
    writer: PdfWriter,
    rect: list[float],
    image_xobject_ref: IndirectObject,
    img_width: int,
    img_height: int,
    model_text: str = "MR36H",
    id_label: str = "j100",
) -> IndirectObject:
    """
    Create a PDF appearance stream that draws:
    1. ID box on top (white box with border, blue text)
    2. Blue filled circle (navy blue)
    3. Product image in center
    4. "CISCO" text at top (white, inside circle)
    5. Model number at bottom (white, inside circle)

    Uses ABSOLUTE page coordinates (like Bluebeam does) for the BBox and drawing.

    Args:
        writer: PdfWriter to add objects to
        rect: Annotation rect [x1, y1, x2, y2] in absolute page coordinates
        image_xobject_ref: Reference to the image XObject
        img_width: Image width in pixels
        img_height: Image height in pixels
        model_text: Model number to display
        id_label: ID label text for the top box (e.g., "j100")

    Returns:
        IndirectObject reference to the appearance stream
    """
    x1, y1, x2, y2 = rect
    width = x2 - x1
    height = y2 - y1

    # Layout: ID box on top, circle below
    # Reserve space for ID box at top
    id_box_height = 4.0  # Height of the ID label box

    # ID box position (centered at top, moved 2px down)
    cx = (x1 + x2) / 2
    id_box_width = width * 0.55  # Smaller - 55% of total width
    id_box_x1 = cx - id_box_width / 2
    id_box_x2 = cx + id_box_width / 2
    id_box_y1 = y2 - id_box_height - 1  # 1px down
    id_box_y2 = y2 - 1  # 1px down

    # Circle: positioned to overlap INTO the ID box by 2px
    # ID box (drawn on top) will cover the overlap, hiding any junction artifacts
    circle_top = id_box_y1 + 2  # Circle extends 2px into ID box area
    circle_bottom = y1
    circle_area_height = circle_top - circle_bottom

    # Circle radius - fit in available space
    radius = min(width, circle_area_height) / 2 - 0.3
    # Circle center - position so top of circle touches id_box_y1
    cy = circle_top - radius  # This ensures cy + radius = circle_top

    # Image dimensions (scaled to fit in circle with padding for text)
    # Larger image (was 0.55, now 0.70)
    img_scale = (radius * 0.70) / max(img_width, img_height)
    img_draw_width = img_width * img_scale
    img_draw_height = img_height * img_scale
    # Center image horizontally, position vertically in middle of circle
    img_x = cx - img_draw_width / 2
    img_y = cy - img_draw_height / 2

    # Build the content stream using ABSOLUTE coordinates
    r, g, b = CIRCLE_COLOR_RGB
    k = 0.5522847498  # Magic constant for circle Bezier approximation

    content_parts = []

    # === 1. Draw Circle FIRST (navy blue fill, black border) ===
    content_parts.append(f"{CIRCLE_BORDER_COLOR[0]:.4f} {CIRCLE_BORDER_COLOR[1]:.4f} {CIRCLE_BORDER_COLOR[2]:.4f} RG")
    content_parts.append(f"{CIRCLE_BORDER_WIDTH:.4f} w")
    content_parts.append(f"{r:.4f} {g:.4f} {b:.4f} rg")

    # Draw circle using 4 Bezier curves
    x0 = cx + radius
    y0 = cy
    content_parts.append(f"{x0:.3f} {y0:.3f} m")

    # Curve 1: Right to Top
    cp1x, cp1y = cx + radius, cy + radius * k
    cp2x, cp2y = cx + radius * k, cy + radius
    endx, endy = cx, cy + radius
    content_parts.append(f"{cp1x:.3f} {cp1y:.3f} {cp2x:.3f} {cp2y:.3f} {endx:.3f} {endy:.3f} c")

    # Curve 2: Top to Left
    cp1x, cp1y = cx - radius * k, cy + radius
    cp2x, cp2y = cx - radius, cy + radius * k
    endx, endy = cx - radius, cy
    content_parts.append(f"{cp1x:.3f} {cp1y:.3f} {cp2x:.3f} {cp2y:.3f} {endx:.3f} {endy:.3f} c")

    # Curve 3: Left to Bottom
    cp1x, cp1y = cx - radius, cy - radius * k
    cp2x, cp2y = cx - radius * k, cy - radius
    endx, endy = cx, cy - radius
    content_parts.append(f"{cp1x:.3f} {cp1y:.3f} {cp2x:.3f} {cp2y:.3f} {endx:.3f} {endy:.3f} c")

    # Curve 4: Bottom to Right
    cp1x, cp1y = cx + radius * k, cy - radius
    cp2x, cp2y = cx + radius, cy - radius * k
    endx, endy = cx + radius, cy
    content_parts.append(f"{cp1x:.3f} {cp1y:.3f} {cp2x:.3f} {cp2y:.3f} {endx:.3f} {endy:.3f} c")

    content_parts.append("h")
    content_parts.append("B")

    # === 2. Draw ID Box ON TOP of circle (white fill, heavier border) ===
    content_parts.append("q")  # Save state
    content_parts.append("1 1 1 rg")  # White fill
    content_parts.append("0 0 0 RG")  # Black stroke
    content_parts.append("0.6 w")  # Heavier border
    content_parts.append(f"{id_box_x1:.3f} {id_box_y1:.3f} {id_box_width:.3f} {id_box_height:.3f} re")
    content_parts.append("B")  # Fill and stroke
    content_parts.append("Q")  # Restore state

    # ID box text (blue, centered)
    content_parts.append("BT")
    content_parts.append(f"{r:.4f} {g:.4f} {b:.4f} rg")  # Blue text (same as circle)
    content_parts.append("/Helv 2.5 Tf")
    # Center text in box (approximate)
    id_text_width = len(id_label) * 1.2  # Rough estimate
    id_text_x = cx - id_text_width / 2
    id_text_y = id_box_y1 + 1.0  # Baseline offset from bottom of box
    content_parts.append(f"{id_text_x:.3f} {id_text_y:.3f} Td")
    content_parts.append(f"({id_label}) Tj")
    content_parts.append("ET")

    # === 3. Draw the gear image (centered in circle) ===
    content_parts.append("q")
    content_parts.append(f"{img_draw_width:.3f} 0 0 {img_draw_height:.3f} {img_x:.3f} {img_y:.3f} cm")
    content_parts.append("/Img Do")
    content_parts.append("Q")

    # Calculate font size to make text width match image width
    # Character width factors for Helvetica Bold (varies by letter)
    # C=0.72, I=0.28, S=0.67, O=0.78 -> CISCO avg ~0.55
    # M=0.83, R=0.72, 3=0.56, 6=0.56, H=0.72 -> MR36H avg ~0.68
    cisco_char_width = 0.55
    model_char_width = 0.52  # MR36H has narrower average

    cisco_chars = 5  # "CISCO"
    model_chars = len(model_text)

    # Font size so text width ≈ image width
    cisco_font_size = img_draw_width / (cisco_chars * cisco_char_width)
    model_font_size = img_draw_width / (model_chars * model_char_width)

    # Cap font sizes - slightly larger (was 1.75/1.45, now 1.9/1.6)
    cisco_font_size = min(cisco_font_size, 1.9)
    model_font_size = min(model_font_size, 1.6)

    # === 4. Draw "CISCO" text (white, near TOP of circle) ===
    content_parts.append("BT")
    content_parts.append("1 1 1 rg")  # White
    content_parts.append(f"/Helv {cisco_font_size:.2f} Tf")
    # Calculate text width and center precisely on image center (cx)
    cisco_text_width = cisco_chars * cisco_char_width * cisco_font_size
    text_x_cisco = cx - cisco_text_width / 2 - 0.2  # 0.2px left
    text_y_cisco = cy + radius - 3.0 - 1  # 1px down
    content_parts.append(f"{text_x_cisco:.3f} {text_y_cisco:.3f} Td")
    content_parts.append("(CISCO) Tj")
    content_parts.append("ET")

    # === 5. Draw model number (white, near BOTTOM of circle) ===
    content_parts.append("BT")
    content_parts.append("1 1 1 rg")
    content_parts.append(f"/Helv {model_font_size:.2f} Tf")
    # Calculate text width and center precisely on image center (cx)
    model_text_width = model_chars * model_char_width * model_font_size
    text_x_model = cx - model_text_width / 2 - 0.7  # 0.1px right (was -0.8, now -0.7)
    text_y_model = cy - radius + 1.5 + 1  # 1px up
    content_parts.append(f"{text_x_model:.3f} {text_y_model:.3f} Td")
    content_parts.append(f"({model_text}) Tj")
    content_parts.append("ET")

    content_string = "\n".join(content_parts)
    content_bytes = content_string.encode('latin-1')

    # Create the appearance stream with ABSOLUTE coordinate BBox (like Bluebeam)
    ap_stream = StreamObject()
    ap_stream[NameObject("/Type")] = NameObject("/XObject")
    ap_stream[NameObject("/Subtype")] = NameObject("/Form")
    ap_stream[NameObject("/FormType")] = NumberObject(1)
    ap_stream[NameObject("/BBox")] = ArrayObject([
        FloatObject(x1),
        FloatObject(y1),
        FloatObject(x2),
        FloatObject(y2),
    ])

    # Resources for the appearance stream (fonts and images)
    resources = DictionaryObject()

    # Font resources
    font_dict = DictionaryObject()
    helv_font = DictionaryObject()
    helv_font[NameObject("/Type")] = NameObject("/Font")
    helv_font[NameObject("/Subtype")] = NameObject("/Type1")
    helv_font[NameObject("/BaseFont")] = NameObject("/Helvetica-Bold")
    font_dict[NameObject("/Helv")] = helv_font
    resources[NameObject("/Font")] = font_dict

    # XObject resources (the image)
    xobject_dict = DictionaryObject()
    xobject_dict[NameObject("/Img")] = image_xobject_ref
    resources[NameObject("/XObject")] = xobject_dict

    ap_stream[NameObject("/Resources")] = resources
    ap_stream._data = content_bytes

    return writer._add_object(ap_stream)


def find_bid_annotation(page, target_subject: str) -> tuple[int, dict] | None:
    """
    Find the first annotation with the given subject.

    Returns:
        Tuple of (index, annotation_dict) or None if not found
    """
    annots_ref = page.get("/Annots")
    if not annots_ref:
        return None

    annots = annots_ref.get_object() if hasattr(annots_ref, 'get_object') else annots_ref

    for idx, annot_ref in enumerate(annots):
        annot = annot_ref.get_object() if hasattr(annot_ref, 'get_object') else annot_ref
        subj = str(annot.get("/Subj", ""))
        if subj == target_subject:
            # Extract key properties
            rect = annot.get("/Rect", [])
            return idx, {
                "rect": [float(r) for r in rect] if rect else None,
                "subtype": str(annot.get("/Subtype", "")),
                "original": annot,
            }

    return None


def create_deployment_annotation(
    writer: PdfWriter,
    rect: list[float],
    deployment_subject: str,
    appearance_ref: IndirectObject,
) -> DictionaryObject:
    """
    Create a deployment annotation with the given appearance.
    """
    x1, y1, x2, y2 = rect

    annot = DictionaryObject()
    annot[NameObject("/Type")] = NameObject("/Annot")
    annot[NameObject("/Subtype")] = NameObject("/Circle")  # Use Circle like original bid icons
    annot[NameObject("/Rect")] = ArrayObject([
        FloatObject(x1),
        FloatObject(y1),
        FloatObject(x2),
        FloatObject(y2),
    ])
    annot[NameObject("/Subj")] = TextStringObject(deployment_subject)
    annot[NameObject("/F")] = NumberObject(4)  # Print flag

    # Colors (these may be ignored if AP is present, but good for fallback)
    annot[NameObject("/IC")] = ArrayObject([
        FloatObject(CIRCLE_COLOR_RGB[0]),
        FloatObject(CIRCLE_COLOR_RGB[1]),
        FloatObject(CIRCLE_COLOR_RGB[2]),
    ])
    annot[NameObject("/C")] = ArrayObject([
        FloatObject(CIRCLE_BORDER_COLOR[0]),
        FloatObject(CIRCLE_BORDER_COLOR[1]),
        FloatObject(CIRCLE_BORDER_COLOR[2]),
    ])

    # Border style
    bs = DictionaryObject()
    bs[NameObject("/W")] = FloatObject(CIRCLE_BORDER_WIDTH)
    bs[NameObject("/S")] = NameObject("/S")
    annot[NameObject("/BS")] = bs

    # Appearance dictionary - THIS IS THE KEY
    ap = DictionaryObject()
    ap[NameObject("/N")] = appearance_ref  # Normal appearance
    annot[NameObject("/AP")] = ap

    return annot


def main():
    print("=" * 60)
    print("MR36H Icon Conversion Test")
    print("=" * 60)

    # Verify files exist
    if not SAMPLE_PDF.exists():
        print(f"ERROR: Sample PDF not found: {SAMPLE_PDF}")
        return

    if not GEAR_ICON.exists():
        print(f"ERROR: Gear icon not found: {GEAR_ICON}")
        print(f"  Looking in: {GEAR_ICON.parent}")
        return

    print(f"\nSource PDF: {SAMPLE_PDF}")
    print(f"Gear Icon: {GEAR_ICON}")
    print(f"Reference PDF: {REFERENCE_PDF}")
    print(f"Output: {OUTPUT_PDF}")
    print(f"\nConverting: '{BID_SUBJECT}' -> '{DEPLOYMENT_SUBJECT}'")
    print("\nVisual settings:")
    print(f"  Circle fill: RGB{CIRCLE_COLOR_RGB}")
    print(f"  Border: {CIRCLE_BORDER_WIDTH}pt, RGB{CIRCLE_BORDER_COLOR}")

    # Load the PDF
    reader = PdfReader(str(SAMPLE_PDF))
    writer = PdfWriter()

    # Copy all pages
    for page in reader.pages:
        writer.add_page(page)

    # Work with the first page
    page = writer.pages[0]

    # Find the target annotation
    result = find_bid_annotation(page, BID_SUBJECT)
    if not result:
        print(f"\nERROR: Could not find annotation with subject '{BID_SUBJECT}'")
        return

    annot_idx, annot_info = result
    rect = annot_info["rect"]

    print(f"\nFound annotation at index {annot_idx}")
    print(f"  Rect: {rect}")
    print(f"  Size: {rect[2] - rect[0]:.2f} x {rect[3] - rect[1]:.2f} PDF units")

    # Load and prepare the image
    print("\nLoading gear icon image...")
    img_data, img_width, img_height = load_image_as_xobject(GEAR_ICON)
    print(f"  Original size: {img_width} x {img_height} pixels")
    print(f"  Data size: {len(img_data)} bytes")

    # Create image XObject
    print("\nCreating PDF XObject for image...")
    img_xobject_ref = create_image_xobject(writer, img_data, img_width, img_height)

    # Create appearance stream with absolute coordinates
    print("Creating appearance stream with ID box, circle, image, and text...")
    appearance_ref = create_appearance_stream(
        writer, rect,
        img_xobject_ref, img_width, img_height,
        model_text="MR36H",
        id_label="j100",  # ID label for the top box
    )

    # Create the deployment annotation
    print("Creating deployment annotation...")
    new_annot = create_deployment_annotation(
        writer, rect, DEPLOYMENT_SUBJECT, appearance_ref
    )

    # Replace the annotation in the page
    annots_ref = page.get("/Annots")
    annots = annots_ref.get_object() if hasattr(annots_ref, 'get_object') else annots_ref

    # Remove old annotation and add new one
    del annots[annot_idx]
    annots.append(new_annot)

    print(f"\nReplaced annotation at index {annot_idx}")

    # Save the output
    print(f"\nSaving to: {OUTPUT_PDF}")
    with open(OUTPUT_PDF, "wb") as f:
        writer.write(f)

    print("\n" + "=" * 60)
    print("SUCCESS! Open the output PDF to verify the icon appearance.")
    print("=" * 60)
    print("\nTo compare with reference:")
    print(f"  1. Open: {OUTPUT_PDF}")
    print(f"  2. Compare to 'j100' icon in: {REFERENCE_PDF}")
    print("\nThe converted icon should show:")
    print("  - ID box on top ('j100' in blue text, white background)")
    print("  - Navy blue circle (RGB 0.22, 0.34, 0.65)")
    print("  - 'CISCO' text (white, above gear image)")
    print("  - MR36H product image in center (on blue background)")
    print("  - 'MR36H' text (white, below gear image)")
    print("  - Thin dark border (~0.5pt)")


if __name__ == "__main__":
    main()
