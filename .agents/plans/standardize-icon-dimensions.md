# Plan: Standardize All Icon Dimensions to Match 9200 Switch

## Context
Currently, each icon category (APs, Switches, P2Ps, Hardlines, etc.) has different rendering parameters for circle size, ID box size, and text positioning. The user wants **every icon to look identical in structure** — same circle dimensions, same ID box dimensions — matching the current "SW - Cisco 9200 12P" switch icon. Text (brand + model) must be centered and fit within the circle.

## Target Dimensions (from Switches category / 9200 icon)
For a standard ~14.58 x 14.59 annotation rect:
- **ID box**: height=3.5, width_ratio=0.55, border_width=0.45
- **Circle**: radius ≈ 6.25 (derived from rect minus id_box)
- **ID font size**: 3.2
- **Brand/model font sizes**: 1.8 / 2.2

## Changes

### 1. `backend/app/services/icon_config.py` — Standardize CATEGORY_DEFAULTS
- Set **all categories** to use the same structural dimensions as Switches:
  - `id_box_height`: 3.5
  - `id_box_width_ratio`: 0.55
  - `id_box_border_width`: 0.45
  - `id_font_size`: 3.2
  - `circle_border_width`: 0.75
  - `brand_font_size`: 1.8
  - `model_font_size`: 2.2
  - `img_scale_ratio`: 0.70
- Keep category-specific values: `circle_color`, `brand_text`, `text_color`, `no_image`, `model_uppercase`
- Remove all manual text offset overrides from `ICON_OVERRIDES` (`brand_x_offset`, `brand_y_offset`, `model_x_offset`, `model_y_offset`) — text centering will be automatic
- Keep image-specific overrides (`img_scale_ratio`, `img_x_offset`, `img_y_offset`) only where needed for image positioning

### 2. `backend/app/services/icon_renderer.py` — Auto-center text and auto-fit
- **Remove reliance on manual x/y offsets for text positioning**
- **Brand text**: Center horizontally in circle, position at a fixed offset below circle top (relative to radius, not absolute offsets)
- **Model text**: Center horizontally in circle, position at a fixed offset above circle bottom
- **Auto-shrink text**: If text width exceeds available circle width at that y-position (chord width), reduce font size to fit
- **ID box text**: Already centered — keep as-is
- All text centering uses circle center (`cx`) and `radius` for chord-width calculations

### 3. `backend/app/services/icon_renderer.py` — Simplify layout constants
- Remove `brand_x_offset`, `brand_y_offset`, `model_x_offset`, `model_y_offset` from `_create_appearance_stream` parameters
- Brand text y-position = `cy + radius * 0.48` (just inside top of circle)
- Model text y-position = `cy - radius * 0.72` (just inside bottom of circle)
- For multi-line model text, stack lines upward from the bottom position

## Files to Modify
1. **`backend/app/services/icon_config.py`** — Standardize all CATEGORY_DEFAULTS, clean up ICON_OVERRIDES
2. **`backend/app/services/icon_renderer.py`** — Auto-centering, auto-fit text logic

## Verification
1. Run `uv run pytest` — expect same 147 passed, 5 known failures
2. Run `uv run python scripts/test_conversion.py` — generate new sample PDF
3. Open output PDF in Bluebeam and verify:
   - All icons have identical circle + ID box dimensions
   - Brand text centered inside circle (top area)
   - Model text centered inside circle (bottom area)
   - No text overflows outside circle boundary
