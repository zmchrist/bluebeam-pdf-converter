"""
Icon renderer service.

Creates PDF appearance streams for deployment icons with:
- Blue filled circle background
- ID box label at top
- Product image in center
- Brand text (e.g., "CISCO")
- Model text (e.g., "MR36H")

Supports two rendering modes:
1. Combined (legacy): Single appearance stream with all elements (for Icon Tuner preview)
2. Compound: Separate appearance streams per component (for Bluebeam-native groups)
"""

import logging
import zlib
from pathlib import Path
from typing import Any

from PIL import Image
from pypdf import PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    IndirectObject,
    NameObject,
    NumberObject,
    StreamObject,
)

from app.services.icon_config import get_icon_config, get_model_text

logger = logging.getLogger(__name__)


# Helvetica-Bold character widths in 1/1000 em units (from Adobe AFM)
HELVETICA_BOLD_WIDTHS: dict[str, int] = {
    " ": 278, "!": 333, '"': 474, "#": 556, "$": 556, "%": 889, "&": 722,
    "'": 238, "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333,
    ".": 278, "/": 278, "0": 556, "1": 556, "2": 556, "3": 556, "4": 556,
    "5": 556, "6": 556, "7": 556, "8": 556, "9": 556, ":": 333, ";": 333,
    "<": 584, "=": 584, ">": 584, "?": 611, "@": 975, "A": 722, "B": 722,
    "C": 722, "D": 722, "E": 667, "F": 611, "G": 778, "H": 722, "I": 278,
    "J": 556, "K": 722, "L": 611, "M": 833, "N": 722, "O": 778, "P": 667,
    "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722, "V": 667, "W": 944,
    "X": 667, "Y": 667, "Z": 611, "[": 333, "\\": 278, "]": 333, "^": 584,
    "_": 556, "`": 333, "a": 556, "b": 611, "c": 556, "d": 611, "e": 556,
    "f": 333, "g": 611, "h": 611, "i": 278, "j": 278, "k": 556, "l": 278,
    "m": 889, "n": 611, "o": 611, "p": 611, "q": 611, "r": 389, "s": 556,
    "t": 333, "u": 611, "v": 556, "w": 778, "x": 556, "y": 556, "z": 500,
    "{": 389, "|": 280, "}": 389, "~": 584,
}


def measure_text_width(text: str, font_size: float) -> float:
    """Measure text width using Helvetica-Bold character metrics."""
    width_units = sum(HELVETICA_BOLD_WIDTHS.get(ch, 556) for ch in text)
    return width_units * font_size / 1000


class IconRenderer:
    """Service for rendering deployment icons as PDF appearance streams."""

    # Bezier magic constant for circle approximation
    BEZIER_K = 0.5522847498

    def __init__(self, gear_icons_dir: Path):
        """
        Initialize icon renderer.

        Args:
            gear_icons_dir: Path to gear icons directory (samples/icons/gearIcons)
        """
        self.gear_icons_dir = gear_icons_dir
        self._image_cache: dict[str, tuple[bytes, int, int]] = {}

    def can_render(self, subject: str) -> bool:
        """
        Check if renderer can render the given subject.

        Args:
            subject: Deployment subject name (e.g., "AP - Cisco MR36H")

        Returns:
            True if the icon can be rendered (has config and image exists)
        """
        config = get_icon_config(subject)
        if not config:
            return False

        # Check if marked as no_image (simple shapes only)
        if config.get("no_image"):
            return False

        image_path = config.get("image_path")
        if not image_path:
            return False

        full_path = self.gear_icons_dir / image_path
        return full_path.exists()

    def load_image(
        self,
        image_path: str,
        bg_color: tuple[float, float, float],
    ) -> tuple[bytes, int, int]:
        """
        Load PNG image and prepare for PDF embedding.

        Args:
            image_path: Relative path from gear_icons_dir
            bg_color: RGB background color (0-1 range) for transparent areas

        Returns:
            Tuple of (raw_rgb_bytes, width, height)
        """
        cache_key = f"{image_path}:{bg_color}"
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        full_path = self.gear_icons_dir / image_path

        # Convert 0-1 to 0-255
        bg_rgb = (
            int(bg_color[0] * 255),
            int(bg_color[1] * 255),
            int(bg_color[2] * 255),
        )

        with Image.open(full_path) as img:
            if img.mode in ("RGBA", "P"):
                background = Image.new("RGB", img.size, bg_rgb)
                if img.mode == "RGBA":
                    background.paste(img, mask=img.split()[3])
                else:
                    img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            width, height = img.size
            raw_data = img.tobytes()

        self._image_cache[cache_key] = (raw_data, width, height)
        return raw_data, width, height

    def create_image_xobject(
        self,
        writer: PdfWriter,
        image_data: bytes,
        width: int,
        height: int,
    ) -> IndirectObject:
        """
        Create PDF XObject Image from raw RGB data.

        Args:
            writer: PdfWriter to add the object to
            image_data: Raw RGB byte data
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            IndirectObject reference to the image XObject
        """
        compressed = zlib.compress(image_data)

        img_dict = DictionaryObject()
        img_dict[NameObject("/Type")] = NameObject("/XObject")
        img_dict[NameObject("/Subtype")] = NameObject("/Image")
        img_dict[NameObject("/Width")] = NumberObject(width)
        img_dict[NameObject("/Height")] = NumberObject(height)
        img_dict[NameObject("/ColorSpace")] = NameObject("/DeviceRGB")
        img_dict[NameObject("/BitsPerComponent")] = NumberObject(8)
        img_dict[NameObject("/Filter")] = NameObject("/FlateDecode")
        img_dict[NameObject("/Length")] = NumberObject(len(compressed))

        img_stream = StreamObject()
        img_stream.update(img_dict)
        img_stream._data = compressed

        return writer._add_object(img_stream)

    def render_icon(
        self,
        writer: PdfWriter,
        subject: str,
        rect: list[float],
        id_label: str = "j100",
    ) -> IndirectObject | None:
        """
        Render a deployment icon and return its appearance stream.

        Args:
            writer: PdfWriter to add objects to
            subject: Deployment subject (e.g., "AP - Cisco MR36H")
            rect: Annotation rect [x1, y1, x2, y2]
            id_label: ID label for top box (e.g., "j100")

        Returns:
            IndirectObject reference to appearance stream, or None if can't render
        """
        config = get_icon_config(subject)
        if not config:
            logger.warning(f"No config found for subject: {subject}")
            return None

        image_path = config.get("image_path")
        if not image_path:
            logger.warning(f"No image path for subject: {subject}")
            return None

        full_image_path = self.gear_icons_dir / image_path
        if not full_image_path.exists():
            logger.warning(f"Image not found: {full_image_path}")
            return None

        # Load image
        circle_color = config.get("circle_color", (0.5, 0.5, 0.5))
        img_data, img_width, img_height = self.load_image(image_path, circle_color)

        # Create image XObject
        img_xobject_ref = self.create_image_xobject(writer, img_data, img_width, img_height)

        # Build appearance stream
        # Check for model text override, otherwise use extracted model
        model_text = config.get("model_text_override") or get_model_text(subject)
        # Apply uppercase if configured
        if config.get("model_uppercase"):
            model_text = model_text.upper()
        brand_text = config.get("brand_text", "")

        return self._create_appearance_stream(
            writer=writer,
            rect=rect,
            config=config,
            image_xobject_ref=img_xobject_ref,
            img_width=img_width,
            img_height=img_height,
            model_text=model_text,
            brand_text=brand_text,
            id_label=id_label,
        )

    def _create_appearance_stream(
        self,
        writer: PdfWriter,
        rect: list[float],
        config: dict[str, Any],
        image_xobject_ref: IndirectObject,
        img_width: int,
        img_height: int,
        model_text: str,
        brand_text: str,
        id_label: str,
    ) -> IndirectObject:
        """
        Create the PDF appearance stream with all visual elements.

        Args:
            writer: PdfWriter to add objects to
            rect: Annotation rect [x1, y1, x2, y2]
            config: Icon configuration dictionary
            image_xobject_ref: Reference to the image XObject
            img_width: Image width in pixels
            img_height: Image height in pixels
            model_text: Model text to display
            brand_text: Brand text to display (e.g., "CISCO")
            id_label: ID label text (e.g., "j100")

        Returns:
            IndirectObject reference to the appearance stream
        """
        x1, y1, x2, y2 = rect
        rect_width = x2 - x1
        rect_height = y2 - y1

        # Canonical coordinate space (matches tuner's 25x30 canvas)
        CANON_W, CANON_H = 25.0, 30.0
        render_scale = min(rect_width / CANON_W, rect_height / CANON_H)
        content_w = CANON_W * render_scale
        content_h = CANON_H * render_scale
        # Zero-origin offsets: BBox is [0,0,w,h], content draws in local coords
        x_off = (rect_width - content_w) / 2
        y_off = (rect_height - content_h) / 2

        # Extract config parameters with defaults
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

        # Layout in canonical [0, 0, 25, 30] space (identical to tuner)
        width = CANON_W
        cx = CANON_W / 2  # 12.5
        id_box_width = width * id_box_width_ratio
        id_box_x1 = cx - id_box_width / 2
        id_box_y1 = CANON_H - id_box_height + id_box_y_offset

        # Circle overlaps into ID box by 2px
        circle_top = id_box_y1 + 2
        circle_bottom = 0
        circle_area_height = circle_top - circle_bottom

        radius = min(width, circle_area_height) / 2 - 0.3
        cy = circle_top - radius

        # Image dimensions
        img_scale = (radius * img_scale_ratio) / max(img_width, img_height)
        img_draw_width = img_width * img_scale
        img_draw_height = img_height * img_scale
        img_x_offset = config.get("img_x_offset", 0.0)
        img_y_offset = config.get("img_y_offset", 0.0)
        img_x = cx - img_draw_width / 2 + img_x_offset
        img_y = cy - img_draw_height / 2 + img_y_offset

        # Build content stream in canonical space, wrapped with cm transform
        inner_parts = self._build_content_stream(
            cx=cx,
            cy=cy,
            radius=radius,
            circle_color=circle_color,
            circle_border_color=circle_border_color,
            circle_border_width=circle_border_width,
            id_box_x1=id_box_x1,
            id_box_y1=id_box_y1,
            id_box_width=id_box_width,
            id_box_height=id_box_height,
            id_box_border_width=id_box_border_width,
            no_id_box=no_id_box,
            id_label=id_label,
            id_text_color=id_text_color,
            id_font_size=id_font_size,
            img_x=img_x,
            img_y=img_y,
            img_draw_width=img_draw_width,
            img_draw_height=img_draw_height,
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

        # Wrap with save/restore and cm transform to scale canonical → actual rect
        content_parts = [
            "q",
            f"{render_scale:.6f} 0 0 {render_scale:.6f} {x_off:.3f} {y_off:.3f} cm",
        ]
        content_parts.extend(inner_parts)
        content_parts.append("Q")

        content_string = "\n".join(content_parts)
        content_bytes = content_string.encode("latin-1")

        # Create appearance stream
        ap_stream = StreamObject()
        ap_stream[NameObject("/Type")] = NameObject("/XObject")
        ap_stream[NameObject("/Subtype")] = NameObject("/Form")
        ap_stream[NameObject("/FormType")] = NumberObject(1)
        ap_stream[NameObject("/BBox")] = ArrayObject(
            [
                FloatObject(0),
                FloatObject(0),
                FloatObject(rect_width),
                FloatObject(rect_height),
            ]
        )

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

    def _build_content_stream(
        self,
        cx: float,
        cy: float,
        radius: float,
        circle_color: tuple[float, float, float],
        circle_border_color: tuple[float, float, float],
        circle_border_width: float,
        id_box_x1: float,
        id_box_y1: float,
        id_box_width: float,
        id_box_height: float,
        id_box_border_width: float,
        no_id_box: bool,
        id_label: str,
        id_text_color: tuple[float, float, float],
        id_font_size: float,
        img_x: float,
        img_y: float,
        img_draw_width: float,
        img_draw_height: float,
        brand_text: str,
        brand_font_size: float,
        brand_y_offset: float,
        brand_x_offset: float,
        model_text: str,
        model_font_size: float,
        model_y_offset: float,
        model_x_offset: float,
        text_color: tuple[float, float, float],
    ) -> list[str]:
        """
        Build the PDF content stream drawing commands.

        Args:
            All layout parameters for drawing the icon

        Returns:
            List of PDF drawing commands
        """
        parts: list[str] = []
        k = self.BEZIER_K
        r, g, b = circle_color

        # 1. Draw circle (fill + stroke)
        parts.append(
            f"{circle_border_color[0]:.4f} {circle_border_color[1]:.4f} "
            f"{circle_border_color[2]:.4f} RG"
        )
        parts.append(f"{circle_border_width:.4f} w")
        parts.append(f"{r:.4f} {g:.4f} {b:.4f} rg")

        # Circle path using Bezier curves
        x0, y0 = cx + radius, cy
        parts.append(f"{x0:.3f} {y0:.3f} m")

        # Right to Top
        parts.append(
            f"{cx + radius:.3f} {cy + radius * k:.3f} "
            f"{cx + radius * k:.3f} {cy + radius:.3f} "
            f"{cx:.3f} {cy + radius:.3f} c"
        )
        # Top to Left
        parts.append(
            f"{cx - radius * k:.3f} {cy + radius:.3f} "
            f"{cx - radius:.3f} {cy + radius * k:.3f} "
            f"{cx - radius:.3f} {cy:.3f} c"
        )
        # Left to Bottom
        parts.append(
            f"{cx - radius:.3f} {cy - radius * k:.3f} "
            f"{cx - radius * k:.3f} {cy - radius:.3f} "
            f"{cx:.3f} {cy - radius:.3f} c"
        )
        # Bottom to Right
        parts.append(
            f"{cx + radius * k:.3f} {cy - radius:.3f} "
            f"{cx + radius:.3f} {cy - radius * k:.3f} "
            f"{cx + radius:.3f} {cy:.3f} c"
        )

        parts.append("h")
        parts.append("B")  # Fill and stroke

        # 2. Draw ID box on top (unless hidden)
        if not no_id_box:
            parts.append("q")
            parts.append("1 1 1 rg")  # White fill
            parts.append("0 0 0 RG")  # Black stroke
            parts.append(f"{id_box_border_width:.1f} w")
            parts.append(
                f"{id_box_x1:.3f} {id_box_y1:.3f} "
                f"{id_box_width:.3f} {id_box_height:.3f} re"
            )
            parts.append("B")
            parts.append("Q")

            # ID box text (centered in box)
            parts.append("BT")
            parts.append(
                f"{id_text_color[0]:.4f} {id_text_color[1]:.4f} "
                f"{id_text_color[2]:.4f} rg"
            )
            parts.append(f"/Helv {id_font_size:.1f} Tf")
            id_text_width = measure_text_width(id_label, id_font_size)
            id_text_x = id_box_x1 + (id_box_width - id_text_width) / 2  # Center in box
            id_text_y = id_box_y1 + (id_box_height - id_font_size) / 2 + 0.3  # Vertically center
            parts.append(f"{id_text_x:.3f} {id_text_y:.3f} Td")
            parts.append(f"({id_label}) Tj")
            parts.append("ET")

        # 3. Draw gear image
        parts.append("q")
        parts.append(
            f"{img_draw_width:.3f} 0 0 {img_draw_height:.3f} "
            f"{img_x:.3f} {img_y:.3f} cm"
        )
        parts.append("/Img Do")
        parts.append("Q")

        # 4. Draw brand text (if provided)
        if brand_text:
            brand_text_width = measure_text_width(brand_text, brand_font_size)
            text_x_brand = cx - brand_text_width / 2 + brand_x_offset
            text_y_brand = cy + radius + brand_y_offset

            parts.append("BT")
            parts.append(
                f"{text_color[0]:.4f} {text_color[1]:.4f} {text_color[2]:.4f} rg"
            )
            parts.append(f"/Helv {brand_font_size:.2f} Tf")
            parts.append(f"{text_x_brand:.3f} {text_y_brand:.3f} Td")
            parts.append(f"({brand_text}) Tj")
            parts.append("ET")

        # 5. Draw model text (supports multi-line with \n, max 3 lines)
        if model_text:
            lines = model_text.split("\n")[:3]  # Limit to 3 lines max
            line_height = model_font_size * 1.2  # Line spacing

            # Calculate base Y position - adjust up if multiple lines
            base_y = cy - radius + model_y_offset
            if len(lines) > 1:
                # Move up to center the stack
                base_y += (len(lines) - 1) * line_height / 2

            for i, line in enumerate(lines):
                line_text_width = measure_text_width(line, model_font_size)
                text_x_model = cx - line_text_width / 2 + model_x_offset
                text_y_model = base_y - i * line_height

                parts.append("BT")
                parts.append(
                    f"{text_color[0]:.4f} {text_color[1]:.4f} {text_color[2]:.4f} rg"
                )
                parts.append(f"/Helv {model_font_size:.2f} Tf")
                parts.append(f"{text_x_model:.3f} {text_y_model:.3f} Td")
                parts.append(f"({line}) Tj")
                parts.append("ET")

        return parts

    # ── Compound rendering (Bluebeam-native 7-component groups) ──────────

    # Scale from canonical 25x30 space to page points.
    # ~28 pts wide by ~34 pts tall — close to Bluebeam's reference proportions.
    COMPOUND_RENDER_SCALE = 1.12

    # Canonical coordinate space dimensions (shared with combined renderer above)
    CANON_W = 25.0
    CANON_H = 30.0

    def render_compound_icon(
        self,
        writer: PdfWriter,
        subject: str,
        center: tuple[float, float],
        id_label: str = "j100",
    ) -> list[dict] | None:
        """
        Render a deployment icon as compound annotation components.

        Each component has its own simple appearance stream that Bluebeam
        can regenerate on move, preventing shape reversion.

        Args:
            writer: PdfWriter to add objects to
            subject: Deployment subject (e.g., "AP - Cisco MR36H")
            center: (cx, cy) center position in page coordinates
            id_label: ID label for top box (e.g., "j100")

        Returns:
            List of component dicts (3-7 items) or None if no config.
            Each dict has: role, subtype, rect, ap_ref, extra_props.
        """
        config = get_icon_config(subject)
        if not config:
            return None

        cx, cy = center

        # Load image if available
        has_image = False
        image_xobj_ref = None
        img_width, img_height = 0, 0
        image_path = config.get("image_path")

        if image_path and not config.get("no_image"):
            full_path = self.gear_icons_dir / image_path
            if full_path.exists():
                circle_color = config.get("circle_color", (0.5, 0.5, 0.5))
                img_data, img_width, img_height = self.load_image(
                    image_path, circle_color
                )
                image_xobj_ref = self.create_image_xobject(
                    writer, img_data, img_width, img_height
                )
                has_image = True

        # Get text values
        model_text = config.get("model_text_override") or get_model_text(subject)
        if config.get("model_uppercase"):
            model_text = model_text.upper()
        brand_text = config.get("brand_text", "")

        # Extract config parameters
        circle_color = config.get("circle_color", (0.22, 0.34, 0.65))
        circle_border_color = config.get("circle_border_color", (0.0, 0.0, 0.0))
        circle_border_width = config.get("circle_border_width", 0.75)
        text_color = config.get("text_color", (1.0, 1.0, 1.0))
        id_text_color = config.get("id_text_color") or circle_color
        id_font_size = config.get("id_font_size", 3.9)
        id_box_border_width = config.get("id_box_border_width", 0.35)
        no_id_box = config.get("no_id_box", False)
        model_font_size = config.get("model_font_size", 2.2)
        brand_font_size = config.get("brand_font_size", 1.8)

        # Compute absolute page rects for all components
        rects = self._compute_component_rects(
            cx, cy, config, img_width, img_height
        )

        components: list[dict] = []

        # 1. Root: ID text (FreeText) — always created
        id_rect = rects["id_text"]
        id_ap = self._render_freetext_ap(
            writer, id_rect, id_label if not no_id_box else "",
            id_font_size, id_text_color,
        )
        components.append({
            "role": "root_id_text",
            "subtype": "/FreeText",
            "rect": id_rect,
            "ap_ref": id_ap,
            "extra_props": {
                "/DA": (
                    f"{id_text_color[0]:.4f} {id_text_color[1]:.4f} "
                    f"{id_text_color[2]:.4f} rg /HelvBld {id_font_size:.2f} Tf"
                ),
                "/Contents": id_label if not no_id_box else "",
                "/C": [],
                "/BS": {"W": 0},
            },
        })

        # 2. ID box border (Square) — unless hidden
        if not no_id_box:
            box_rect = rects["id_box"]
            box_ap = self._render_id_box_ap(writer, box_rect, id_box_border_width)
            components.append({
                "role": "id_box_border",
                "subtype": "/Square",
                "rect": box_rect,
                "ap_ref": box_ap,
                "extra_props": {
                    "/IC": [1.0, 1.0, 1.0],
                    "/C": [0.0, 0.0, 0.0],
                    "/BS": {"W": id_box_border_width},
                    "/RD": id_box_border_width / 2,
                },
            })

        # 3. Container (FreeText) — overall bounding box
        container_rect = rects["container"]
        container_ap = self._render_container_ap(writer, container_rect)
        components.append({
            "role": "container",
            "subtype": "/FreeText",
            "rect": container_rect,
            "ap_ref": container_ap,
            "extra_props": {
                "/DA": "0 0 0 rg /HelvBld 1 Tf",
                "/Contents": "",
                "/C": [],
                "/BS": {"W": 0},
            },
        })

        # 4. Circle
        circle_rect = rects["circle"]
        circle_ap = self._render_circle_ap(
            writer, circle_rect, circle_color, circle_border_color,
            circle_border_width,
        )
        components.append({
            "role": "circle",
            "subtype": "/Circle",
            "rect": circle_rect,
            "ap_ref": circle_ap,
            "extra_props": {
                "/IC": list(circle_color),
                "/C": list(circle_border_color),
                "/BS": {"W": circle_border_width},
                "/RD": circle_border_width / 2,
            },
        })

        # 5. Image (Square) — if available
        if has_image and image_xobj_ref:
            img_rect = rects["image"]
            img_ap = self._render_image_ap(writer, img_rect, image_xobj_ref)
            components.append({
                "role": "image",
                "subtype": "/Square",
                "rect": img_rect,
                "ap_ref": img_ap,
                "extra_props": {
                    "/C": [1.0, 0.0, 0.0],
                    "/BS": {"W": 0},
                },
            })

        # 6. Model text (FreeText) — if available
        if model_text:
            model_rect = rects["model_text"]
            model_ap = self._render_freetext_ap(
                writer, model_rect, model_text, model_font_size, text_color,
            )
            components.append({
                "role": "model_text",
                "subtype": "/FreeText",
                "rect": model_rect,
                "ap_ref": model_ap,
                "extra_props": {
                    "/DA": (
                        f"{text_color[0]:.4f} {text_color[1]:.4f} "
                        f"{text_color[2]:.4f} rg /HelvBld {model_font_size:.2f} Tf"
                    ),
                    "/Contents": model_text,
                    "/C": [],
                    "/BS": {"W": 0},
                },
            })

        # 7. Brand text (FreeText) — if available
        if brand_text:
            brand_rect = rects["brand_text"]
            brand_ap = self._render_freetext_ap(
                writer, brand_rect, brand_text, brand_font_size, text_color,
            )
            components.append({
                "role": "brand_text",
                "subtype": "/FreeText",
                "rect": brand_rect,
                "ap_ref": brand_ap,
                "extra_props": {
                    "/DA": (
                        f"{text_color[0]:.4f} {text_color[1]:.4f} "
                        f"{text_color[2]:.4f} rg /HelvBld {brand_font_size:.2f} Tf"
                    ),
                    "/Contents": brand_text,
                    "/C": [],
                    "/BS": {"W": 0},
                },
            })

        return components

    def _compute_component_rects(
        self,
        cx: float,
        cy: float,
        config: dict[str, Any],
        img_width: int,
        img_height: int,
    ) -> dict[str, list[float]]:
        """
        Compute absolute page rects for all compound annotation components.

        Reuses the canonical 25x30 coordinate space layout math from
        _create_appearance_stream, transforming to absolute page coords.

        Args:
            cx: Page X center of the icon
            cy: Page Y center of the icon
            config: Icon configuration dictionary
            img_width: Image width in pixels (0 if no image)
            img_height: Image height in pixels (0 if no image)

        Returns:
            Dict mapping role name to [x1, y1, x2, y2] absolute page rects.
        """
        scale = self.COMPOUND_RENDER_SCALE
        half_w = (self.CANON_W * scale) / 2
        half_h = (self.CANON_H * scale) / 2

        # Origin of canonical (0,0) in page coords
        ox = cx - half_w
        oy = cy - half_h

        def to_page_rect(c_x1: float, c_y1: float, c_w: float, c_h: float) -> list[float]:
            return [
                ox + c_x1 * scale,
                oy + c_y1 * scale,
                ox + (c_x1 + c_w) * scale,
                oy + (c_y1 + c_h) * scale,
            ]

        # Canonical layout (same math as _create_appearance_stream lines 286-328)
        id_box_height = config.get("id_box_height", 2.3)
        id_box_width_ratio = config.get("id_box_width_ratio", 0.41)
        id_box_y_offset = config.get("id_box_y_offset", 0.0)
        img_scale_ratio = config.get("img_scale_ratio", 0.70)

        canon_cx = self.CANON_W / 2  # 12.5
        id_box_width = self.CANON_W * id_box_width_ratio
        id_box_x1 = canon_cx - id_box_width / 2
        id_box_y1 = self.CANON_H - id_box_height + id_box_y_offset

        circle_top = id_box_y1 + 2
        circle_area_height = circle_top  # circle_bottom = 0
        radius = min(self.CANON_W, circle_area_height) / 2 - 0.3
        canon_cy = circle_top - radius

        rects: dict[str, list[float]] = {}

        # Container — full canonical space
        rects["container"] = to_page_rect(0, 0, self.CANON_W, self.CANON_H)

        # ID box (Square border)
        rects["id_box"] = to_page_rect(
            id_box_x1, id_box_y1, id_box_width, id_box_height
        )

        # ID text (FreeText) — full width, covers ID box area with padding
        rects["id_text"] = to_page_rect(
            0, id_box_y1 - 2, self.CANON_W, id_box_height + 4
        )

        # Circle
        rects["circle"] = to_page_rect(
            canon_cx - radius, canon_cy - radius, 2 * radius, 2 * radius
        )

        # Image
        if img_width > 0 and img_height > 0:
            img_scale = (radius * img_scale_ratio) / max(img_width, img_height)
            img_draw_w = img_width * img_scale
            img_draw_h = img_height * img_scale
            img_x_off = config.get("img_x_offset", 0.0)
            img_y_off = config.get("img_y_offset", 0.0)
            img_cx = canon_cx - img_draw_w / 2 + img_x_off
            img_cy = canon_cy - img_draw_h / 2 + img_y_off
            rects["image"] = to_page_rect(img_cx, img_cy, img_draw_w, img_draw_h)

        # Model text — below circle, full width
        model_y_offset = config.get("model_y_offset", 2.5)
        model_font_size = config.get("model_font_size", 2.2)
        model_text_y = canon_cy - radius + model_y_offset - model_font_size * 2
        rects["model_text"] = to_page_rect(
            0, max(model_text_y, 0), self.CANON_W, model_font_size * 5
        )

        # Brand text — upper area of circle, full width
        brand_y_offset = config.get("brand_y_offset", -3.2)
        brand_font_size = config.get("brand_font_size", 1.8)
        brand_text_y = canon_cy + radius + brand_y_offset - brand_font_size
        rects["brand_text"] = to_page_rect(
            0, brand_text_y, self.CANON_W, brand_font_size * 4
        )

        return rects

    def _make_form_stream(
        self,
        writer: PdfWriter,
        bbox: list[float],
        content_bytes: bytes,
        resources: DictionaryObject | None = None,
    ) -> IndirectObject:
        """
        Create a PDF Form XObject with absolute BBox and Matrix.

        Uses absolute BBox [x1,y1,x2,y2] with Matrix [1,0,0,1,-x1,-y1]
        so content streams draw at absolute page coordinates and the Matrix
        translates them into form-local space.

        Args:
            writer: PdfWriter to add the object to
            bbox: Absolute bounding box [x1, y1, x2, y2]
            content_bytes: Encoded content stream bytes
            resources: Optional Resources dictionary

        Returns:
            IndirectObject reference to the form stream
        """
        x1, y1 = bbox[0], bbox[1]

        ap_stream = StreamObject()
        ap_stream[NameObject("/Type")] = NameObject("/XObject")
        ap_stream[NameObject("/Subtype")] = NameObject("/Form")
        ap_stream[NameObject("/FormType")] = NumberObject(1)
        ap_stream[NameObject("/BBox")] = ArrayObject([
            FloatObject(bbox[0]), FloatObject(bbox[1]),
            FloatObject(bbox[2]), FloatObject(bbox[3]),
        ])
        ap_stream[NameObject("/Matrix")] = ArrayObject([
            NumberObject(1), NumberObject(0),
            NumberObject(0), NumberObject(1),
            FloatObject(-x1), FloatObject(-y1),
        ])

        if resources:
            ap_stream[NameObject("/Resources")] = resources

        ap_stream._data = content_bytes
        return writer._add_object(ap_stream)

    def _make_font_resource(self) -> DictionaryObject:
        """Create a Resources dict with Helvetica-Bold font as /HelvBld."""
        resources = DictionaryObject()
        font_dict = DictionaryObject()
        helv = DictionaryObject()
        helv[NameObject("/Type")] = NameObject("/Font")
        helv[NameObject("/Subtype")] = NameObject("/Type1")
        helv[NameObject("/BaseFont")] = NameObject("/Helvetica-Bold")
        font_dict[NameObject("/HelvBld")] = helv
        resources[NameObject("/Font")] = font_dict
        return resources

    def _render_circle_ap(
        self,
        writer: PdfWriter,
        rect: list[float],
        circle_color: tuple[float, float, float],
        border_color: tuple[float, float, float],
        border_width: float,
    ) -> IndirectObject:
        """Create circle appearance stream at absolute coordinates."""
        x1, y1, x2, y2 = rect
        ccx = (x1 + x2) / 2
        ccy = (y1 + y2) / 2
        radius = min(x2 - x1, y2 - y1) / 2

        k = self.BEZIER_K
        r, g, b = circle_color
        parts = [
            f"{border_color[0]:.4f} {border_color[1]:.4f} {border_color[2]:.4f} RG",
            f"{border_width:.4f} w",
            f"{r:.4f} {g:.4f} {b:.4f} rg",
            f"{ccx + radius:.3f} {ccy:.3f} m",
            f"{ccx + radius:.3f} {ccy + radius * k:.3f} "
            f"{ccx + radius * k:.3f} {ccy + radius:.3f} "
            f"{ccx:.3f} {ccy + radius:.3f} c",
            f"{ccx - radius * k:.3f} {ccy + radius:.3f} "
            f"{ccx - radius:.3f} {ccy + radius * k:.3f} "
            f"{ccx - radius:.3f} {ccy:.3f} c",
            f"{ccx - radius:.3f} {ccy - radius * k:.3f} "
            f"{ccx - radius * k:.3f} {ccy - radius:.3f} "
            f"{ccx:.3f} {ccy - radius:.3f} c",
            f"{ccx + radius * k:.3f} {ccy - radius:.3f} "
            f"{ccx + radius:.3f} {ccy - radius * k:.3f} "
            f"{ccx + radius:.3f} {ccy:.3f} c",
            "h B",
        ]
        content = "\n".join(parts).encode("latin-1")
        return self._make_form_stream(writer, rect, content)

    def _render_id_box_ap(
        self,
        writer: PdfWriter,
        rect: list[float],
        border_width: float,
    ) -> IndirectObject:
        """Create white rectangle with black border at absolute coordinates."""
        x1, y1, x2, y2 = rect
        parts = [
            "1 1 1 rg",
            "0 0 0 RG",
            f"{border_width:.2f} w",
            f"{x1:.3f} {y1:.3f} {x2 - x1:.3f} {y2 - y1:.3f} re",
            "B",
        ]
        content = "\n".join(parts).encode("latin-1")
        return self._make_form_stream(writer, rect, content)

    def _render_image_ap(
        self,
        writer: PdfWriter,
        rect: list[float],
        image_xobj_ref: IndirectObject,
    ) -> IndirectObject:
        """Create image appearance stream at absolute coordinates."""
        x1, y1, x2, y2 = rect
        w = x2 - x1
        h = y2 - y1
        content = f"q {w:.3f} 0 0 {h:.3f} {x1:.3f} {y1:.3f} cm /Img Do Q".encode(
            "latin-1"
        )

        resources = DictionaryObject()
        xobject_dict = DictionaryObject()
        xobject_dict[NameObject("/Img")] = image_xobj_ref
        resources[NameObject("/XObject")] = xobject_dict

        return self._make_form_stream(writer, rect, content, resources)

    def _render_freetext_ap(
        self,
        writer: PdfWriter,
        rect: list[float],
        text: str,
        font_size: float,
        text_color: tuple[float, float, float],
    ) -> IndirectObject:
        """Create FreeText appearance stream with centered text at absolute coords."""
        x1, y1, x2, y2 = rect
        tcx = (x1 + x2) / 2
        tcy = (y1 + y2) / 2
        r, g, b = text_color

        lines = text.split("\n")[:3] if text else [""]
        line_height = font_size * 1.2

        parts = ["BT", f"{r:.4f} {g:.4f} {b:.4f} rg", f"/HelvBld {font_size:.2f} Tf"]

        base_y = tcy - font_size / 2 + 0.3
        if len(lines) > 1:
            base_y += (len(lines) - 1) * line_height / 2

        for i, line in enumerate(lines):
            line_w = measure_text_width(line, font_size)
            lx = tcx - line_w / 2
            ly = base_y - i * line_height
            parts.append(f"1 0 0 1 {lx:.3f} {ly:.3f} Tm")
            parts.append(f"({line}) Tj")

        parts.append("ET")

        content = "\n".join(parts).encode("latin-1")
        return self._make_form_stream(writer, rect, content, self._make_font_resource())

    def _render_container_ap(
        self,
        writer: PdfWriter,
        rect: list[float],
    ) -> IndirectObject:
        """Create empty container appearance (invisible bounding box)."""
        return self._make_form_stream(writer, rect, b"", self._make_font_resource())
