"""
Test script to convert a single bid icon to deployment icon with proper visual appearance.

This script:
1. Finds ONE "Artist - Indoor Wi-Fi Access Point" annotation in BidMap.pdf
2. Replaces it with "AP - Cisco 9120" that has a proper appearance stream
3. Saves the result for visual verification

The appearance stream includes:
- Blue circle background
- "CISCO" text header
- Product image (from gearIcons)
- Model number text
"""

import zlib
from pathlib import Path
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    IndirectObject,
    NameObject,
    NumberObject,
    StreamObject,
    TextStringObject,
)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SAMPLE_PDF = PROJECT_ROOT / "samples" / "maps" / "BidMap.pdf"
GEAR_ICON = PROJECT_ROOT / "toolchest" / "gearIcons" / "APs" / "AP - Cisco 9120.png"
OUTPUT_PDF = PROJECT_ROOT / "samples" / "maps" / "test_single_icon_v3.pdf"

# Target annotation
BID_SUBJECT = "Artist - Indoor Wi-Fi Access Point"
DEPLOYMENT_SUBJECT = "AP - Cisco 9120"

# Visual settings (Bluebeam blue color)
CIRCLE_COLOR_RGB = (0.2196, 0.3412, 0.6471)  # Blue from BTX
CIRCLE_BORDER_WIDTH = 0.5


def load_image_as_xobject(image_path: Path, target_size: tuple[int, int] = None) -> tuple[bytes, int, int]:
    """
    Load a PNG image and prepare it for PDF embedding.

    Returns:
        Tuple of (image_data, width, height)
    """
    with Image.open(image_path) as img:
        # Convert to RGB if necessary (remove alpha for simplicity)
        if img.mode in ('RGBA', 'P'):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[3])  # Use alpha as mask
            else:
                img = img.convert('RGBA')
                background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize if needed
        if target_size:
            img = img.resize(target_size, Image.Resampling.LANCZOS)

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
    model_text: str = "9120",
) -> IndirectObject:
    """
    Create a PDF appearance stream that draws:
    1. Blue filled circle
    2. Product image in center
    3. "CISCO" text at top
    4. Model number at bottom

    Uses ABSOLUTE page coordinates (like Bluebeam does) for the BBox and drawing.

    Args:
        writer: PdfWriter to add objects to
        rect: Annotation rect [x1, y1, x2, y2] in absolute page coordinates
        image_xobject_ref: Reference to the image XObject
        img_width: Image width in pixels
        img_height: Image height in pixels
        model_text: Model number to display

    Returns:
        IndirectObject reference to the appearance stream
    """
    x1, y1, x2, y2 = rect
    width = x2 - x1
    height = y2 - y1

    # Center in absolute coordinates
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    radius = min(width, height) / 2 - 0.5  # Circle radius with small margin

    # Image dimensions (scaled to fit in circle)
    img_scale = (radius * 0.9) / max(img_width, img_height)
    img_draw_width = img_width * img_scale
    img_draw_height = img_height * img_scale
    img_x = cx - img_draw_width / 2
    img_y = cy - img_draw_height / 2 - 0.5  # Offset down slightly for text

    # Build the content stream using ABSOLUTE coordinates
    r, g, b = CIRCLE_COLOR_RGB
    k = 0.5522847498  # Magic constant for circle Bezier approximation

    content_parts = []

    # Set stroke color (black) and line width first
    content_parts.append("0 0 0 RG")  # Black stroke
    content_parts.append(f"{CIRCLE_BORDER_WIDTH:.4f} w")  # Line width

    # Set fill color (blue)
    content_parts.append(f"{r:.4f} {g:.4f} {b:.4f} rg")

    # Draw circle using 4 Bezier curves with absolute coordinates
    # Start at the right-most point (3 o'clock position)
    x0 = cx + radius
    y0 = cy

    content_parts.append(f"{x0:.3f} {y0:.3f} m")  # Move to start

    # Curve 1: Right to Top (3 o'clock to 12 o'clock)
    cp1x, cp1y = cx + radius, cy + radius * k
    cp2x, cp2y = cx + radius * k, cy + radius
    endx, endy = cx, cy + radius
    content_parts.append(f"{cp1x:.3f} {cp1y:.3f} {cp2x:.3f} {cp2y:.3f} {endx:.3f} {endy:.3f} c")

    # Curve 2: Top to Left (12 o'clock to 9 o'clock)
    cp1x, cp1y = cx - radius * k, cy + radius
    cp2x, cp2y = cx - radius, cy + radius * k
    endx, endy = cx - radius, cy
    content_parts.append(f"{cp1x:.3f} {cp1y:.3f} {cp2x:.3f} {cp2y:.3f} {endx:.3f} {endy:.3f} c")

    # Curve 3: Left to Bottom (9 o'clock to 6 o'clock)
    cp1x, cp1y = cx - radius, cy - radius * k
    cp2x, cp2y = cx - radius * k, cy - radius
    endx, endy = cx, cy - radius
    content_parts.append(f"{cp1x:.3f} {cp1y:.3f} {cp2x:.3f} {cp2y:.3f} {endx:.3f} {endy:.3f} c")

    # Curve 4: Bottom to Right (6 o'clock to 3 o'clock) - closes the circle
    cp1x, cp1y = cx + radius * k, cy - radius
    cp2x, cp2y = cx + radius, cy - radius * k
    endx, endy = cx + radius, cy
    content_parts.append(f"{cp1x:.3f} {cp1y:.3f} {cp2x:.3f} {cp2y:.3f} {endx:.3f} {endy:.3f} c")

    # Close path and fill+stroke
    content_parts.append("h")  # Close path
    content_parts.append("B")  # Fill and stroke

    # Draw the image using transformation matrix
    content_parts.append("q")  # Save state
    content_parts.append(f"{img_draw_width:.3f} 0 0 {img_draw_height:.3f} {img_x:.3f} {img_y:.3f} cm")
    content_parts.append("/Img Do")
    content_parts.append("Q")  # Restore state

    # Draw "CISCO" text at top (white text inside the circle)
    content_parts.append("BT")
    content_parts.append("1 1 1 rg")  # White fill
    content_parts.append("/Helv 2.2 Tf")
    text_x_cisco = cx - 4
    text_y_top = cy + radius * 0.45
    content_parts.append(f"{text_x_cisco:.3f} {text_y_top:.3f} Td")
    content_parts.append("(CISCO) Tj")
    content_parts.append("ET")

    # Draw model number at bottom
    content_parts.append("BT")
    content_parts.append("1 1 1 rg")
    content_parts.append("/Helv 1.8 Tf")
    text_x_model = cx - 2.5
    text_y_bottom = cy - radius * 0.6
    content_parts.append(f"{text_x_model:.3f} {text_y_bottom:.3f} Td")
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
        FloatObject(0), FloatObject(0), FloatObject(0),  # Black border
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
    print("Single Icon Conversion Test")
    print("=" * 60)

    # Verify files exist
    if not SAMPLE_PDF.exists():
        print(f"ERROR: Sample PDF not found: {SAMPLE_PDF}")
        return

    if not GEAR_ICON.exists():
        print(f"ERROR: Gear icon not found: {GEAR_ICON}")
        return

    print(f"\nSource PDF: {SAMPLE_PDF}")
    print(f"Gear Icon: {GEAR_ICON}")
    print(f"Output: {OUTPUT_PDF}")
    print(f"\nConverting: '{BID_SUBJECT}' -> '{DEPLOYMENT_SUBJECT}'")

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
    print("Creating appearance stream with circle, image, and text...")
    appearance_ref = create_appearance_stream(
        writer, rect,  # Pass full rect for absolute coordinates
        img_xobject_ref, img_width, img_height,
        model_text="9120"
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
    print("\nCompare this annotation to others in the PDF.")
    print("The converted icon should show:")
    print("  - Blue circle background")
    print("  - 'CISCO' text at top")
    print("  - Product image in center")
    print("  - '9120' model number at bottom")


if __name__ == "__main__":
    main()
