#!/usr/bin/env python
"""
Test script to render any deployment icon by name.

Usage:
    python test_icon_render.py "AP - Cisco MR36H"
    python test_icon_render.py "AP - Cisco 9120"
    python test_icon_render.py --list  # List all available icons
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    TextStringObject,
)

from app.services.icon_config import get_icon_config, get_model_text, ICON_CATEGORIES
from app.services.icon_renderer import IconRenderer


PROJECT_ROOT = Path(__file__).parent.parent.parent
SAMPLE_PDF = PROJECT_ROOT / "samples" / "maps" / "BidMap.pdf"
GEAR_ICONS = PROJECT_ROOT / "samples" / "icons" / "gearIcons"
OUTPUT_DIR = PROJECT_ROOT / "samples" / "maps"


def list_available_icons():
    """List all icons that can be rendered."""
    print("Available deployment icons:")
    print("-" * 60)

    renderer = IconRenderer(GEAR_ICONS)

    # Group by category
    categories: dict[str, list[str]] = {}
    for subj, cat in ICON_CATEGORIES.items():
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(subj)

    for category in sorted(categories.keys()):
        icons_in_category = categories[category]
        print(f"\n{category}:")
        for icon in sorted(icons_in_category):
            can_render = "Y" if renderer.can_render(icon) else "N"
            print(f"  [{can_render}] {icon}")

    print("\n" + "-" * 60)
    print("Legend: [Y] = Can render with image, [N] = No image available")


def render_test_icon(subject: str):
    """Render a single icon for visual testing."""
    print(f"\nRendering: {subject}")
    print("=" * 60)

    renderer = IconRenderer(GEAR_ICONS)

    if not renderer.can_render(subject):
        print(f"ERROR: Cannot render '{subject}'")
        print("  - Check if config exists in icon_config.py")
        print("  - Check if image file exists")

        config = get_icon_config(subject)
        if not config:
            print(f"  - No config found for subject")
        else:
            print(f"  - Config found, category: {config.get('category')}")
            image_path = config.get("image_path")
            if image_path:
                full_path = GEAR_ICONS / image_path
                print(f"  - Image path: {image_path}")
                print(f"  - Image exists: {full_path.exists()}")
            else:
                print("  - No image path in config")
        return

    config = get_icon_config(subject)
    print(f"Category: {config.get('category')}")
    print(f"Circle color: {config.get('circle_color')}")
    print(f"Model text: {get_model_text(subject)}")
    print(f"Brand text: {config.get('brand_text', '(none)')}")
    print(f"Image path: {config.get('image_path')}")

    # Check if sample PDF exists
    if not SAMPLE_PDF.exists():
        print(f"\nWARNING: Sample PDF not found: {SAMPLE_PDF}")
        print("Creating a blank PDF for testing...")
        # Create blank PDF
        writer = PdfWriter()
        writer.add_blank_page(612, 792)  # Letter size
    else:
        # Create test PDF from sample
        reader = PdfReader(str(SAMPLE_PDF))
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

    page = writer.pages[0]

    # Create test annotation rect (fixed position for testing)
    rect = [100.0, 700.0, 125.0, 730.0]  # 25x30 PDF units

    # Render icon
    print("\nRendering icon appearance stream...")
    appearance_ref = renderer.render_icon(writer, subject, rect, id_label="test")

    if not appearance_ref:
        print("ERROR: Rendering failed")
        return

    # Create annotation with the appearance
    annot = DictionaryObject()
    annot[NameObject("/Type")] = NameObject("/Annot")
    annot[NameObject("/Subtype")] = NameObject("/Circle")
    annot[NameObject("/Rect")] = ArrayObject(
        [
            FloatObject(rect[0]),
            FloatObject(rect[1]),
            FloatObject(rect[2]),
            FloatObject(rect[3]),
        ]
    )
    annot[NameObject("/Subj")] = TextStringObject(subject)
    annot[NameObject("/F")] = NumberObject(4)

    # Set colors
    circle_color = config.get("circle_color", (0.5, 0.5, 0.5))
    annot[NameObject("/IC")] = ArrayObject(
        [
            FloatObject(circle_color[0]),
            FloatObject(circle_color[1]),
            FloatObject(circle_color[2]),
        ]
    )

    # Appearance
    ap = DictionaryObject()
    ap[NameObject("/N")] = appearance_ref
    annot[NameObject("/AP")] = ap

    # Add to page annotations
    annots_ref = page.get("/Annots")
    if annots_ref:
        annots = annots_ref.get_object() if hasattr(annots_ref, "get_object") else annots_ref
        annots.append(annot)
    else:
        # Create new annotations array
        page[NameObject("/Annots")] = ArrayObject([annot])

    # Save
    safe_name = subject.replace(" ", "_").replace("-", "_").replace("/", "_")
    output_path = OUTPUT_DIR / f"test_icon_{safe_name}.pdf"

    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"\nSaved to: {output_path}")
    print("\nOpen the PDF and verify the icon appearance.")
    print("The icon should appear in the top-left area of the first page.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_icon_render.py <subject>")
        print("       python test_icon_render.py --list")
        print()
        print("Examples:")
        print('  python test_icon_render.py "AP - Cisco MR36H"')
        print('  python test_icon_render.py "SW - Cisco Micro 4P"')
        print('  python test_icon_render.py "HL - Artist"')
        sys.exit(1)

    if sys.argv[1] == "--list":
        list_available_icons()
    else:
        subject = " ".join(sys.argv[1:])
        render_test_icon(subject)


if __name__ == "__main__":
    main()
