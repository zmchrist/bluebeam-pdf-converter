# Fix: Annotations Invisible After BBox+Matrix Change

## Context

Our BBox+Matrix changes from this session made all converted annotations invisible. The root cause: content stream draws at zero-origin coords but absolute BBox clips them out. We need to generate two test PDFs for Bluebeam comparison.

## Root Cause

BBox defines the **clipping rectangle** in form space. Our content stream draws at `(1.217, 0.0)` but BBox clips to `[702, 871, 717, 886]` — content is entirely outside the clip area.

The `/Matrix` transforms form-to-outer space, it does NOT affect BBox clipping.

## Plan: Generate Two Test PDFs

### PDF A: Absolute BBox + absolute cm + Matrix (matches real Bluebeam)
- `icon_renderer.py`: Change `x_off = x1 + (rect_width - content_w) / 2` (absolute cm offsets)
- `icon_renderer.py`: Keep absolute BBox `[x1,y1,x2,y2]` and Matrix `[1,0,0,1,-x1,-y1]`
- `annotation_replacer.py`: Same for simple appearance — content draws at absolute coords
- `/IC`, `/C`, `/BS` always present

### PDF B: Zero-origin BBox, no Matrix (revert to pre-session working state)
- `icon_renderer.py`: Revert BBox to `[0,0,w,h]`, remove Matrix, keep zero-origin cm
- `annotation_replacer.py`: Same revert for simple appearance
- `/IC`, `/C`, `/BS` always present (keep this change)

### Files
- `backend/app/services/icon_renderer.py` — `_create_appearance_stream()`
- `backend/app/services/annotation_replacer.py` — `_create_simple_appearance()`

### Verification
Generate both PDFs, user opens in Bluebeam to compare:
1. Are annotations visible?
2. Can they be moved without turning white?
3. Are they selectable/editable?
