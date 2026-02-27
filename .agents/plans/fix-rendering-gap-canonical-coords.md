# Fix Rendering Gap: Canonical Coordinate Space for Icon Rendering

## Context

After implementing the first round of rendering gap fixes (image aspect ratio, Helvetica-Bold metrics, PDF preview toggle), icon tuner previews still don't match actual converted PDF output. The user reports that circle shape, border width, text size, and overall layout differ between the tuner and the converted PDF — even though colors, text content, shapes, and images are correct.

**Root cause:** The icon tuner always renders in a fixed `[0, 0, 25, 30]` coordinate space (25 wide, 30 tall — a 5:6 aspect ratio). But real Bluebeam stamp annotations are **square**: ~22.9x22.9 in BidMap.pdf, ~14.6x14.6 in BidMap2.pdf. The icon renderer currently draws directly in the annotation's coordinate space, so all config parameters (font sizes, border widths, offsets, id_box_height) produce different visual proportions depending on the annotation rect size. A 0.5pt border looks right in 25x30 but proportionally thicker/thinner in 22.9x22.9.

## Solution: Canonical Coordinate Space with PDF `cm` Transform

Always render icon content in the canonical `[0, 0, 25, 30]` coordinate space (matching the tuner), then use a PDF `cm` (concatenate matrix) operator to uniformly scale and center the content within the actual annotation rect. This guarantees the tuner preview matches the PDF output exactly.

**How it works:**
1. Compute a uniform scale factor: `scale = min(rect_width / 25, rect_height / 30)`
2. Center the scaled content: offset = `(rect_size - canonical_size * scale) / 2`
3. Wrap all drawing commands in `q` / `scale 0 0 scale x_off y_off cm` / ... / `Q`
4. All layout calculations use the canonical 25x30 space (cx=12.5, height=30, etc.)
5. BBox stays as `[x1, y1, x2, y2]` (no viewer scaling needed — the cm handles it)

**Example:** For a 22.9x22.9 annotation rect at `[100, 200, 122.9, 222.9]`:
- `scale = min(22.9/25, 22.9/30) = 0.763`
- Effective content: 19.1 wide x 22.9 tall (centered with 1.9pt margin on each side)
- All fonts, borders, offsets scale by 0.763 — proportions identical to tuner

## Implementation

### File: `backend/app/services/icon_renderer.py` — `_create_appearance_stream()`

Replace the layout section (lines 273-315) to use canonical space:

```python
x1, y1, x2, y2 = rect
rect_width = x2 - x1
rect_height = y2 - y1

# Canonical space (matches tuner's 25x30 coordinate space)
CANON_W, CANON_H = 25.0, 30.0
render_scale = min(rect_width / CANON_W, rect_height / CANON_H)
content_w = CANON_W * render_scale
content_h = CANON_H * render_scale
x_off = x1 + (rect_width - content_w) / 2
y_off = y1 + (rect_height - content_h) / 2

# Layout in canonical [0, 0, 25, 30] space (identical to tuner)
width = CANON_W
cx = CANON_W / 2  # 12.5
id_box_width = width * id_box_width_ratio
id_box_x1 = cx - id_box_width / 2
id_box_y1 = CANON_H - id_box_height  # e.g., 26

circle_top = id_box_y1 + 2
circle_bottom = 0
circle_area_height = circle_top - circle_bottom
radius = min(width, circle_area_height) / 2 - 0.3
cy = circle_top - radius

# Image, text positions — all in canonical space (same as before, just using CANON_W/H)
```

Then wrap the content stream:

```python
content_parts = ["q", f"{render_scale:.6f} 0 0 {render_scale:.6f} {x_off:.3f} {y_off:.3f} cm"]
content_parts.extend(self._build_content_stream(...))  # All coords in canonical space
content_parts.append("Q")
```

### No changes needed to:
- `_build_content_stream()` — receives canonical coordinates, no change
- `canvasDrawing.ts` — already uses 25x30 canonical space
- `tuner.py` render-pdf endpoint — already uses `[0, 0, 25, 30]`
- BBox in the appearance stream — stays as `[x1, y1, x2, y2]`

## Files to Modify

| File | Change |
|------|--------|
| `backend/app/services/icon_renderer.py` | Replace layout calculations in `_create_appearance_stream` to use canonical 25x30 space + cm transform |

## Verification

1. **Visual match**: Open tuner, toggle "Show PDF Preview" — canvas and PDF preview should now look identical in proportions
2. **Converted PDF**: Run `uv run python scripts/test_conversion.py`, open output PDF — icons should match tuner preview
3. **Standalone render**: Run `uv run python scripts/test_icon_render.py "AP - Cisco MR36H"` — verify icon renders correctly
4. **Tests**: Run `cd backend && uv run pytest tests/test_icon_renderer.py -v` — expect same baseline (1 known failure)
5. **Full suite**: Run `cd backend && uv run pytest` — expect 170 passed, 6 known failures, 11 skipped
