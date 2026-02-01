# Feature: Config-Driven Icon Rendering System

The following plan should be complete, but it's important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils, types and models. Import from the right files etc.

## Feature Description

Implement a configuration-driven icon rendering system that enables rendering all 118 deployment icons with pixel-perfect visual appearance matching the reference PDFs. The system uses a hierarchical configuration structure with category-level defaults and per-icon overrides, eliminating code duplication while allowing precise per-icon tuning.

The MR36H icon has already been successfully rendered with tuned parameters in `backend/scripts/test_mr36h_icon.py`. This plan extracts those parameters into a reusable configuration system and integrates it into the main annotation replacement pipeline.

## User Story

As a developer/maintainer,
I want a configuration-driven icon rendering system,
So that I can tune each of the 118 deployment icons without writing duplicate rendering code, and the system remains maintainable and extensible.

## Problem Statement

Currently:
- The MR36H icon rendering logic exists in a one-off test script (`test_mr36h_icon.py`)
- Visual parameters are hardcoded in that script
- Extending to 118 icons would require massive code duplication (one script per icon)
- No centralized way to configure icon appearance parameters
- The `annotation_replacer.py` creates simple colored shapes, not the rich visual icons needed

## Solution Statement

Create a configuration-driven rendering engine:
1. **Configuration file** (`icon_config.py`) - Centralized Python dict with category defaults and per-icon overrides
2. **Icon renderer service** (`icon_renderer.py`) - Single rendering engine that reads config and generates PDF appearance streams
3. **Integration** - Update `annotation_replacer.py` to use the icon renderer for rich visual icons
4. **Test infrastructure** - Scripts to render individual icons for visual verification

## Feature Metadata

**Feature Type**: New Capability / Enhancement
**Estimated Complexity**: Medium
**Primary Systems Affected**:
- `backend/app/services/` (new icon_renderer.py, icon_config.py)
- `backend/app/services/annotation_replacer.py` (integration)
**Dependencies**:
- PyPDF2 (for appearance stream construction)
- Pillow (for image processing)
- Existing gear icons in `samples/icons/gearIcons/`

---

## CONTEXT REFERENCES

### Relevant Codebase Files IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

- `backend/scripts/test_mr36h_icon.py` (entire file) - **CRITICAL**: Contains the working MR36H rendering with all tuned parameters. Extract these exact parameters.
- `backend/app/services/annotation_replacer.py` (lines 1-200) - Current annotation replacement logic to integrate with
- `backend/app/services/appearance_extractor.py` (entire file) - Pattern for service class structure
- `backend/app/services/btx_loader.py` (lines 1-100, 400-473) - Pattern for service initialization and loading data
- `backend/app/models/mapping.py` (entire file) - Pattern for Pydantic model definitions
- `backend/tests/test_annotation_replacer.py` (lines 1-100) - Pattern for mocking and testing services
- `backend/data/mapping.md` (entire file) - List of all deployment subjects that need rendering configs

### New Files to Create

- `backend/app/services/icon_config.py` - Icon configuration with category defaults and per-icon overrides
- `backend/app/services/icon_renderer.py` - Unified rendering engine that creates PDF appearance streams
- `backend/scripts/test_icon_render.py` - Test script to render any icon by name for visual verification
- `backend/tests/test_icon_renderer.py` - Unit tests for icon renderer service

### Relevant Documentation YOU SHOULD READ THESE BEFORE IMPLEMENTING!

- PyPDF2 StreamObject documentation for appearance stream construction
- PDF Reference 1.7 Section 8.4 (Appearance Streams) for understanding BBox, Matrix, and content streams

---

## SAMPLES/ICONS FOLDER STRUCTURE - CRITICAL REFERENCE

**Base Path:** `samples/icons/`

This folder contains ALL source materials for icon rendering:

```
samples/icons/
├── bidIcons/                    # PNG screenshots of bid icons (reference only)
│   ├── accessPoints.png
│   ├── cctv.png
│   ├── emergencyAnnounce.png
│   ├── hardlines.png
│   ├── IPTV.png
│   ├── p2p.png
│   └── phones.png
│
├── deploymentIcons/             # PDF files with VISUAL REFERENCE for rendered icons
│   ├── accessPoints.pdf         # Contains j100, j101, etc. - AP icon visual targets
│   ├── cameras.pdf              # CCTV/camera icon visual targets
│   ├── hardlines.pdf            # Hardline icon visual targets
│   ├── p2p.pdf                  # Point-to-point icon visual targets
│   └── switches.pdf             # Switch/distribution icon visual targets
│
└── gearIcons/                   # PNG product images to EMBED in rendered icons
    ├── APs/                     # Access Point product images
    │   ├── AP - Cisco 9120.png
    │   ├── AP - Cisco 9124.png
    │   ├── AP - Cisco 9166.png
    │   ├── AP - Cisco MR36H.png      # ← Used for MR36H icon
    │   ├── AP - Cisco MR78.png
    │   ├── AP - Cisco Marlin 4.png
    │   └── AP - DB10.png
    │
    ├── Hardlines/               # Cable/hardline product images
    │   ├── CAT6 Cable.png
    │   ├── LC SM.png
    │   ├── SC SM.png
    │   └── ST SM.png
    │
    ├── Hardware/                # Mounting hardware images (26 items + Archive/)
    │   ├── AAA Adjustable Base Cheeseboro.png
    │   ├── MR30H MR36H Mount.png
    │   ├── Pole Double Cheeseboros.png
    │   ├── Speaker Stand.png
    │   └── ... (22 more items)
    │
    ├── Misc/                    # Miscellaneous equipment (30 items)
    │   ├── AXIS P5655-E.png          # Camera
    │   ├── AXIS S9302 Workstation.png
    │   ├── Brightsign XT1144.png     # IPTV
    │   ├── EAS Laptop.png            # Emergency Announce
    │   ├── Emergency Announce Command Unit.png
    │   ├── Emergency Announce Trigger Box.png
    │   ├── Meraki MT15.png
    │   ├── Meraki MT40.png
    │   ├── Yealink P965.png          # VoIP phones
    │   ├── Yealink T29G.png
    │   └── ... (20 more items)
    │
    ├── P2Ps/                    # Point-to-Point transceivers (9 items)
    │   ├── P2P - Ubiquiti GigaBeam LR.png
    │   ├── P2P - Ubiquiti GigaBeam.png
    │   ├── P2P - Ubiquiti LiteAP AC.png
    │   ├── P2P - Ubiquiti NanoBeam.png
    │   ├── P2P - Ubiquiti Wave AP Micro.png
    │   ├── P2P - Ubiquiti Wave Nano.png
    │   ├── P2P - Ubiquiti Wave Pico.png
    │   └── P2P - PrismStation w_ RF Elements 60° Horn.png
    │
    └── Switches/                # Network switches/distribution (23 items)
        ├── Cisco 9200 12-P.png
        ├── Cisco 9300 24-P.png
        ├── Cisco 9300 48-P.png
        ├── Cisco 9500 48-P.png
        ├── Cisco Micro 4-P.png
        ├── Cisco MX.png
        ├── IDF.png
        ├── MikroTik Hex.png
        ├── Mini NOC.png
        ├── NOC.png
        ├── Netonix 6-P DC.png
        ├── Netonix 8-P DC.png
        ├── Netonix 12-P AC.png
        ├── Starlink.png
        └── ... (9 more items)
```

### How to Use These Resources

**1. Visual Reference (deploymentIcons/*.pdf):**
- Open `accessPoints.pdf` to see how MR36H icon should look (labeled "j100")
- These PDFs show the EXACT visual appearance to match
- Each icon has an ID label (j100, j101, etc.) for reference

**2. Gear Images (gearIcons/**/*.png):**
- These PNG files are EMBEDDED in the rendered icons
- The filename corresponds to the deployment subject
- Example: "AP - Cisco MR36H" uses `gearIcons/APs/AP - Cisco MR36H.png`

**3. Mapping Deployment Subject → Gear Image:**

| Deployment Subject | Gear Image Path |
|--------------------|-----------------|
| `AP - Cisco MR36H` | `APs/AP - Cisco MR36H.png` |
| `AP - Cisco 9120` | `APs/AP - Cisco 9120.png` |
| `AP - Cisco 9166I` | `APs/AP - Cisco 9166.png` |
| `AP - Cisco 9166D` | `APs/AP - Cisco 9166.png` |
| `AP - Cisco MR78` | `APs/AP - Cisco MR78.png` |
| `AP - Cisco Marlin 4` | `APs/AP - Cisco Marlin 4.png` |
| `AP - Cisco DB10` | `APs/AP - DB10.png` |
| `SW - Cisco Micro 4P` | `Switches/Cisco Micro 4-P.png` |
| `SW - Cisco 9200 12P` | `Switches/Cisco 9200 12-P.png` |
| `SW - IDF Cisco 9300 24X` | `Switches/Cisco 9300 24-P.png` |
| `DIST - Mini NOC` | `Switches/Mini NOC.png` |
| `DIST - Standard NOC` | `Switches/NOC.png` |
| `DIST - Micro NOC` | `Switches/Mini NOC.png` |
| `DIST - MikroTik Hex` | `Switches/MikroTik Hex.png` |
| `DIST - Starlink` | `Switches/Starlink.png` |
| `P2P - Ubiquiti NanoBeam` | `P2Ps/P2P - Ubiquiti NanoBeam.png` |
| `P2P - Ubiquiti LiteAP` | `P2Ps/P2P - Ubiquiti LiteAP AC.png` |
| `P2P - Ubiquiti GigaBeam` | `P2Ps/P2P - Ubiquiti GigaBeam.png` |
| `P2P - Ubiquiti GigaBeam LR` | `P2Ps/P2P - Ubiquiti GigaBeam LR.png` |
| `VOIP - Yealink T29G` | `Misc/Yealink T29G.png` |
| `VOIP - Yealink CP965` | `Misc/Yealink P965.png` |
| `CCTV - AXIS P5655-E` | `Misc/AXIS P5655-E.png` |
| `CCTV - AXIS S9302` | `Misc/AXIS S9302 Workstation.png` |
| `EAS - Command Unit` | `Misc/Emergency Announce Command Unit.png` |
| `EAS - Laptop` | `Misc/EAS Laptop.png` |
| `EAS - Trigger Box` | `Misc/Emergency Announce Trigger Box.png` |
| `IPTV - BrightSign XT1144` | `Misc/Brightsign XT1144.png` |

**4. Icons WITHOUT Gear Images (use colored shapes only):**
- `FIBER` - No product image, use colored shape
- `INFRA - Fiber Patch Panel` - No product image

**5. Hardlines - All use CAT6 Cable image:**
All `HL - *` deployment subjects use the same image: `Hardlines/CAT6 Cable.png`

### Path Constants for Implementation

```python
# In icon_config.py
from pathlib import Path

# Base paths (relative to project root)
SAMPLES_ICONS_DIR = Path("samples/icons")
GEAR_ICONS_DIR = SAMPLES_ICONS_DIR / "gearIcons"
DEPLOYMENT_ICONS_DIR = SAMPLES_ICONS_DIR / "deploymentIcons"

# Category subdirectories in gearIcons/
GEAR_ICON_CATEGORIES = {
    "APs": GEAR_ICONS_DIR / "APs",
    "Switches": GEAR_ICONS_DIR / "Switches",
    "P2Ps": GEAR_ICONS_DIR / "P2Ps",
    "Hardlines": GEAR_ICONS_DIR / "Hardlines",
    "Hardware": GEAR_ICONS_DIR / "Hardware",
    "Misc": GEAR_ICONS_DIR / "Misc",
}
```

---

### Patterns to Follow

**Service Class Pattern (from btx_loader.py):**
```python
class ServiceName:
    """Docstring with description."""

    def __init__(self, param: Type):
        """Initialize with dependencies."""
        self.param = param
        self._loaded = False

    def load(self) -> None:
        """Load/initialize the service."""
        # ... loading logic
        self._loaded = True

    def is_loaded(self) -> bool:
        """Check if service is loaded."""
        return self._loaded
```

**Configuration Dict Pattern (from memories.md decision):**
```python
ICON_CONFIGS = {
    "_defaults": {
        "APs": {
            "circle_color": (0.22, 0.34, 0.65),
            "id_box_width_ratio": 0.55,
            "img_scale": 0.70,
            # ... category defaults
        },
    },
    # Per-icon overrides (only what differs from category)
    "AP - Cisco MR36H": {
        "model_y_offset": 2.5,
    },
}
```

**Test Pattern (from test_annotation_replacer.py):**
```python
class MockServiceName:
    """Mock service for testing."""
    def __init__(self, data=None):
        self.data = data or {}

    def method(self, arg):
        return self.data.get(arg)

class TestServiceName:
    """Test suite for ServiceName."""

    def test_initialization(self):
        """Test service initialization."""
        service = ServiceName(param)
        assert service.param == param
```

**Naming Conventions:**
- Service files: `snake_case.py` (e.g., `icon_renderer.py`)
- Service classes: `PascalCase` (e.g., `IconRenderer`)
- Config dicts: `SCREAMING_SNAKE_CASE` (e.g., `ICON_CONFIGS`)
- Methods: `snake_case` (e.g., `render_icon()`)

---

## IMPLEMENTATION PLAN

### Phase 1: Configuration Foundation

Create the icon configuration module with:
1. Category defaults extracted from test_mr36h_icon.py visual parameters
2. Per-icon override structure for fine-tuning
3. Helper function to merge category defaults with overrides
4. Icon-to-image path mapping

### Phase 2: Icon Renderer Service

Create the rendering engine that:
1. Takes deployment subject and annotation rect as input
2. Looks up configuration (merges category default + icon override)
3. Creates PDF appearance stream with:
   - Blue filled circle
   - ID box overlay
   - Gear image embedding
   - CISCO text (or brand)
   - Model text
4. Returns the appearance stream ready for PDF annotation

### Phase 3: Integration with Annotation Replacer

Update the annotation replacement pipeline to:
1. Use IconRenderer for visual appearance generation
2. Fall back to simple colored shapes for unmapped icons
3. Preserve existing coordinate/size logic

### Phase 4: Testing & Validation

1. Unit tests for IconRenderer service
2. Test script to render individual icons for visual verification
3. Integration test with BidMap.pdf conversion

---

## STEP-BY-STEP TASKS

IMPORTANT: Execute every task in order, top to bottom. Each task is atomic and independently testable.

### Task 1: CREATE `backend/app/services/icon_config.py`

**IMPLEMENT**: Configuration module with:

1. **ICON_CATEGORIES** dict mapping deployment subjects to categories:
```python
ICON_CATEGORIES = {
    "AP - Cisco MR36H": "APs",
    "AP - Cisco 9120": "APs",
    "AP - Cisco 9166I": "APs",
    "AP - Cisco 9166D": "APs",
    "AP - Cisco MR78": "APs",
    "AP - Cisco Marlin 4": "APs",
    "AP - Cisco DB10": "APs",
    "SW - Cisco Micro 4P": "Switches",
    "SW - Cisco 9200 12P": "Switches",
    # ... (extract all deployment subjects from mapping.md)
}
```

2. **CATEGORY_DEFAULTS** dict with rendering parameters per category:
```python
CATEGORY_DEFAULTS = {
    "APs": {
        "circle_color": (0.22, 0.34, 0.65),  # Navy blue from MR36H
        "circle_border_width": 0.5,
        "circle_border_color": (0.0, 0.0, 0.0),
        "id_box_height": 4.0,
        "id_box_width_ratio": 0.55,
        "id_box_border_width": 0.6,
        "img_scale_ratio": 0.70,
        "brand_text": "CISCO",
        "brand_font_size": 1.9,
        "brand_y_offset": -4.0,  # from circle top
        "brand_x_offset": -0.2,
        "model_font_size": 1.6,
        "model_y_offset": 2.5,  # from circle bottom
        "model_x_offset": -0.7,
        "font_name": "/Helvetica-Bold",
        "text_color": (1.0, 1.0, 1.0),  # White
        "id_text_color": None,  # Same as circle_color if None
    },
    "Switches": {
        "circle_color": (0.15, 0.45, 0.25),  # Green for switches
        # ... similar structure
    },
    # ... other categories
}
```

3. **ICON_OVERRIDES** dict for per-icon fine-tuning:
```python
ICON_OVERRIDES = {
    "AP - Cisco MR36H": {
        # MR36H uses category defaults, no overrides needed
    },
    "AP - Cisco 9120": {
        "model_y_offset": 3.0,  # Taller image needs adjustment
        "img_scale_ratio": 0.65,
    },
    # ... other icons with specific tuning

    # === Hardlines ===
    # All hardlines use same image (CAT6 Cable.png) and same color
    # Differentiated only by model text (e.g., "Artist", "Production") and ID label
    # No overrides needed - they all use Hardlines category defaults
}
```

4. **ICON_IMAGE_PATHS** dict mapping deployment subject to gear icon filename:
```python
# Maps deployment subject to relative path from gearIcons/
ICON_IMAGE_PATHS = {
    # === Access Points ===
    "AP - Cisco MR36H": "APs/AP - Cisco MR36H.png",
    "AP - Cisco 9120": "APs/AP - Cisco 9120.png",
    "AP - Cisco 9166I": "APs/AP - Cisco 9166.png",  # Same image for I and D variants
    "AP - Cisco 9166D": "APs/AP - Cisco 9166.png",
    "AP - Cisco MR78": "APs/AP - Cisco MR78.png",
    "AP - Cisco Marlin 4": "APs/AP - Cisco Marlin 4.png",
    "AP - Cisco DB10": "APs/AP - DB10.png",  # Note: filename is "AP - DB10" not "AP - Cisco DB10"

    # === Switches / Distribution ===
    "SW - Cisco Micro 4P": "Switches/Cisco Micro 4-P.png",
    "SW - Cisco 9200 12P": "Switches/Cisco 9200 12-P.png",
    "SW - IDF Cisco 9300 24X": "Switches/Cisco 9300 24-P.png",
    "DIST - Mini NOC": "Switches/Mini NOC.png",
    "DIST - Micro NOC": "Switches/Mini NOC.png",  # Same as Mini NOC
    "DIST - Standard NOC": "Switches/NOC.png",
    "DIST - MikroTik Hex": "Switches/MikroTik Hex.png",
    "DIST - Starlink": "Switches/Starlink.png",
    "DIST - Pelican NOC": "Switches/NOC.png",  # Use standard NOC image

    # === Point-to-Points ===
    "P2P - Ubiquiti NanoBeam": "P2Ps/P2P - Ubiquiti NanoBeam.png",
    "P2P - Ubiquiti LiteAP": "P2Ps/P2P - Ubiquiti LiteAP AC.png",
    "P2P - Ubiquiti GigaBeam": "P2Ps/P2P - Ubiquiti GigaBeam.png",
    "P2P - Ubiquiti GigaBeam LR": "P2Ps/P2P - Ubiquiti GigaBeam LR.png",

    # === IoT / Misc ===
    "VOIP - Yealink T29G": "Misc/Yealink T29G.png",
    "VOIP - Yealink CP965": "Misc/Yealink P965.png",  # Note: filename is "P965" not "CP965"
    "CCTV - AXIS P5655-E": "Misc/AXIS P5655-E.png",
    "CCTV - AXIS S9302": "Misc/AXIS S9302 Workstation.png",
    "EAS - Command Unit": "Misc/Emergency Announce Command Unit.png",
    "EAS - Laptop": "Misc/EAS Laptop.png",
    "EAS - Trigger Box": "Misc/Emergency Announce Trigger Box.png",
    "IPTV - BrightSign XT1144": "Misc/Brightsign XT1144.png",

    # === Hardlines (all use CAT6 Cable image) ===
    "HL - Artist": "Hardlines/CAT6 Cable.png",
    "HL - Production": "Hardlines/CAT6 Cable.png",
    "HL - PoS": "Hardlines/CAT6 Cable.png",
    "HL - Access Control": "Hardlines/CAT6 Cable.png",
    "HL - Sponsor": "Hardlines/CAT6 Cable.png",
    "HL - General Internet": "Hardlines/CAT6 Cable.png",
    "HL - Audio": "Hardlines/CAT6 Cable.png",
    "HL - Emergency Announce System": "Hardlines/CAT6 Cable.png",
    "HL - WAN": "Hardlines/CAT6 Cable.png",

    # === Cables (NO gear images) ===
    "FIBER": None,

    # === Miscellaneous (NO gear images) ===
    "INFRA - Fiber Patch Panel": None,
}
```

5. **Helper function** `get_icon_config(subject: str) -> dict`:
```python
def get_icon_config(subject: str) -> dict:
    """Get merged config for an icon (category defaults + icon overrides)."""
    category = ICON_CATEGORIES.get(subject)
    if not category:
        return {}

    config = CATEGORY_DEFAULTS.get(category, {}).copy()
    overrides = ICON_OVERRIDES.get(subject, {})
    config.update(overrides)
    config["image_path"] = ICON_IMAGE_PATHS.get(subject)
    config["category"] = category
    return config
```

6. **Helper function** `get_model_text(subject: str) -> str`:
```python
def get_model_text(subject: str) -> str:
    """Extract model text from deployment subject (e.g., 'AP - Cisco MR36H' -> 'MR36H')."""
    # Handle different naming patterns
    if " - " in subject:
        parts = subject.split(" - ")
        if len(parts) >= 2:
            # "AP - Cisco MR36H" -> "Cisco MR36H" -> "MR36H"
            model_part = parts[-1]
            # Remove brand prefix if present
            for brand in ["Cisco ", "Ubiquiti ", "Axis "]:
                if model_part.startswith(brand):
                    return model_part[len(brand):]
            return model_part
    return subject

# Examples:
# "AP - Cisco MR36H" -> "MR36H"
# "HL - Artist" -> "Artist"
# "HL - Production" -> "Production"
# "P2P - Ubiquiti NanoBeam" -> "NanoBeam"
# "DIST - Mini NOC" -> "Mini NOC"
```

**IMPORTS**:
```python
from pathlib import Path
```

**GOTCHA**: The image paths are relative to `samples/icons/gearIcons/`. The renderer service will need to resolve the full path.

**VALIDATE**:
```bash
cd backend && python -c "from app.services.icon_config import get_icon_config, get_model_text; c = get_icon_config('AP - Cisco MR36H'); print(f'circle_color={c.get(\"circle_color\")}'); print(f'model={get_model_text(\"AP - Cisco MR36H\")}')"
```

Expected output:
```
circle_color=(0.22, 0.34, 0.65)
model=MR36H
```

---

### Task 2: CREATE `backend/app/services/icon_renderer.py`

**IMPLEMENT**: Icon rendering service that creates PDF appearance streams.

**PATTERN**: Mirror the structure from `test_mr36h_icon.py` but parameterized:

```python
"""
Icon renderer service.

Creates PDF appearance streams for deployment icons with:
- Blue filled circle background
- ID box label at top
- Product image in center
- Brand text (e.g., "CISCO")
- Model text (e.g., "MR36H")
"""

import io
import logging
import zlib
from pathlib import Path
from typing import Any

from PIL import Image
from PyPDF2 import PdfWriter
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

from app.services.icon_config import get_icon_config, get_model_text, ICON_IMAGE_PATHS

logger = logging.getLogger(__name__)


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
        """Check if renderer can render the given subject."""
        config = get_icon_config(subject)
        if not config:
            return False
        image_path = config.get("image_path")
        if not image_path:
            return False
        full_path = self.gear_icons_dir / image_path
        return full_path.exists()

    def load_image(self, image_path: str, bg_color: tuple[float, float, float]) -> tuple[bytes, int, int]:
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
            if img.mode in ('RGBA', 'P'):
                background = Image.new('RGB', img.size, bg_rgb)
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])
                else:
                    img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

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
        """Create PDF XObject Image from raw RGB data."""
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
        model_text = get_model_text(subject)
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
        config: dict,
        image_xobject_ref: IndirectObject,
        img_width: int,
        img_height: int,
        model_text: str,
        brand_text: str,
        id_label: str,
    ) -> IndirectObject:
        """Create the PDF appearance stream with all visual elements."""
        x1, y1, x2, y2 = rect
        width = x2 - x1
        height = y2 - y1

        # Extract config parameters
        circle_color = config.get("circle_color", (0.22, 0.34, 0.65))
        circle_border_width = config.get("circle_border_width", 0.5)
        circle_border_color = config.get("circle_border_color", (0.0, 0.0, 0.0))
        id_box_height = config.get("id_box_height", 4.0)
        id_box_width_ratio = config.get("id_box_width_ratio", 0.55)
        id_box_border_width = config.get("id_box_border_width", 0.6)
        img_scale_ratio = config.get("img_scale_ratio", 0.70)
        brand_font_size = config.get("brand_font_size", 1.9)
        brand_y_offset = config.get("brand_y_offset", -4.0)
        brand_x_offset = config.get("brand_x_offset", -0.2)
        model_font_size = config.get("model_font_size", 1.6)
        model_y_offset = config.get("model_y_offset", 2.5)
        model_x_offset = config.get("model_x_offset", -0.7)
        text_color = config.get("text_color", (1.0, 1.0, 1.0))
        id_text_color = config.get("id_text_color") or circle_color

        # Layout calculations
        cx = (x1 + x2) / 2
        id_box_width = width * id_box_width_ratio
        id_box_x1 = cx - id_box_width / 2
        id_box_x2 = cx + id_box_width / 2
        id_box_y1 = y2 - id_box_height - 1
        id_box_y2 = y2 - 1

        # Circle overlaps into ID box by 2px
        circle_top = id_box_y1 + 2
        circle_bottom = y1
        circle_area_height = circle_top - circle_bottom

        radius = min(width, circle_area_height) / 2 - 0.3
        cy = circle_top - radius

        # Image dimensions
        img_scale = (radius * img_scale_ratio) / max(img_width, img_height)
        img_draw_width = img_width * img_scale
        img_draw_height = img_height * img_scale
        img_x = cx - img_draw_width / 2
        img_y = cy - img_draw_height / 2

        # Build content stream
        content_parts = self._build_content_stream(
            cx=cx, cy=cy, radius=radius,
            circle_color=circle_color,
            circle_border_color=circle_border_color,
            circle_border_width=circle_border_width,
            id_box_x1=id_box_x1, id_box_y1=id_box_y1,
            id_box_width=id_box_width, id_box_height=id_box_height,
            id_box_border_width=id_box_border_width,
            id_label=id_label, id_text_color=id_text_color,
            img_x=img_x, img_y=img_y,
            img_draw_width=img_draw_width, img_draw_height=img_draw_height,
            brand_text=brand_text, brand_font_size=brand_font_size,
            brand_y_offset=brand_y_offset, brand_x_offset=brand_x_offset,
            model_text=model_text, model_font_size=model_font_size,
            model_y_offset=model_y_offset, model_x_offset=model_x_offset,
            text_color=text_color,
        )

        content_string = "\n".join(content_parts)
        content_bytes = content_string.encode('latin-1')

        # Create appearance stream
        ap_stream = StreamObject()
        ap_stream[NameObject("/Type")] = NameObject("/XObject")
        ap_stream[NameObject("/Subtype")] = NameObject("/Form")
        ap_stream[NameObject("/FormType")] = NumberObject(1)
        ap_stream[NameObject("/BBox")] = ArrayObject([
            FloatObject(x1), FloatObject(y1), FloatObject(x2), FloatObject(y2),
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

    def _build_content_stream(
        self,
        cx: float, cy: float, radius: float,
        circle_color: tuple, circle_border_color: tuple, circle_border_width: float,
        id_box_x1: float, id_box_y1: float,
        id_box_width: float, id_box_height: float, id_box_border_width: float,
        id_label: str, id_text_color: tuple,
        img_x: float, img_y: float,
        img_draw_width: float, img_draw_height: float,
        brand_text: str, brand_font_size: float,
        brand_y_offset: float, brand_x_offset: float,
        model_text: str, model_font_size: float,
        model_y_offset: float, model_x_offset: float,
        text_color: tuple,
    ) -> list[str]:
        """Build the PDF content stream drawing commands."""
        parts = []
        k = self.BEZIER_K
        r, g, b = circle_color

        # 1. Draw circle (fill + stroke)
        parts.append(f"{circle_border_color[0]:.4f} {circle_border_color[1]:.4f} {circle_border_color[2]:.4f} RG")
        parts.append(f"{circle_border_width:.4f} w")
        parts.append(f"{r:.4f} {g:.4f} {b:.4f} rg")

        # Circle path using Bezier curves
        x0, y0 = cx + radius, cy
        parts.append(f"{x0:.3f} {y0:.3f} m")

        # Right to Top
        parts.append(f"{cx + radius:.3f} {cy + radius * k:.3f} {cx + radius * k:.3f} {cy + radius:.3f} {cx:.3f} {cy + radius:.3f} c")
        # Top to Left
        parts.append(f"{cx - radius * k:.3f} {cy + radius:.3f} {cx - radius:.3f} {cy + radius * k:.3f} {cx - radius:.3f} {cy:.3f} c")
        # Left to Bottom
        parts.append(f"{cx - radius:.3f} {cy - radius * k:.3f} {cx - radius * k:.3f} {cy - radius:.3f} {cx:.3f} {cy - radius:.3f} c")
        # Bottom to Right
        parts.append(f"{cx + radius * k:.3f} {cy - radius:.3f} {cx + radius:.3f} {cy - radius * k:.3f} {cx + radius:.3f} {cy:.3f} c")

        parts.append("h")
        parts.append("B")  # Fill and stroke

        # 2. Draw ID box on top
        parts.append("q")
        parts.append("1 1 1 rg")  # White fill
        parts.append("0 0 0 RG")  # Black stroke
        parts.append(f"{id_box_border_width:.1f} w")
        parts.append(f"{id_box_x1:.3f} {id_box_y1:.3f} {id_box_width:.3f} {id_box_height:.3f} re")
        parts.append("B")
        parts.append("Q")

        # ID box text
        parts.append("BT")
        parts.append(f"{id_text_color[0]:.4f} {id_text_color[1]:.4f} {id_text_color[2]:.4f} rg")
        parts.append("/Helv 2.5 Tf")
        id_text_width = len(id_label) * 1.2
        id_text_x = cx - id_text_width / 2
        id_text_y = id_box_y1 + 1.0
        parts.append(f"{id_text_x:.3f} {id_text_y:.3f} Td")
        parts.append(f"({id_label}) Tj")
        parts.append("ET")

        # 3. Draw gear image
        parts.append("q")
        parts.append(f"{img_draw_width:.3f} 0 0 {img_draw_height:.3f} {img_x:.3f} {img_y:.3f} cm")
        parts.append("/Img Do")
        parts.append("Q")

        # 4. Draw brand text (if provided)
        if brand_text:
            cisco_char_width = 0.55
            brand_chars = len(brand_text)
            brand_text_width = brand_chars * cisco_char_width * brand_font_size
            text_x_brand = cx - brand_text_width / 2 + brand_x_offset
            text_y_brand = cy + radius + brand_y_offset

            parts.append("BT")
            parts.append(f"{text_color[0]:.4f} {text_color[1]:.4f} {text_color[2]:.4f} rg")
            parts.append(f"/Helv {brand_font_size:.2f} Tf")
            parts.append(f"{text_x_brand:.3f} {text_y_brand:.3f} Td")
            parts.append(f"({brand_text}) Tj")
            parts.append("ET")

        # 5. Draw model text
        if model_text:
            model_char_width = 0.52
            model_chars = len(model_text)
            model_text_width = model_chars * model_char_width * model_font_size
            text_x_model = cx - model_text_width / 2 + model_x_offset
            text_y_model = cy - radius + model_y_offset

            parts.append("BT")
            parts.append(f"{text_color[0]:.4f} {text_color[1]:.4f} {text_color[2]:.4f} rg")
            parts.append(f"/Helv {model_font_size:.2f} Tf")
            parts.append(f"{text_x_model:.3f} {text_y_model:.3f} Td")
            parts.append(f"({model_text}) Tj")
            parts.append("ET")

        return parts
```

**IMPORTS**: Add to `backend/app/services/__init__.py`:
```python
from app.services.icon_renderer import IconRenderer
```

**GOTCHA**: The `_data` attribute on StreamObject is internal to PyPDF2. This matches the pattern in test_mr36h_icon.py.

**VALIDATE**:
```bash
cd backend && python -c "
from pathlib import Path
from app.services.icon_renderer import IconRenderer
renderer = IconRenderer(Path('../samples/icons/gearIcons'))
print(f'Can render MR36H: {renderer.can_render(\"AP - Cisco MR36H\")}')"
```

Expected: `Can render MR36H: True`

---

### Task 3: UPDATE `backend/app/services/annotation_replacer.py`

**IMPLEMENT**: Integrate IconRenderer into annotation replacement.

1. Add `icon_renderer` parameter to `__init__`:
```python
def __init__(
    self,
    mapping_parser: MappingParser,
    btx_loader: BTXReferenceLoader,
    appearance_extractor: "AppearanceExtractor | None" = None,
    icon_renderer: "IconRenderer | None" = None,  # NEW
):
    ...
    self.icon_renderer = icon_renderer
```

2. Add new method `_render_rich_icon()`:
```python
def _render_rich_icon(
    self,
    writer: PdfWriter,
    deployment_subject: str,
    rect: list[float],
    id_label: str = "j100",
) -> IndirectObject | None:
    """
    Render a rich deployment icon with full visual appearance.

    Args:
        writer: PdfWriter to add objects to
        deployment_subject: Deployment subject name
        rect: Annotation rect [x1, y1, x2, y2]
        id_label: ID label for the icon

    Returns:
        IndirectObject reference to appearance stream, or None if can't render
    """
    if not self.icon_renderer:
        return None

    if not self.icon_renderer.can_render(deployment_subject):
        return None

    return self.icon_renderer.render_icon(writer, deployment_subject, rect, id_label)
```

3. Update `replace_annotations()` to use rich rendering when available:
   - When creating new annotations, first try `_render_rich_icon()`
   - If that returns None, fall back to simple colored shapes (existing behavior)

**PATTERN**: See existing `_create_annotation_on_page()` method for reference.

**GOTCHA**: The current implementation uses PyMuPDF for annotation creation. To use PyPDF2-based appearance streams, we need to either:
- Option A: Create a parallel code path using PyPDF2 when rich rendering is needed
- Option B: Extract the appearance stream bytes and apply to PyMuPDF annotation

Recommend Option B for minimal disruption. PyMuPDF annotations can have custom appearance streams set.

**VALIDATE**:
```bash
cd backend && python -m pytest tests/test_annotation_replacer.py -v
```

---

### Task 4: CREATE `backend/scripts/test_icon_render.py`

**IMPLEMENT**: Test script to render any icon by name for visual verification.

```python
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

from app.services.icon_config import get_icon_config, ICON_CATEGORIES, get_model_text
from app.services.icon_renderer import IconRenderer


PROJECT_ROOT = Path(__file__).parent.parent.parent
SAMPLE_PDF = PROJECT_ROOT / "samples" / "maps" / "BidMap.pdf"
GEAR_ICONS = PROJECT_ROOT / "samples" / "icons" / "gearIcons"
OUTPUT_DIR = PROJECT_ROOT / "samples" / "maps"


def list_available_icons():
    """List all icons that can be rendered."""
    print("Available deployment icons:")
    print("-" * 50)

    renderer = IconRenderer(GEAR_ICONS)

    for category in sorted(set(ICON_CATEGORIES.values())):
        icons_in_category = [
            subj for subj, cat in ICON_CATEGORIES.items()
            if cat == category
        ]
        print(f"\n{category}:")
        for icon in sorted(icons_in_category):
            can_render = "✓" if renderer.can_render(icon) else "✗"
            print(f"  {can_render} {icon}")


def render_test_icon(subject: str):
    """Render a single icon for visual testing."""
    print(f"\nRendering: {subject}")
    print("=" * 60)

    renderer = IconRenderer(GEAR_ICONS)

    if not renderer.can_render(subject):
        print(f"ERROR: Cannot render '{subject}'")
        print("  - Check if config exists in icon_config.py")
        print("  - Check if image file exists")
        return

    config = get_icon_config(subject)
    print(f"Category: {config.get('category')}")
    print(f"Circle color: {config.get('circle_color')}")
    print(f"Model text: {get_model_text(subject)}")
    print(f"Image path: {config.get('image_path')}")

    # Create test PDF
    reader = PdfReader(str(SAMPLE_PDF))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    page = writer.pages[0]

    # Create test annotation rect (fixed position for testing)
    rect = [100.0, 700.0, 125.0, 730.0]  # 25x30 PDF units

    # Render icon
    appearance_ref = renderer.render_icon(writer, subject, rect, id_label="test")

    if not appearance_ref:
        print("ERROR: Rendering failed")
        return

    # Create annotation with the appearance
    annot = DictionaryObject()
    annot[NameObject("/Type")] = NameObject("/Annot")
    annot[NameObject("/Subtype")] = NameObject("/Circle")
    annot[NameObject("/Rect")] = ArrayObject([
        FloatObject(rect[0]), FloatObject(rect[1]),
        FloatObject(rect[2]), FloatObject(rect[3]),
    ])
    annot[NameObject("/Subj")] = TextStringObject(subject)
    annot[NameObject("/F")] = NumberObject(4)

    # Set colors
    circle_color = config.get("circle_color", (0.5, 0.5, 0.5))
    annot[NameObject("/IC")] = ArrayObject([
        FloatObject(circle_color[0]),
        FloatObject(circle_color[1]),
        FloatObject(circle_color[2]),
    ])

    # Appearance
    ap = DictionaryObject()
    ap[NameObject("/N")] = appearance_ref
    annot[NameObject("/AP")] = ap

    # Add to page
    annots_ref = page.get("/Annots")
    if annots_ref:
        annots = annots_ref.get_object() if hasattr(annots_ref, 'get_object') else annots_ref
        annots.append(annot)

    # Save
    safe_name = subject.replace(" ", "_").replace("-", "_").replace("/", "_")
    output_path = OUTPUT_DIR / f"test_icon_{safe_name}.pdf"

    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"\nSaved to: {output_path}")
    print("\nOpen the PDF and verify the icon appearance.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_icon_render.py <subject>")
        print("       python test_icon_render.py --list")
        sys.exit(1)

    if sys.argv[1] == "--list":
        list_available_icons()
    else:
        subject = " ".join(sys.argv[1:])
        render_test_icon(subject)


if __name__ == "__main__":
    main()
```

**VALIDATE**:
```bash
cd backend && python scripts/test_icon_render.py --list
cd backend && python scripts/test_icon_render.py "AP - Cisco MR36H"
```

---

### Task 5: CREATE `backend/tests/test_icon_renderer.py`

**IMPLEMENT**: Unit tests for the icon renderer service.

```python
"""Tests for icon renderer service."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PyPDF2 import PdfWriter

from app.services.icon_config import (
    get_icon_config,
    get_model_text,
    ICON_CATEGORIES,
    CATEGORY_DEFAULTS,
)
from app.services.icon_renderer import IconRenderer


class TestIconConfig:
    """Tests for icon configuration."""

    def test_get_icon_config_known_icon(self):
        """Test config retrieval for known icon."""
        config = get_icon_config("AP - Cisco MR36H")
        assert config is not None
        assert "circle_color" in config
        assert config["category"] == "APs"

    def test_get_icon_config_unknown_icon(self):
        """Test config retrieval for unknown icon."""
        config = get_icon_config("Unknown - Nonexistent Icon")
        assert config == {}

    def test_get_model_text_cisco(self):
        """Test model text extraction for Cisco device."""
        assert get_model_text("AP - Cisco MR36H") == "MR36H"
        assert get_model_text("AP - Cisco 9120") == "9120"

    def test_get_model_text_ubiquiti(self):
        """Test model text extraction for Ubiquiti device."""
        assert get_model_text("P2P - Ubiquiti NanoBeam") == "NanoBeam"

    def test_category_defaults_exist(self):
        """Test that all categories have defaults."""
        categories = set(ICON_CATEGORIES.values())
        for cat in categories:
            assert cat in CATEGORY_DEFAULTS, f"Missing defaults for {cat}"


class TestIconRenderer:
    """Tests for IconRenderer service."""

    @pytest.fixture
    def renderer(self, tmp_path):
        """Create renderer with temp directory."""
        # Create fake gear icons structure
        aps_dir = tmp_path / "APs"
        aps_dir.mkdir()

        # Create a minimal PNG file for testing
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(aps_dir / "AP - Cisco MR36H.png")

        return IconRenderer(tmp_path)

    def test_init(self, renderer):
        """Test renderer initialization."""
        assert renderer.gear_icons_dir is not None
        assert renderer._image_cache == {}

    def test_can_render_with_image(self, renderer):
        """Test can_render returns True when image exists."""
        # This depends on icon_config having the mapping
        # We may need to mock the config
        with patch('app.services.icon_renderer.get_icon_config') as mock_config:
            mock_config.return_value = {
                "image_path": "APs/AP - Cisco MR36H.png",
                "category": "APs",
            }
            assert renderer.can_render("AP - Cisco MR36H") is True

    def test_can_render_without_config(self, renderer):
        """Test can_render returns False when no config."""
        with patch('app.services.icon_renderer.get_icon_config') as mock_config:
            mock_config.return_value = {}
            assert renderer.can_render("Unknown Icon") is False

    def test_load_image_caching(self, renderer):
        """Test that images are cached after loading."""
        with patch('app.services.icon_renderer.get_icon_config') as mock_config:
            mock_config.return_value = {
                "image_path": "APs/AP - Cisco MR36H.png",
            }

            bg_color = (0.22, 0.34, 0.65)

            # First load
            data1, w1, h1 = renderer.load_image("APs/AP - Cisco MR36H.png", bg_color)

            # Second load should use cache
            data2, w2, h2 = renderer.load_image("APs/AP - Cisco MR36H.png", bg_color)

            assert data1 == data2
            assert w1 == w2
            assert h1 == h2

    def test_render_icon_returns_indirect_object(self, renderer):
        """Test that render_icon returns an IndirectObject."""
        with patch('app.services.icon_renderer.get_icon_config') as mock_config:
            mock_config.return_value = {
                "image_path": "APs/AP - Cisco MR36H.png",
                "category": "APs",
                "circle_color": (0.22, 0.34, 0.65),
                "circle_border_width": 0.5,
                "circle_border_color": (0.0, 0.0, 0.0),
                "id_box_height": 4.0,
                "id_box_width_ratio": 0.55,
                "id_box_border_width": 0.6,
                "img_scale_ratio": 0.70,
                "brand_text": "CISCO",
                "brand_font_size": 1.9,
                "brand_y_offset": -4.0,
                "brand_x_offset": -0.2,
                "model_font_size": 1.6,
                "model_y_offset": 2.5,
                "model_x_offset": -0.7,
                "text_color": (1.0, 1.0, 1.0),
            }

            writer = PdfWriter()
            rect = [100.0, 200.0, 125.0, 230.0]

            result = renderer.render_icon(writer, "AP - Cisco MR36H", rect)

            assert result is not None


class TestIconRendererIntegration:
    """Integration tests with real files."""

    def test_with_real_gear_icons(self):
        """Test with actual gear icons directory if available."""
        gear_icons = Path("../samples/icons/gearIcons")
        if not gear_icons.exists():
            gear_icons = Path("samples/icons/gearIcons")

        if not gear_icons.exists():
            pytest.skip("Gear icons directory not found")

        renderer = IconRenderer(gear_icons)

        # Test a known icon
        assert renderer.can_render("AP - Cisco MR36H") is True
```

**IMPORTS**: Requires PIL/Pillow for creating test images.

**VALIDATE**:
```bash
cd backend && python -m pytest tests/test_icon_renderer.py -v
```

---

### Task 6: ADD remaining icon configs to `icon_config.py`

**IMPLEMENT**: Add configurations for all deployment subjects in mapping.md.

Extract unique deployment subjects from mapping.md and add configs for each category.

#### COMPLETE ICON INVENTORY

**ICONS WITH GEAR IMAGES (rich rendering with product photos):**

| Category | Deployment Subject | Gear Image File | Brand Text |
|----------|-------------------|-----------------|------------|
| **APs** | AP - Cisco MR36H | `APs/AP - Cisco MR36H.png` | CISCO |
| **APs** | AP - Cisco 9120 | `APs/AP - Cisco 9120.png` | CISCO |
| **APs** | AP - Cisco 9166I | `APs/AP - Cisco 9166.png` | CISCO |
| **APs** | AP - Cisco 9166D | `APs/AP - Cisco 9166.png` | CISCO |
| **APs** | AP - Cisco MR78 | `APs/AP - Cisco MR78.png` | CISCO |
| **APs** | AP - Cisco Marlin 4 | `APs/AP - Cisco Marlin 4.png` | CISCO |
| **APs** | AP - Cisco DB10 | `APs/AP - DB10.png` | CISCO |
| **Switches** | SW - Cisco Micro 4P | `Switches/Cisco Micro 4-P.png` | CISCO |
| **Switches** | SW - Cisco 9200 12P | `Switches/Cisco 9200 12-P.png` | CISCO |
| **Switches** | SW - IDF Cisco 9300 24X | `Switches/Cisco 9300 24-P.png` | CISCO |
| **Switches** | DIST - Mini NOC | `Switches/Mini NOC.png` | (none) |
| **Switches** | DIST - Micro NOC | `Switches/Mini NOC.png` | (none) |
| **Switches** | DIST - Standard NOC | `Switches/NOC.png` | (none) |
| **Switches** | DIST - MikroTik Hex | `Switches/MikroTik Hex.png` | MIKROTIK |
| **Switches** | DIST - Starlink | `Switches/Starlink.png` | STARLINK |
| **Switches** | DIST - Pelican NOC | `Switches/NOC.png` | (none) |
| **P2Ps** | P2P - Ubiquiti NanoBeam | `P2Ps/P2P - Ubiquiti NanoBeam.png` | UBIQUITI |
| **P2Ps** | P2P - Ubiquiti LiteAP | `P2Ps/P2P - Ubiquiti LiteAP AC.png` | UBIQUITI |
| **P2Ps** | P2P - Ubiquiti GigaBeam | `P2Ps/P2P - Ubiquiti GigaBeam.png` | UBIQUITI |
| **P2Ps** | P2P - Ubiquiti GigaBeam LR | `P2Ps/P2P - Ubiquiti GigaBeam LR.png` | UBIQUITI |
| **IoT** | VOIP - Yealink T29G | `Misc/Yealink T29G.png` | YEALINK |
| **IoT** | VOIP - Yealink CP965 | `Misc/Yealink P965.png` | YEALINK |
| **IoT** | CCTV - AXIS P5655-E | `Misc/AXIS P5655-E.png` | AXIS |
| **IoT** | CCTV - AXIS S9302 | `Misc/AXIS S9302 Workstation.png` | AXIS |
| **IoT** | EAS - Command Unit | `Misc/Emergency Announce Command Unit.png` | (none) |
| **IoT** | EAS - Laptop | `Misc/EAS Laptop.png` | (none) |
| **IoT** | EAS - Trigger Box | `Misc/Emergency Announce Trigger Box.png` | (none) |
| **IoT** | IPTV - BrightSign XT1144 | `Misc/Brightsign XT1144.png` | BRIGHTSIGN |
| **Hardlines** | HL - Artist | `Hardlines/CAT6 Cable.png` | (none) |
| **Hardlines** | HL - Production | `Hardlines/CAT6 Cable.png` | (none) |
| **Hardlines** | HL - PoS | `Hardlines/CAT6 Cable.png` | (none) |
| **Hardlines** | HL - Access Control | `Hardlines/CAT6 Cable.png` | (none) |
| **Hardlines** | HL - Sponsor | `Hardlines/CAT6 Cable.png` | (none) |
| **Hardlines** | HL - General Internet | `Hardlines/CAT6 Cable.png` | (none) |
| **Hardlines** | HL - Audio | `Hardlines/CAT6 Cable.png` | (none) |
| **Hardlines** | HL - Emergency Announce System | `Hardlines/CAT6 Cable.png` | (none) |
| **Hardlines** | HL - WAN | `Hardlines/CAT6 Cable.png` | (none) |

**ICONS WITHOUT GEAR IMAGES (simple colored shapes only):**

| Category | Deployment Subject | Render As | Color Suggestion |
|----------|-------------------|-----------|------------------|
| **Cables** | FIBER | Line/Rectangle | Yellow/Orange |
| **Misc** | INFRA - Fiber Patch Panel | Rectangle | Gray |

#### CATEGORY DEFAULTS STRUCTURE

```python
CATEGORY_DEFAULTS = {
    "APs": {
        "circle_color": (0.22, 0.34, 0.65),  # Navy blue
        "brand_text": "CISCO",  # Default, can override per-icon
        # ... other params from MR36H
    },
    "Switches": {
        "circle_color": (0.15, 0.45, 0.25),  # Green
        "brand_text": "",  # Many switches have no brand text
    },
    "P2Ps": {
        "circle_color": (0.4, 0.2, 0.6),  # Purple
        "brand_text": "UBIQUITI",
    },
    "IoT": {
        "circle_color": (0.6, 0.3, 0.1),  # Brown/orange
        "brand_text": "",  # Varies by device
    },
    "Hardlines": {
        "circle_color": (0.3, 0.3, 0.3),  # Gray
        "brand_text": "",  # No brand text for hardlines
        # All hardlines use the same image: Hardlines/CAT6 Cable.png
    },
    "Cables": {
        "circle_color": (0.8, 0.6, 0.0),  # Yellow/orange
        "no_image": True,
    },
    "Misc": {
        "circle_color": (0.5, 0.5, 0.5),  # Gray
        "no_image": True,
    },
}
```

**GOTCHA**:
1. Deployment subjects with `None` in ICON_IMAGE_PATHS should have `"no_image": True` in their category defaults (only FIBER and INFRA - Fiber Patch Panel)
2. Brand text varies by manufacturer - CISCO, UBIQUITI, AXIS, YEALINK, BRIGHTSIGN, MIKROTIK, STARLINK
3. Some icons (NOC, Mini NOC, EAS, Hardlines) have no brand text - just the model or category label
4. **All Hardlines use the same image and color:** `Hardlines/CAT6 Cable.png` - differentiated only by model text (e.g., "Artist", "Production", "PoS") and ID label

**VALIDATE**:
```bash
cd backend && python -c "
from app.services.icon_config import ICON_CATEGORIES, ICON_IMAGE_PATHS
with_images = sum(1 for v in ICON_IMAGE_PATHS.values() if v is not None)
without_images = sum(1 for v in ICON_IMAGE_PATHS.values() if v is None)
print(f'Total icons: {len(ICON_CATEGORIES)}')
print(f'With gear images: {with_images}')
print(f'Without images (colored shapes): {without_images}')"
```

Expected output:
```
Total icons: 39
With gear images: 37
Without images (colored shapes): 2
```

---

## TESTING STRATEGY

### Unit Tests

- `test_icon_config.py`: Test config loading, merging, model text extraction
- `test_icon_renderer.py`: Test renderer initialization, can_render(), image loading, appearance generation

### Integration Tests

- `test_annotation_replacer.py`: Update to test rich icon rendering path
- Manual test script `test_icon_render.py` for visual verification

### Edge Cases

1. Icon with no gear image available
2. Icon with no config defined
3. Very small annotation rect (< 10pt)
4. Very large annotation rect (> 100pt)
5. Unicode characters in model text

---

## VALIDATION COMMANDS

### Level 1: Syntax & Style

```bash
cd backend && python -m py_compile app/services/icon_config.py
cd backend && python -m py_compile app/services/icon_renderer.py
```

### Level 2: Unit Tests

```bash
cd backend && python -m pytest tests/test_icon_renderer.py -v
cd backend && python -m pytest tests/test_icon_config.py -v 2>/dev/null || echo "Test file may not exist yet"
```

### Level 3: Integration Tests

```bash
cd backend && python -m pytest tests/ -v
```

### Level 4: Manual Validation

```bash
# Test single icon rendering
cd backend && python scripts/test_icon_render.py "AP - Cisco MR36H"

# List all available icons
cd backend && python scripts/test_icon_render.py --list

# Open output PDF and visually verify icon appearance
open samples/maps/test_icon_AP_Cisco_MR36H.pdf
```

### Level 5: Full Conversion Test

```bash
# After integration, test full BidMap.pdf conversion
cd backend && python scripts/test_conversion.py
```

---

## ACCEPTANCE CRITERIA

- [ ] `icon_config.py` contains category defaults extracted from test_mr36h_icon.py
- [ ] `icon_config.py` maps all deployment subjects to categories and images
- [ ] `get_icon_config()` correctly merges category defaults with per-icon overrides
- [ ] `IconRenderer.can_render()` returns True for icons with available images
- [ ] `IconRenderer.render_icon()` produces valid PDF appearance streams
- [ ] MR36H icon rendered via new system visually matches previous test_mr36h_icon.py output
- [ ] All 86+ existing tests still pass
- [ ] New tests for icon_config and icon_renderer pass
- [ ] Test script can render icons for visual verification

---

## COMPLETION CHECKLIST

- [ ] Task 1: icon_config.py created with category defaults
- [ ] Task 2: icon_renderer.py created with rendering engine
- [ ] Task 3: annotation_replacer.py updated for integration (optional for MVP)
- [ ] Task 4: test_icon_render.py script created
- [ ] Task 5: test_icon_renderer.py unit tests created
- [ ] Task 6: All deployment subjects have configs
- [ ] All validation commands pass
- [ ] Manual visual verification successful
- [ ] All acceptance criteria met

---

## NOTES

### Design Decisions

1. **Python dict vs YAML/JSON**: Using Python dict for configuration allows:
   - Type hints and IDE support
   - Computed values (e.g., color tuples)
   - No parsing dependencies
   - Easy to modify programmatically

2. **Hierarchical config (category defaults + overrides)**: Minimizes duplication while allowing per-icon tuning. Most icons in a category share 90% of parameters.

3. **Separate rendering service vs inline in annotation_replacer**: Keeps concerns separated:
   - `icon_renderer.py` handles visual appearance only
   - `annotation_replacer.py` handles PDF manipulation and mapping

### Known Limitations

1. **Image dependency**: Icons without gear images will need simpler rendering (colored shapes)
2. **Font limitations**: Using Helvetica-Bold (standard PDF font) - no custom fonts
3. **Text sizing**: Character width calculations are approximations

### Future Enhancements

1. Add "coordinates" label at bottom (xx' xx° format)
2. Support for non-Cisco brands (different brand text)
3. Batch visual verification tool
4. Automated visual regression testing
