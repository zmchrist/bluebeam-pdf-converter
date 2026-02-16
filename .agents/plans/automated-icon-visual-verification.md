# Feature: Automated Icon Visual Verification & Auto-Tuning

The following plan should be complete, but its important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Create a standalone tuning system that automates the visual verification of rendered deployment icons by comparing them pixel-by-pixel against reference deployment PDFs. The system extracts individual icons from reference catalog pages, renders the corresponding generated icons, computes similarity scores, and auto-tunes `icon_config.py` parameters (colors, offsets, sizes) to maximize visual match.

## User Story

As a developer maintaining icon rendering
I want an automated comparison tool that scores my rendered icons against reference PDFs
So that I can tune icon parameters without manual PDF-open-and-eyeball verification

## Problem Statement

Currently, verifying that rendered deployment icons visually match the reference deployment PDFs requires manually rendering a test icon to PDF, opening it in a PDF viewer, and visually comparing it to the reference. This is slow, subjective, and error-prone. With 87+ icons across 5 reference PDFs, comprehensive verification is impractical.

## Solution Statement

Build a Python script package that:
1. Renders reference PDF pages to images and extracts individual icon crops
2. Renders generated icons to images using the same pipeline as production
3. Computes quantitative pixel-level similarity scores
4. Automatically adjusts icon_config.py parameters to improve match scores
5. Outputs proposed config changes and side-by-side comparison images for review

## Feature Metadata

**Feature Type**: New Capability (developer tooling)
**Estimated Complexity**: High
**Primary Systems Affected**: `backend/scripts/`, `backend/app/services/icon_config.py`, `backend/app/services/icon_renderer.py`
**Dependencies**: Pillow (already installed), PyMuPDF (already installed), PyPDF2 (already installed)

---

## CONTEXT REFERENCES

### Relevant Codebase Files IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

- `backend/app/services/icon_renderer.py` (full file) - Why: The rendering engine you'll be converting to image output. Contains `render_icon()`, `_create_appearance_stream()`, `_build_content_stream()`, `load_image()`, `create_image_xobject()`. Uses PyPDF2 PdfWriter to create appearance streams.
- `backend/app/services/icon_config.py` (full file) - Why: All tunable parameters. Contains `ICON_CATEGORIES`, `CATEGORY_DEFAULTS`, `ICON_OVERRIDES`, `ICON_IMAGE_PATHS`, `get_icon_config()`, `get_model_text()`. This is what the auto-tuner will be optimizing.
- `backend/scripts/test_icon_render.py` (full file) - Why: Existing pattern for rendering a single icon to a test PDF. Your `render_icon_to_image()` function will be a direct evolution of this script's approach - same rect, same annotation creation, but output to PIL Image instead of file.
- `backend/scripts/validate_fix.py` (lines 31-45) - Why: Shows the pattern for using `annot.get_pixmap()` with PyMuPDF to render annotations to images.
- `backend/app/services/appearance_extractor.py` (full file) - Why: Shows PyMuPDF usage patterns (`fitz.open()`, page iteration, annotation inspection).

### Reference PDF Visual Analysis (from actual rendering)

**accessPoints.pdf** (612x792 portrait, 7 icons):
- Layout: 3x3 grid, last row has 1 icon
- Order (L-R, T-B): j100/MR36H, k100/MR78, l100/9166I, m100/9166D, n100/9120, o100/MARLIN 4, p100/DB10
- Style: Navy blue circles, "CISCO" brand text (white), white ID box at top, "xx' xx°" coordinate label below each icon
- Each icon includes: ID box → circle with gear image → brand text → model text → coordinate label

**switches.pdf** (792x612 LANDSCAPE, ~21 icons):
- Layout: 3 rows densely packed, landscape orientation
- Row 1 (8 icons): a100/MICRO 4P, b100/108F 8P, c100/9200 12P, d300/9300X 24X, d500/9300 12X36M, d700/9300X 24Y, d900/9500 48Y4C, a100 (PoE?)
- Row 2 (5 icons): e100/IDF 9300 24X, e300/IDF 9300X 24X, e500/IDF 9300 12X36M, e700/IDF 9300X 24Y, e900/IDF 9500 48Y4C, f100 (NOC?)
- Row 3 (4+ icons): f100/STARLINK, f100/MINI NOC, f100/NOC, f100/MIKROTIK
- Style: Green circles (0.267, 0.714, 0.290), various brand texts

**hardlines.pdf** (612x792 portrait, ~28 icons):
- Layout: Dense grid, ~6 columns x 5 rows
- All use red circles and CAT6 Cable image, differentiated by model text label
- Order includes: aa100/ARTIST, bb100/PRODUCTION, cc100/AUDIO, dd100/CCTV, ee100/CLAIR, ff100/EAS, gg100/GENERAL INTERNET, hh100/IPTV, etc.
- Additional fiber types: LC SM, SC SM, ST SM (different images)

**p2p.pdf** (612x792 portrait, 7 icons):
- Layout: 3x3 grid, last row has 1 icon
- Order: s100/NANOBEAM, t100/LITEAP, u100/WAVE NANO, v100/WAVE PICO, w100/WAVE AP MICRO, x100/GIGABEAM, y100/GIGABEAM LR
- Style: Orange/amber circles (NOT purple as currently configured!), "UBIQUITI" brand text

**cameras.pdf** (612x792 portrait, 4 icons):
- Layout: 3+1 grid
- Order: 100a/MV93X, 100b/P5655-E, 100c/M5526-E, (row 2) S9302
- Style: Navy BLUE circles with dark border (NOT brown IoT as currently configured!), various brand texts (CISCO, AXIS)
- Note: S9302 has no ID label above it in the reference

### CRITICAL COLOR DISCOVERIES FROM REFERENCE PDFs

The visual inspection revealed color mismatches between current config and reference PDFs:

| Category | Current Config Color | Reference PDF Color | Action Needed |
|----------|---------------------|---------------------|---------------|
| APs | (0.22, 0.34, 0.65) navy blue | Navy blue | Correct ✓ |
| Switches | (0.267, 0.714, 0.290) green | Green | Correct ✓ |
| P2Ps | (0.4, 0.2, 0.6) purple | Orange/amber | WRONG - needs fix |
| Cameras (IoT) | (0.6, 0.3, 0.1) brown | Navy blue (same as APs) | WRONG - needs fix |
| Hardlines | (0.8, 0.2, 0.2) red | Red | Correct ✓ |

These will be auto-detected and corrected by the color extraction phase.

### New Files to Create

- `backend/scripts/icon_tuner/__init__.py` - Package init
- `backend/scripts/icon_tuner/reference_extractor.py` - Extract icons from reference PDFs
- `backend/scripts/icon_tuner/icon_comparator.py` - Render generated icons, compute similarity
- `backend/scripts/icon_tuner/auto_tuner.py` - Parameter optimization engine
- `backend/scripts/icon_tuner/region_config.py` - Reference PDF → subject mapping config
- `backend/scripts/run_icon_tuner.py` - CLI entry point

### Patterns to Follow

**Script path setup** (from test_icon_render.py):
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**PyMuPDF page rendering** (from validate_fix.py pattern):
```python
import fitz
doc = fitz.open(str(pdf_path))
page = doc[0]
mat = fitz.Matrix(zoom, zoom)  # zoom = dpi / 72.0
pix = page.get_pixmap(matrix=mat)
img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
```

**Icon rendering pipeline** (from test_icon_render.py):
```python
writer = PdfWriter()
writer.add_blank_page(612, 792)
page = writer.pages[0]
renderer = IconRenderer(GEAR_ICONS)
rect = [100.0, 700.0, 125.0, 730.0]  # Standard test rect
appearance_ref = renderer.render_icon(writer, subject, rect, id_label="test")
# Create annotation dict, add to page, write to buffer
```

**Config override** (using unittest.mock):
```python
from unittest.mock import patch

def mock_get_config(subj):
    config = original_get_icon_config(subj)
    if subj == target_subject:
        config.update(overrides)
    return config

with patch("app.services.icon_config.get_icon_config", side_effect=mock_get_config):
    result = render_icon(...)
```

---

## IMPLEMENTATION PLAN

### Phase 1: Foundation - Package Structure & Region Config

Create the icon_tuner package with region_config.py containing the exact mapping of which icons appear in each reference PDF, in order.

### Phase 2: Reference Extraction

Implement rendering reference PDFs to images and extracting individual icon crops using auto-detection (threshold-based connected component analysis) with manual crop fallback.

### Phase 3: Icon-to-Image Rendering

Implement rendering generated icons to PIL Images by piping through PdfWriter → BytesIO → PyMuPDF → pixmap → PIL Image → crop.

### Phase 4: Similarity Engine

Implement pixel-level comparison metrics: NMAE, histogram intersection, region-based comparison.

### Phase 5: Auto-Tuning Engine

Implement coordinate descent optimization for tunable parameters (color extraction, image scale binary search, offset grid search, font size stepping).

### Phase 6: CLI Entry Point

Create the run_icon_tuner.py script with compare/tune/extract-regions/extract-colors subcommands.

---

## STEP-BY-STEP TASKS

### Task 1: CREATE `backend/scripts/icon_tuner/__init__.py`

- **IMPLEMENT**: Empty package init, just docstring
- **VALIDATE**: `python -c "import sys; sys.path.insert(0, 'backend'); from scripts.icon_tuner import *"`

### Task 2: CREATE `backend/scripts/icon_tuner/region_config.py`

- **IMPLEMENT**: Map each reference PDF to ordered list of deployment subjects matching the visual order discovered from the reference PDFs. Include optional manual crop boxes.
- **PATTERN**: Use the visual analysis above for exact ordering
- **DATA**:
  ```python
  REFERENCE_PDF_DIR = "samples/icons/deploymentIcons"

  # Maps PDF filename → list of (subject, optional_crop_box) tuples
  # Order: left-to-right, top-to-bottom as they appear in the reference PDF
  REFERENCE_REGIONS = {
      "accessPoints.pdf": [
          ("AP - Cisco MR36H", None),
          ("AP - Cisco MR78", None),
          ("AP - Cisco 9166I", None),
          ("AP - Cisco 9166D", None),
          ("AP - Cisco 9120", None),
          ("AP - Cisco Marlin 4", None),
          ("AP - Cisco DB10", None),
      ],
      "switches.pdf": [
          ("SW - Cisco Micro 4P", None),
          ("SW - Fortinet 108F 8P", None),
          ("SW - Cisco 9200 12P", None),
          ("SW - Cisco 9300X 24X", None),
          ("SW - Cisco 9300 12X36M", None),
          ("SW - Cisco 9300X 24Y", None),
          ("SW - Cisco 9500 48Y4C", None),
          # Row 2: IDFs
          ("SW - IDF Cisco 9300 24X", None),
          ("SW - IDF Cisco 9300X 24X", None),
          ("SW - IDF Cisco 9300 12X36M", None),
          ("SW - IDF Cisco 9300X 24Y", None),
          ("SW - IDF Cisco 9500 48Y4C", None),
          # Row 3: NOCs/Distribution
          ("DIST - Starlink", None),
          ("DIST - Micro NOC", None),
          ("DIST - Standard NOC", None),
          ("DIST - MikroTik Hex", None),
      ],
      "hardlines.pdf": [
          ("HL - Access Control", None),
          ("HL - Artist", None),
          ("HL - Audio", None),
          ("HL - CCTV", None),
          ("HL - Clair", None),
          ("HL - Emergency Announce System", None),
          ("HL - General Internet", None),
          ("HL - IPTV", None),
          ("HL - Lighting", None),
          ("HL - Media", None),
          ("HL - PoS", None),
          ("HL - Production", None),
          ("HL - Radios", None),
          ("HL - Sponsor", None),
          ("HL - Streaming", None),
          ("HL - Video", None),
          ("HL - WAN", None),
          # Fiber types
          ("HL - LC SM", None),
          ("HL - SC SM", None),
          ("HL - ST SM", None),
      ],
      "p2p.pdf": [
          ("P2P - Ubiquiti NanoBeam", None),
          ("P2P - Ubiquiti LiteAP", None),
          ("P2P - Ubiquiti Wave Nano", None),
          ("P2P - Ubiquiti Wave Pico", None),
          ("P2P - Ubiquiti Wave AP Micro", None),
          ("P2P - Ubiquiti GigaBeam", None),
          ("P2P - Ubiquiti GigaBeam LR", None),
      ],
      "cameras.pdf": [
          ("CCTV - Cisco MV93X", None),
          ("CCTV - AXIS P5655-E", None),
          ("CCTV - AXIS M5526-E", None),
          ("CCTV - AXIS S9302", None),
      ],
  }
  ```
- **GOTCHA**: The hardlines.pdf ordering needs verification at runtime - use `extract-regions` debug command to confirm
- **GOTCHA**: switches.pdf is LANDSCAPE (792x612), all others are portrait (612x792)
- **VALIDATE**: `cd backend && uv run python -c "from scripts.icon_tuner.region_config import REFERENCE_REGIONS; print(f'{sum(len(v) for v in REFERENCE_REGIONS.values())} icons across {len(REFERENCE_REGIONS)} PDFs')"`

### Task 3: CREATE `backend/scripts/icon_tuner/reference_extractor.py`

- **IMPLEMENT**:
  1. `render_pdf_page_to_image(pdf_path, dpi=300)` - PyMuPDF page.get_pixmap() → PIL Image
  2. `detect_icon_regions(image, min_size=40, merge_distance=5)` - Threshold-based blob detection:
     - Convert to grayscale
     - Threshold at luminance < 220 for non-white pixels
     - Scan rows for dark pixel runs, group via simple flood-fill or row-merge algorithm
     - Compute bounding boxes, filter by size (>40px) and aspect ratio (0.4-1.8)
     - Add padding (10px) around each detected region
     - Sort left-to-right, top-to-bottom (sort by y first with row grouping, then by x within row)
  3. `extract_reference_icons(pdf_path)` - Combine rendering + detection + region_config mapping → `dict[str, PIL.Image]`
  4. `save_annotated_reference(pdf_path, output_dir)` - Debug: draw detected bounding boxes on rendered page, save as PNG with numbered labels
- **IMPORTS**: `fitz` (PyMuPDF), `PIL.Image`, `PIL.ImageDraw`, `pathlib.Path`
- **GOTCHA**: Reference icons include the ID box above AND the "xx' xx°" coordinate label below. The crop should capture the FULL icon including ID box, circle, and model text, but exclude the coordinate label if possible. The coordinate label is separate from the icon itself.
- **GOTCHA**: Some reference icons are closely spaced. If auto-detection merges two icons into one blob, the manual crop fallback in region_config handles this.
- **GOTCHA**: The gray background (~0.9, 0.9, 0.9) in reference PDFs means the threshold should distinguish icon content from the light gray background, not just from white.
- **VALIDATE**: `cd backend && uv run python -c "from scripts.icon_tuner.reference_extractor import extract_reference_icons; from pathlib import Path; icons = extract_reference_icons(Path('..') / 'samples' / 'icons' / 'deploymentIcons' / 'accessPoints.pdf'); print(f'Extracted {len(icons)} icons: {list(icons.keys())}')"`

### Task 4: CREATE `backend/scripts/icon_tuner/icon_comparator.py`

- **IMPLEMENT**:
  1. `render_icon_to_image(subject, config_override=None, rect=None, id_label="test", dpi=300)` → PIL.Image:
     - Default rect: `[100.0, 700.0, 125.0, 730.0]` (same as test_icon_render.py)
     - Create PdfWriter, add blank page (612x792)
     - Use `unittest.mock.patch` to override `get_icon_config` when config_override provided
     - Call `IconRenderer.render_icon()` to get appearance stream
     - Create annotation dict (mirror test_icon_render.py pattern exactly)
     - Write to `io.BytesIO` buffer
     - Open with `fitz.open(stream=buffer.read(), filetype="pdf")`
     - Render page with `page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))`
     - Convert to PIL Image, crop to annotation rect area
     - Account for PDF coordinate system (y-axis flipped): `pixel_y = (page_height - pdf_y) * zoom`
  2. `compute_nmae(img1, img2)` → float (0-1): Normalized Mean Absolute Error
     - Resize both to same dimensions (larger of the two)
     - Sum |pixel1 - pixel2| / (255 * num_pixels)
  3. `compute_histogram_similarity(img1, img2)` → float (0-1): Color histogram intersection
     - Resize both to 64x64
     - Use PIL `.histogram()` (768 bins)
     - Intersection / total
  4. `compute_region_similarity(img1, img2)` → dict[str, float]: Compare subregions
     - Regions: id_box (top 15%), circle (10-95%), brand_zone (15-35%), image_zone (30-70%), model_zone (70-90%)
     - Each region: 1.0 - compute_nmae(crop1, crop2)
  5. `compute_similarity(ref_img, gen_img)` → dict: Combined metrics
     - combined = 0.3*(1-nmae) + 0.2*histogram + 0.5*region_avg
  6. `create_comparison_image(ref_img, gen_img, subject, scores)` → PIL.Image:
     - Side-by-side: reference | generated | pixel diff
     - Resize to same height, add labels using PIL.ImageDraw
- **IMPORTS**: `io`, `fitz`, `PIL.Image`, `PIL.ImageDraw`, `PIL.ImageFont`, `unittest.mock.patch`, `PyPDF2`, icon_renderer, icon_config
- **PATTERN**: Mirror test_icon_render.py lines 62-168 for the annotation creation
- **GOTCHA**: When patching `get_icon_config`, patch it at `app.services.icon_renderer.get_icon_config` (where it's imported), not `app.services.icon_config.get_icon_config`
- **GOTCHA**: PDF y-axis is bottom-up, image y-axis is top-down. The crop calculation must flip: `img_y = (page_height_pts - pdf_y2) * zoom` for top, `(page_height_pts - pdf_y1) * zoom` for bottom
- **GOTCHA**: Reference icons may be much larger than generated icons (reference PDFs show icons at ~100-150px, generated rect produces ~80-100px at 300 DPI). Resize both to same pixel dimensions before comparison.
- **VALIDATE**: `cd backend && uv run python -c "from scripts.icon_tuner.icon_comparator import render_icon_to_image; img = render_icon_to_image('AP - Cisco MR36H'); print(f'Rendered: {img.size}')"`

### Task 5: CREATE `backend/scripts/icon_tuner/auto_tuner.py`

- **IMPLEMENT**:
  1. `extract_dominant_circle_color(ref_img)` → tuple[float,float,float]:
     - Crop to circle region (inner 70% width, rows 20-85% height)
     - Sample pixels, filter out white (>220 lum), black (<30 lum), and near-gray
     - Compute median RGB of remaining pixels
     - Return as 0-1 range
  2. `binary_search_parameter(subject, ref_img, base_config, param_name, low, high, steps=8, metric_fn=None)` → float:
     - Test 3 points each iteration (low, mid, high), narrow around best
     - Returns optimal value rounded to 4 decimals
  3. `grid_search_offsets(subject, ref_img, base_config, x_param, y_param, x_range, y_range, metric_fn=None)` → tuple[float,float]:
     - Grid search over x and y in given ranges with step
     - Returns (best_x, best_y)
  4. `auto_tune_icon(subject, ref_img, current_config, max_iterations=20, threshold=0.85)` → tuple[dict, list]:
     - Phase A: Extract circle color directly (no iteration)
     - Phase B: Binary search img_scale_ratio in [0.3, 2.0]
     - Phase C: Grid search img_x/y_offset in [-2.0, 2.0] step 0.4
     - Phase D: Grid search brand/model x/y offsets
     - Phase E: Step search font sizes in [0.4, 3.0] step 0.2
     - Returns (proposed_overrides, iteration_history)
  5. `generate_proposed_config(results)` → str:
     - Format proposed ICON_OVERRIDES as Python source code
     - Include before/after comments
- **GOTCHA**: Each `render_icon_to_image()` call takes ~0.5-1s. Budget renders carefully:
  - Binary search: 3*8=24 renders max
  - Grid search offsets: (2.0-(-2.0))/0.4 = 10 steps per axis = 100 renders
  - Use coarse grid first (step 1.0), then refine around best (step 0.2)
  - Total budget: ~30-50 renders per icon, ~15-30 seconds per icon
- **VALIDATE**: `cd backend && uv run python -c "from scripts.icon_tuner.auto_tuner import extract_dominant_circle_color; from PIL import Image; img = Image.new('RGB', (100,100), (56, 87, 166)); print(extract_dominant_circle_color(img))"`

### Task 6: CREATE `backend/scripts/run_icon_tuner.py`

- **IMPLEMENT**: CLI entry point with argparse subcommands:
  1. `compare <subject>` - Compare single icon, save comparison image, print score
  2. `compare --category <name>` - Compare all icons in category
  3. `compare --all` - Compare all icons across all reference PDFs
  4. `tune <subject>` - Auto-tune single icon, output proposed overrides
  5. `tune --category <name>` - Auto-tune all icons in category
  6. `tune --all` - Auto-tune everything
  7. `extract-regions` - Debug: save annotated reference images
  8. `extract-colors` - Quick: extract circle colors from all references
- **OUTPUT DIRECTORY**: `backend/scripts/icon_tuner_output/` (created at runtime)
  - `comparisons/` - Side-by-side PNGs
  - `reports/` - Text reports
  - `proposed_overrides.py` - Generated config changes
- **IMPORTS**: argparse, pathlib, all icon_tuner modules
- **PATTERN**: Follow test_icon_render.py sys.path setup
- **VALIDATE**: `cd backend && uv run python scripts/run_icon_tuner.py --help`

### Task 7: UPDATE `.gitignore`

- **ADD**: `icon_tuner_output/` pattern to prevent committing generated comparison images and reports
- **VALIDATE**: `grep icon_tuner_output .gitignore`

### Task 8: Run extract-regions to verify region detection

- **EXECUTE**: `cd backend && uv run python scripts/run_icon_tuner.py extract-regions`
- **VERIFY**: Open output images in `icon_tuner_output/` and confirm bounding boxes correctly isolate individual icons
- **FIX**: If any icons are merged or missed, add manual crop boxes to region_config.py

### Task 9: Run initial comparison baseline

- **EXECUTE**: `cd backend && uv run python scripts/run_icon_tuner.py compare --all`
- **VERIFY**: Check scores and comparison images. Note which icons score well and which need tuning.

### Task 10: Run auto-tuning

- **EXECUTE**: `cd backend && uv run python scripts/run_icon_tuner.py tune --all`
- **VERIFY**: Review proposed overrides in `icon_tuner_output/proposed_overrides.py`
- **VERIFY**: Check before/after comparison images

---

## TESTING STRATEGY

### Unit-Level Validation

Each module has inline validation commands (see VALIDATE lines above). These test individual components in isolation.

### Integration Test

Full pipeline test:
```bash
cd backend && uv run python scripts/run_icon_tuner.py compare "AP - Cisco MR36H"
```
Expected: Outputs score and saves comparison image to `icon_tuner_output/comparisons/`

### Regression Check

Existing tests must still pass:
```bash
cd backend && uv run pytest -x --tb=short
```
Expected: 147 passed, 5 failed (known), 11 skipped (no change)

### Edge Cases

- Reference PDF with icons too close together (switches.pdf - densely packed)
- Icons with no image (FIBER, INFRA - Fiber Patch Panel) - should skip gracefully
- Icons not in any reference PDF - should report as "no reference available"
- Empty/missing reference PDF - should error gracefully
- Config override that produces invalid rendering - should catch and report

### Known Issues

- 5 pre-existing test failures in test_annotation_replacer.py (PyMuPDF/PyPDF2 fixture incompatibility)
- 11 skipped tests (features not yet implemented)
- P2P circle_color is currently purple but reference shows orange - will be auto-corrected
- Camera (CCTV) circle_color is currently brown (IoT default) but reference shows navy blue - will be auto-corrected

---

## VALIDATION COMMANDS

### Level 1: Syntax & Style

```bash
cd backend && uv run ruff check scripts/icon_tuner/ scripts/run_icon_tuner.py
```

### Level 2: Module Import Tests

```bash
cd backend && uv run python -c "from scripts.icon_tuner.region_config import REFERENCE_REGIONS; print('OK')"
cd backend && uv run python -c "from scripts.icon_tuner.reference_extractor import extract_reference_icons; print('OK')"
cd backend && uv run python -c "from scripts.icon_tuner.icon_comparator import render_icon_to_image, compute_similarity; print('OK')"
cd backend && uv run python -c "from scripts.icon_tuner.auto_tuner import auto_tune_icon; print('OK')"
```

### Level 3: Functional Tests

```bash
cd backend && uv run python scripts/run_icon_tuner.py extract-regions
cd backend && uv run python scripts/run_icon_tuner.py compare "AP - Cisco MR36H"
cd backend && uv run python scripts/run_icon_tuner.py compare --category APs
```

### Level 4: Regression

```bash
cd backend && uv run pytest -x --tb=short
```

### Level 5: Full Auto-Tune Run

```bash
cd backend && uv run python scripts/run_icon_tuner.py tune --category APs
```

---

## ACCEPTANCE CRITERIA

- [ ] `extract-regions` correctly isolates individual icons from all 5 reference PDFs
- [ ] `compare` produces valid similarity scores (0-1 range) for all configured icons
- [ ] `compare` saves side-by-side comparison images to output directory
- [ ] `tune` improves similarity scores for at least 80% of icons tested
- [ ] `tune` outputs proposed ICON_OVERRIDES as reviewable Python source
- [ ] Color extraction correctly identifies P2P as orange and cameras as navy blue (fixing current config errors)
- [ ] No new dependencies added (Pillow + PyMuPDF + PyPDF2 only)
- [ ] Existing test suite unaffected (147 passed, 5 failed, 11 skipped)
- [ ] Script handles edge cases gracefully (missing icons, no reference, render failures)

---

## COMPLETION CHECKLIST

- [ ] All 10 tasks completed in order
- [ ] Each task validation passed
- [ ] All validation commands executed successfully
- [ ] Full test suite passes (no regressions)
- [ ] extract-regions output verified visually
- [ ] At least one compare run produces valid output
- [ ] At least one tune run produces proposed config changes
- [ ] Code follows project conventions (ruff clean, type hints)

---

## NOTES

### Performance Budget

- Per icon comparison: ~1-2 seconds
- Per icon full tune: ~15-30 seconds (30-50 renders with coordinate descent)
- Full suite (~55 icons across 5 PDFs): ~15-25 minutes
- Reference images cached after first extraction

### Design Decisions

1. **Pillow-only metrics** - Avoids adding scikit-image/numpy dependencies. NMAE + histogram + region comparison provides sufficient accuracy.
2. **unittest.mock.patch for config override** - Avoids modifying IconRenderer internals. Patches at import site.
3. **Coordinate descent** - More efficient than full grid search given ~1s render cost per evaluation.
4. **Output proposed changes, don't auto-apply** - User reviews config diff before committing to icon_config.py.
5. **Manual subject ordering in region_config** - More reliable than OCR/text extraction (reference PDFs have no extractable text).
6. **Coarse-then-fine grid search** - First pass at step 1.0, refinement at step 0.2 around best. Reduces renders from 100+ to ~30.
