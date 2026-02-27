#!/usr/bin/env python
"""
Generate two test PDFs for Bluebeam comparison of BBox/Matrix strategies.

PDF A: Absolute BBox + Matrix (matches real Bluebeam annotation structure)
  - BBox = [x1, y1, x2, y2] (absolute page coordinates)
  - Matrix = [1, 0, 0, 1, -x1, -y1] (form-to-page transform)
  - Content stream draws at ABSOLUTE page coordinates

PDF B: Zero-origin BBox, no Matrix (pre-session working approach)
  - BBox = [0, 0, width, height]
  - No Matrix
  - Content stream draws at LOCAL zero-origin coordinates

Both PDFs have /IC, /C, /BS always present (native color fallback).

Usage: cd backend && uv run python scripts/test_bbox_variants.py
"""

import sys
from pathlib import Path
from types import MethodType

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pypdf.generic import (
    ArrayObject,
    FloatObject,
    NameObject,
    NumberObject,
    StreamObject,
)
from pypdf import PdfWriter

from app.services.pdf_parser import PDFAnnotationParser
from app.services.mapping_parser import MappingParser
from app.services.btx_loader import BTXReferenceLoader
from app.services.annotation_replacer import AnnotationReplacer
from app.services.appearance_extractor import AppearanceExtractor
from app.services.icon_renderer import IconRenderer, measure_text_width
from app.services.layer_manager import LayerManager


# ---------------------------------------------------------------------------
# PDF A variant: absolute BBox + absolute content coords + Matrix
# ---------------------------------------------------------------------------

def _create_appearance_stream_absolute(
    self, writer, rect, config, image_xobject_ref,
    img_width, img_height, model_text, brand_text, id_label,
):
    """PDF A: absolute BBox [x1,y1,x2,y2], Matrix [1,0,0,1,-x1,-y1], absolute cm."""
    x1, y1, x2, y2 = rect
    rect_width = x2 - x1
    rect_height = y2 - y1

    CANON_W, CANON_H = 25.0, 30.0
    render_scale = min(rect_width / CANON_W, rect_height / CANON_H)
    content_w = CANON_W * render_scale
    content_h = CANON_H * render_scale

    # ABSOLUTE offsets — content draws at page coordinates
    x_off = x1 + (rect_width - content_w) / 2
    y_off = y1 + (rect_height - content_h) / 2

    # Extract config parameters (same as original)
    circle_color = config.get("circle_color", (0.22, 0.34, 0.65))
    circle_border_width = config.get("circle_border_width", 0.5)
    circle_border_color = config.get("circle_border_color", (0.0, 0.0, 0.0))
    id_box_height = config.get("id_box_height", 4.0)
    id_box_width_ratio = config.get("id_box_width_ratio", 0.55)
    id_box_border_width = config.get("id_box_border_width", 0.6)
    id_box_y_offset = config.get("id_box_y_offset", 0.0)
    no_id_box = config.get("no_id_box", False)
    img_scale_ratio = config.get("img_scale_ratio", 0.70)
    brand_font_size = config.get("brand_font_size", 1.9)
    brand_y_offset = config.get("brand_y_offset", -4.0)
    brand_x_offset = config.get("brand_x_offset", -0.2)
    model_font_size = config.get("model_font_size", 1.6)
    model_y_offset = config.get("model_y_offset", 2.5)
    model_x_offset = config.get("model_x_offset", -0.7)
    text_color = config.get("text_color", (1.0, 1.0, 1.0))
    id_text_color = config.get("id_text_color") or circle_color
    id_font_size = config.get("id_font_size", 2.5)

    # Layout in canonical space (same as original)
    width = CANON_W
    cx = CANON_W / 2
    id_box_width = width * id_box_width_ratio
    id_box_x1_val = cx - id_box_width / 2
    id_box_y1_val = CANON_H - id_box_height + id_box_y_offset
    circle_top = id_box_y1_val + 2
    circle_bottom = 0
    circle_area_height = circle_top - circle_bottom
    radius = min(width, circle_area_height) / 2 - 0.3
    cy = circle_top - radius
    img_scale = (radius * img_scale_ratio) / max(img_width, img_height)
    img_draw_width = img_width * img_scale
    img_draw_height = img_height * img_scale
    img_x_offset = config.get("img_x_offset", 0.0)
    img_y_offset = config.get("img_y_offset", 0.0)
    img_x = cx - img_draw_width / 2 + img_x_offset
    img_y = cy - img_draw_height / 2 + img_y_offset

    inner_parts = self._build_content_stream(
        cx=cx, cy=cy, radius=radius,
        circle_color=circle_color,
        circle_border_color=circle_border_color,
        circle_border_width=circle_border_width,
        id_box_x1=id_box_x1_val, id_box_y1=id_box_y1_val,
        id_box_width=id_box_width, id_box_height=id_box_height,
        id_box_border_width=id_box_border_width,
        no_id_box=no_id_box,
        id_label=id_label,
        id_text_color=id_text_color,
        id_font_size=id_font_size,
        img_x=img_x, img_y=img_y,
        img_draw_width=img_draw_width, img_draw_height=img_draw_height,
        brand_text=brand_text,
        brand_font_size=brand_font_size,
        brand_y_offset=brand_y_offset,
        brand_x_offset=brand_x_offset,
        model_text=model_text,
        model_font_size=model_font_size,
        model_y_offset=model_y_offset,
        model_x_offset=model_x_offset,
        text_color=text_color,
    )

    # Wrap with ABSOLUTE cm transform
    content_parts = [
        "q",
        f"{render_scale:.6f} 0 0 {render_scale:.6f} {x_off:.3f} {y_off:.3f} cm",
    ]
    content_parts.extend(inner_parts)
    content_parts.append("Q")

    content_string = "\n".join(content_parts)
    content_bytes = content_string.encode("latin-1")

    # Appearance stream with ABSOLUTE BBox and Matrix
    from pypdf.generic import DictionaryObject
    ap_stream = StreamObject()
    ap_stream[NameObject("/Type")] = NameObject("/XObject")
    ap_stream[NameObject("/Subtype")] = NameObject("/Form")
    ap_stream[NameObject("/FormType")] = NumberObject(1)
    # Absolute BBox
    ap_stream[NameObject("/BBox")] = ArrayObject([
        FloatObject(x1), FloatObject(y1),
        FloatObject(x2), FloatObject(y2),
    ])
    # Matrix transforms form space → page space
    ap_stream[NameObject("/Matrix")] = ArrayObject([
        FloatObject(1), FloatObject(0),
        FloatObject(0), FloatObject(1),
        FloatObject(-x1), FloatObject(-y1),
    ])

    # Resources
    resources = DictionaryObject()
    font_dict = DictionaryObject()
    helv_font = DictionaryObject()
    helv_font[NameObject("/Type")] = NameObject("/Font")
    helv_font[NameObject("/Subtype")] = NameObject("/Type1")
    helv_font[NameObject("/BaseFont")] = NameObject("/Helvetica-Bold")
    font_dict[NameObject("/Helv")] = helv_font
    resources[NameObject("/Font")] = font_dict
    xobject_dict = DictionaryObject()
    xobject_dict[NameObject("/Img")] = image_xobject_ref
    resources[NameObject("/XObject")] = xobject_dict
    ap_stream[NameObject("/Resources")] = resources
    ap_stream._data = content_bytes

    return writer._add_object(ap_stream)


def _create_simple_appearance_absolute(
    self, writer, rect, fill_color, stroke_color, annotation_type,
):
    """PDF A: simple appearance with absolute BBox + Matrix."""
    from app.services.annotation_replacer import DEFAULT_BORDER_WIDTH

    x1, y1, x2, y2 = rect
    width = x2 - x1
    height = y2 - y1

    # Absolute coordinates for content
    cx = x1 + width / 2
    cy = y1 + height / 2
    radius = min(width, height) / 2 - 0.5

    r, g, b = fill_color
    sr, sg, sb = stroke_color

    content_parts = []
    content_parts.append(f"{sr:.4f} {sg:.4f} {sb:.4f} RG")
    content_parts.append(f"{DEFAULT_BORDER_WIDTH:.4f} w")
    content_parts.append(f"{r:.4f} {g:.4f} {b:.4f} rg")

    if annotation_type == "/Circle":
        k = 0.5522847498
        x0, y0 = cx + radius, cy
        content_parts.append(f"{x0:.3f} {y0:.3f} m")
        content_parts.append(f"{cx + radius:.3f} {cy + radius * k:.3f} {cx + radius * k:.3f} {cy + radius:.3f} {cx:.3f} {cy + radius:.3f} c")
        content_parts.append(f"{cx - radius * k:.3f} {cy + radius:.3f} {cx - radius:.3f} {cy + radius * k:.3f} {cx - radius:.3f} {cy:.3f} c")
        content_parts.append(f"{cx - radius:.3f} {cy - radius * k:.3f} {cx - radius * k:.3f} {cy - radius:.3f} {cx:.3f} {cy - radius:.3f} c")
        content_parts.append(f"{cx + radius * k:.3f} {cy - radius:.3f} {cx + radius:.3f} {cy - radius * k:.3f} {cx + radius:.3f} {cy:.3f} c")
        content_parts.append("h")
        content_parts.append("B")
    else:
        content_parts.append(f"{x1:.3f} {y1:.3f} {width:.3f} {height:.3f} re")
        content_parts.append("B")

    content_string = "\n".join(content_parts)
    content_bytes = content_string.encode("latin-1")

    from pypdf.generic import DictionaryObject
    ap_stream = StreamObject()
    ap_stream[NameObject("/Type")] = NameObject("/XObject")
    ap_stream[NameObject("/Subtype")] = NameObject("/Form")
    ap_stream[NameObject("/FormType")] = NumberObject(1)
    # Absolute BBox
    ap_stream[NameObject("/BBox")] = ArrayObject([
        FloatObject(x1), FloatObject(y1),
        FloatObject(x2), FloatObject(y2),
    ])
    # Matrix transforms form space → page space
    ap_stream[NameObject("/Matrix")] = ArrayObject([
        FloatObject(1), FloatObject(0),
        FloatObject(0), FloatObject(1),
        FloatObject(-x1), FloatObject(-y1),
    ])
    ap_stream._data = content_bytes

    return writer._add_object(ap_stream)


# ---------------------------------------------------------------------------
# Main script
# ---------------------------------------------------------------------------

def generate_pdf(variant: str, output_path: Path, project_root: Path):
    """Generate a converted PDF with the given BBox variant."""
    input_pdf = project_root / "samples" / "maps" / "BidMap2.pdf"
    reference_pdf = project_root / "samples" / "maps" / "DeploymentMap.pdf"
    mapping_file = project_root / "backend" / "data" / "mapping.md"
    toolchest_dir = project_root / "toolchest"
    gear_icons_dir = project_root / "samples" / "icons" / "gearIcons"
    layer_ref = project_root / "samples" / "EVENT26 IT Deployment [v0.0] [USE TO IMPORT LAYER FORMATTING].pdf"

    if not input_pdf.exists():
        print(f"ERROR: Input PDF not found: {input_pdf}")
        sys.exit(1)

    # Load services
    mapping_parser = MappingParser(mapping_file)
    mapping_parser.load_mappings()

    btx_loader = BTXReferenceLoader(toolchest_dir)
    btx_loader.load_toolchest()

    appearance_extractor = AppearanceExtractor()
    if reference_pdf.exists():
        appearance_extractor.load_from_pdf(reference_pdf)

    icon_renderer = IconRenderer(gear_icons_dir)
    layer_manager = LayerManager(layer_ref) if layer_ref.exists() else None

    replacer = AnnotationReplacer(
        mapping_parser, btx_loader, appearance_extractor,
        icon_renderer, layer_manager=layer_manager,
    )

    if variant == "A":
        # Monkey-patch for absolute BBox + Matrix
        icon_renderer._create_appearance_stream = MethodType(
            _create_appearance_stream_absolute, icon_renderer
        )
        replacer._create_simple_appearance = MethodType(
            _create_simple_appearance_absolute, replacer
        )

    # variant "B" uses current code as-is (zero-origin BBox, no Matrix)

    converted, skipped, skipped_subjects = replacer.replace_annotations(
        input_pdf, output_path
    )

    return converted, skipped, skipped_subjects


def main():
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "samples" / "maps"

    pdf_a_path = output_dir / "PDF_A_absolute_bbox_matrix.pdf"
    pdf_b_path = output_dir / "PDF_B_zero_origin_bbox.pdf"

    print("=" * 60)
    print("BBox Variant Test — Generate Two PDFs for Bluebeam Comparison")
    print("=" * 60)

    # PDF A
    print("\n[PDF A] Absolute BBox + Matrix [1,0,0,1,-x1,-y1]")
    print("  Content draws at absolute page coordinates")
    print(f"  Output: {pdf_a_path.name}")
    conv_a, skip_a, _ = generate_pdf("A", pdf_a_path, project_root)
    print(f"  Result: {conv_a} converted, {skip_a} skipped")
    print(f"  Size: {pdf_a_path.stat().st_size:,} bytes")

    # PDF B
    print(f"\n[PDF B] Zero-origin BBox [0,0,w,h], no Matrix")
    print("  Content draws at local zero-origin coordinates")
    print(f"  Output: {pdf_b_path.name}")
    conv_b, skip_b, _ = generate_pdf("B", pdf_b_path, project_root)
    print(f"  Result: {conv_b} converted, {skip_b} skipped")
    print(f"  Size: {pdf_b_path.stat().st_size:,} bytes")

    # Summary
    print("\n" + "=" * 60)
    print("DONE — Open both in Bluebeam and compare:")
    print("=" * 60)
    print(f"  PDF A: {pdf_a_path}")
    print(f"  PDF B: {pdf_b_path}")
    print()
    print("Check for each:")
    print("  1. Are annotations visible?")
    print("  2. Can they be moved without turning white?")
    print("  3. Are they selectable/editable?")
    print("  4. Do rich icons (gear images, text) render correctly?")


if __name__ == "__main__":
    main()
