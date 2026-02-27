# Feature: Compound Annotation Groups (Bluebeam-Native Icon Structure)

The following plan should be complete, but validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Refactor annotation output from a single complex `/Circle` annotation with a rich `/AP` stream to **7 separate annotations per icon grouped via Bluebeam's `/GroupNesting` system**. This matches how Bluebeam Revu natively creates deployment icons, ensuring they survive move/resize operations without losing their visual appearance.

## User Story

As a deployment technician using Bluebeam Revu
I want converted deployment icons to be fully editable (movable, resizable, selectable)
So that I can adjust icon positions on the map without them turning into plain circles

## Problem Statement

Our converter creates a single `/Circle` annotation with everything (circle + ID box + gear image + brand text + model text) packed into one complex appearance stream. When Bluebeam moves this annotation, it regenerates the appearance from native `/Circle` properties (`/IC`, `/C`, `/BS`), discarding our rich appearance. The icon turns into a plain blue circle with a black border.

## Solution Statement

Emit **compound annotation groups** matching Bluebeam's native structure: 7 separate annotations per icon, each with its own simple appearance stream, linked via `/IRT` (In Reply To) and `/GroupNesting` (Bluebeam-proprietary grouping). Each component is simple enough that Bluebeam can regenerate it on move. All use absolute BBox + Matrix coordinates, as confirmed by reference PDF analysis.

## Feature Metadata

**Feature Type**: Bug Fix / Architectural Refactor
**Estimated Complexity**: High
**Primary Systems Affected**: `annotation_replacer.py`, `icon_renderer.py`
**Dependencies**: pypdf (existing), Pillow (existing)

---

## CONTEXT REFERENCES

### Relevant Codebase Files — MUST READ BEFORE IMPLEMENTING

- `backend/app/services/annotation_replacer.py` (full file) — Current single-annotation creation logic. The `_create_deployment_annotation_dict()` method (lines 248-331) and `replace_annotations()` loop (lines 333-505) must be restructured to emit 7 annotations instead of 1.
- `backend/app/services/icon_renderer.py` (full file) — Current combined appearance stream builder. The `_create_appearance_stream()` (lines 244-411) and `_build_content_stream()` (lines 413-573) contain all the layout math and rendering that must be decomposed into per-component streams.
- `backend/app/services/icon_config.py` (full file) — Icon configuration, category defaults, per-icon overrides, ID assignment. The layout parameters (circle_color, id_box_height, img_scale_ratio, brand_text, model_text, font sizes, offsets) drive component sizing and must be used to compute per-component rects.
- `backend/tests/test_annotation_replacer.py` — Existing tests that will need updating for the new multi-annotation output.
- `backend/tests/test_icon_renderer.py` — Existing renderer tests.

### Reference Data — Bluebeam Native Compound Annotation Structure

A single "AP - Cisco MR36H" icon in the reference `DeploymentMap.pdf` consists of **7 annotations**:

| Order | `/NM` | `/Subtype` | Purpose | `/IRT` | Rect Size |
|-------|-------|-----------|---------|--------|-----------|
| 1 | ZWFFSOLMOSBTDZTQ | `/FreeText` | **ROOT** — ID box text ("j165") | None | 25.78 x 12.73 |
| 2 | BGPLVXBOXOKHASMO | `/Square` | White ID box border | → root | 17.39 x 6.90 |
| 3 | LSCRBNWAXGBECNSW | `/FreeText` | Overall bounding container | → root | 27.63 x 36.79 |
| 4 | XLDOXJOKFATNYCMO | `/Circle` | Blue filled circle | → root | 22.91 x 22.92 |
| 5 | SZCSZPRIRJLCIMEF | `/Square` | Gear image (has /XObject) | → root | 7.05 x 7.24 |
| 6 | RTZGTNQPCNGSUHWI | `/FreeText` | Model text ("MR36H") | → root | 27.22 x 11.08 |
| 7 | JLKEFVZRPPLNYXGU | `/FreeText` | Brand text ("CISCO") | → root | 27.22 x 11.08 |

**Shared properties across all 7:**
- `/Subj`: Same deployment subject (e.g., "AP - Cisco MR36H")
- `/OC`: Same OCG layer reference
- `/F`: 4 (Print flag)
- `/T`: Author name
- `/M`, `/CreationDate`: Same timestamps
- `/BSIColumnData`: 23-entry array (Bluebeam column tracking)
- **BBox**: Absolute page coordinates `[x1, y1, x2, y2]`
- **Matrix**: `[1, 0, 0, 1, -x1, -y1]` (translates to origin)

**Root-only properties:**
- `/GroupNesting`: `[subject, /NM1, /NM2, /NM3, /NM4, /NM5, /NM6, /NM7]`
- `/Sequence`: `{/IID: <16-char-uuid>, /Index: <int>}`
- No `/IRT`

**Child-only properties:**
- `/IRT`: IndirectObject reference to root annotation
- `/GroupNesting`: Same array as root (copied to all children)

**Content stream patterns from reference PDF:**
- Circle: `0 0 0 RG 0.5968134 w 0.2196078 0.3411765 0.6470588 rg [bezier]` — draws at absolute coords
- Image: `q 7.046387 0 0 7.240723 5062.38 5890.938 cm /Image Do Q` — absolute cm
- Text: `BT ... 1 0 0 1 <abs_x> <abs_y> Tm (<text>) Tj ET` — uses Tm matrix
- ID text: Same pattern with `/HelvBld` font and circle color for text

### New Files to Create

None — all changes are within existing files.

### Patterns to Follow

**Absolute BBox + Matrix** (confirmed from every Bluebeam annotation):
```python
ap_stream[NameObject("/BBox")] = ArrayObject([
    FloatObject(x1), FloatObject(y1), FloatObject(x2), FloatObject(y2),
])
ap_stream[NameObject("/Matrix")] = ArrayObject([
    NumberObject(1), NumberObject(0), NumberObject(0), NumberObject(1),
    FloatObject(-x1), FloatObject(-y1),
])
```

**Content streams draw at absolute coordinates** (the Matrix handles translation):
```python
# Circle Bezier at absolute (cx, cy)
# Image cm at absolute (img_x, img_y)
# Text Tm at absolute (text_x, text_y)
```

**GroupNesting format** (Bluebeam proprietary):
```python
# First entry = subject name, remaining = /NM values prefixed with /
[TextStringObject("AP - Cisco MR36H"),
 TextStringObject("/ABCD1234EFGH5678"),
 TextStringObject("/IJKL9012MNOP3456"),
 ...]
```

**IRT linking** — children reference the root's IndirectObject:
```python
child_annot[NameObject("/IRT")] = root_ref  # IndirectObject from writer._add_object(root)
```

**FreeText annotations** require `/DA` (default appearance) and `/Contents`:
```python
annot[NameObject("/DA")] = TextStringObject("0.22 0.34 0.65 rg /HelvBld 4.38 Tf")
annot[NameObject("/Contents")] = TextStringObject("j100")
```

---

## IMPLEMENTATION PLAN

### Phase 1: Decompose Icon Renderer Into Component Renderers

Refactor `icon_renderer.py` to produce individual appearance streams for each visual component instead of one combined stream. Keep the layout computation logic (canonical 25x30 space, scaling, offsets) but output separate AP streams.

### Phase 2: Build Compound Annotation Groups

Refactor `annotation_replacer.py` to emit 7 annotations per icon instead of 1. Create each component annotation with its own rect, simple appearance, and proper IRT/GroupNesting linking.

### Phase 3: Update Simple Appearance Fallback

For icons without gear images (`no_image: True`), still emit a compound group but with fewer components (no image square, potentially no brand text).

### Phase 4: Testing & Validation

Update tests, generate test PDFs, validate in Bluebeam.

---

## STEP-BY-STEP TASKS

### Task 1: UPDATE `icon_renderer.py` — Add component-level rendering methods

The core refactor. Add methods that produce individual appearance streams for each of the 7 components. Keep `render_icon()` as the public API but change its return type.

**IMPLEMENT:**

1. Add a new public method `render_compound_icon()` that returns a list of component dicts instead of a single AP ref:

```python
def render_compound_icon(
    self,
    writer: PdfWriter,
    subject: str,
    center: tuple[float, float],  # (cx, cy) center position
    id_label: str = "j100",
) -> list[dict] | None:
    """
    Render a deployment icon as compound annotation components.

    Returns list of component dicts, each with:
    - "role": str — "root_id_text", "id_box_border", "container", "circle", "image", "model_text", "brand_text"
    - "subtype": str — "/FreeText", "/Circle", "/Square"
    - "rect": list[float] — [x1, y1, x2, y2] absolute page coords
    - "ap_ref": IndirectObject — appearance stream reference
    - "extra_props": dict — additional annotation properties (/DA, /Contents, /IC, /C, /BS, etc.)
    """
```

2. Add private methods for each component's appearance stream:
   - `_render_circle_ap(writer, rect, circle_color, border_color, border_width)` — Bezier circle at absolute coords
   - `_render_id_box_ap(writer, rect, border_width)` — White filled rectangle with black border
   - `_render_image_ap(writer, rect, image_xobject_ref)` — Image drawn at absolute coords
   - `_render_text_ap(writer, rect, text, font_size, text_color, alignment)` — Text at absolute coords
   - `_render_id_text_ap(writer, rect, id_label, font_size, text_color)` — ID text (FreeText root)

3. Add a layout computation method that calculates rects for all 7 components given a center point:

```python
def _compute_component_rects(
    self,
    cx: float, cy: float,
    config: dict,
    img_width: int, img_height: int,
) -> dict[str, list[float]]:
    """
    Compute absolute page rects for all compound annotation components.

    Uses existing canonical 25x30 coordinate space math from _create_appearance_stream,
    but outputs absolute rects instead of relative offsets.

    Returns dict mapping role -> [x1, y1, x2, y2].
    """
```

The layout math should reuse the existing canonical space calculations from `_create_appearance_stream()` (lines 277-328 of current code), but transform from canonical coordinates to absolute page coordinates.

**Key layout computation:**
```python
# Canonical space (25x30) scaled to fit standard icon size
CANON_W, CANON_H = 25.0, 30.0
render_scale = min(STANDARD_ICON_SIZE / CANON_W, STANDARD_ICON_SIZE / CANON_H)

# Overall annotation bounding box (container)
half_w = (CANON_W * render_scale) / 2
half_h = (CANON_H * render_scale) / 2
container_rect = [cx - half_w, cy - half_h, cx + half_w, cy + half_h]

# Each component rect is computed from canonical positions transformed to page coords
# Example: circle center in canonical = (12.5, cy_canon)
# Absolute circle center = (cx - half_w + 12.5 * render_scale, cy - half_h + cy_canon * render_scale)
```

**IMPORTANT — Standard icon size consideration:**
Currently `STANDARD_ICON_SIZE = 14.6` fits everything in one 14.6x14.6 square. With compound annotations, the overall bounding rect needs to be larger. The Bluebeam reference shows ~27.63 x 36.79 pts for the container. Scale proportionally from canonical 25x30 space. Consider bumping the effective size or computing it dynamically from the canonical space. The render_scale calculation already handles this — just ensure the annotation rects are computed from the full canonical height (30 pts) not just the width.

The overall icon size should be: `CANON_H * render_scale` tall by `CANON_W * render_scale` wide.
With `render_scale = STANDARD_ICON_SIZE / CANON_H = 14.6 / 30 = 0.4867`:
- Width = 25 * 0.4867 = 12.17 pts
- Height = 14.6 pts (= 30 * 0.4867)

This makes icons taller than wide (matching Bluebeam's proportions). If this is too small, bump `STANDARD_ICON_SIZE` to something larger (e.g., 20 or 25 pts). Test visually.

**PATTERN**: Reuse math from `icon_renderer.py:277-328` (canonical space layout)
**GOTCHA**: Content streams MUST draw at absolute page coordinates. The Matrix `[1,0,0,1,-x1,-y1]` translates the coordinate system so `(x1,y1)` maps to the origin for rendering. This means content at `(x1, y1)` renders at the BBox origin.
**GOTCHA**: FreeText annotations use `/DA` (Default Appearance) string instead of just content stream fonts. Format: `"<r> <g> <b> rg /HelvBld <size> Tf"`. The text is positioned with `Tm` operator (text matrix) at absolute coordinates.
**VALIDATE**: `cd backend && uv run pytest tests/test_icon_renderer.py -v`

---

### Task 2: UPDATE `annotation_replacer.py` — Emit compound annotation groups

Restructure the conversion loop to create 7 annotations per icon instead of 1.

**IMPLEMENT:**

1. Add a new method `_create_compound_annotation_group()` that orchestrates creating all 7 annotations:

```python
def _create_compound_annotation_group(
    self,
    writer: PdfWriter,
    components: list[dict],  # From icon_renderer.render_compound_icon()
    deployment_subject: str,
    ocg_ref=None,
) -> list[IndirectObject]:
    """
    Create a compound annotation group (7 linked annotations).

    Returns list of IndirectObject refs to append to page /Annots array.
    """
```

2. The method should:
   a. Generate unique `/NM` (16-char hex UUID) for each of the 7 annotations
   b. Create the **root annotation first** (always a `/FreeText` for the ID box text)
   c. Register root with `writer._add_object()` to get an `IndirectObject` ref
   d. Build `/GroupNesting` array: `[subject, /NM1, /NM2, ..., /NM7]`
   e. Create each **child annotation** with `/IRT` pointing to root's `IndirectObject`
   f. Copy `/GroupNesting` to every annotation (root + all children)
   g. Register each child with `writer._add_object()`
   h. Return list of all `IndirectObject` refs

3. Shared annotation properties for ALL 7 annotations:
```python
annot[NameObject("/Type")] = NameObject("/Annot")
annot[NameObject("/Subj")] = TextStringObject(deployment_subject)
annot[NameObject("/F")] = NumberObject(4)
annot[NameObject("/T")] = TextStringObject("PDF Converter")
annot[NameObject("/M")] = TextStringObject(now)
annot[NameObject("/CreationDate")] = TextStringObject(now)
annot[NameObject("/NM")] = TextStringObject(nm)
annot[NameObject("/OC")] = ocg_ref  # if present
annot[NameObject("/GroupNesting")] = group_nesting_array
# AP dict with /N pointing to component's ap_ref
```

4. Root-only properties:
```python
root[NameObject("/Sequence")] = DictionaryObject({
    NameObject("/IID"): TextStringObject(uuid.uuid4().hex[:16].upper()),
    NameObject("/Index"): NumberObject(sequence_index),
})
# NO /IRT on root
```

5. Child-only properties:
```python
child[NameObject("/IRT")] = root_indirect_ref
```

6. Per-component specific properties:

   **Circle child:**
   ```python
   annot[NameObject("/Subtype")] = NameObject("/Circle")
   annot[NameObject("/IC")] = ArrayObject([FloatObject(r), FloatObject(g), FloatObject(b)])
   annot[NameObject("/C")] = ArrayObject([FloatObject(0), FloatObject(0), FloatObject(0)])
   annot[NameObject("/BS")] = border_style_dict
   annot[NameObject("/RD")] = rd_array
   ```

   **Square children (ID box, image):**
   ```python
   annot[NameObject("/Subtype")] = NameObject("/Square")
   # ID box: /IC white, /C black, /BS with border width
   # Image: /C red (1,0,0), /BS /W 0 (invisible border)
   ```

   **FreeText children (root ID text, model, brand):**
   ```python
   annot[NameObject("/Subtype")] = NameObject("/FreeText")
   annot[NameObject("/DA")] = TextStringObject(da_string)
   annot[NameObject("/Contents")] = TextStringObject(text_content)
   annot[NameObject("/C")] = ArrayObject([])  # Empty = no visible border
   annot[NameObject("/BS")] = DictionaryObject({"/W": FloatObject(0), "/S": NameObject("/S")})
   ```

7. Update the main conversion loop in `replace_annotations()` (around line 454-480):

```python
# BEFORE (single annotation):
# appearance_ref = self._render_rich_icon(...)
# new_annot = self._create_deployment_annotation_dict(...)
# new_annot_ref = writer._add_object(new_annot)
# new_annots.append(new_annot_ref)

# AFTER (compound group):
components = self.icon_renderer.render_compound_icon(
    writer, deployment_subject, (cx, cy), id_label=id_label
)
if components:
    annot_refs = self._create_compound_annotation_group(
        writer, components, deployment_subject, ocg_ref=ocg_ref
    )
    new_annots.extend(annot_refs)  # Append ALL 7 refs
    converted_count += 1
else:
    # Fallback: simple single annotation (for no_image icons)
    # ... existing simple appearance logic ...
```

**IMPORTANT**: The `converted_count` should still increment by 1 per icon (not 7). The count represents logical icons converted, not PDF annotations created.

**PATTERN**: Follow the `/IRT` linking pattern from existing IRT filtering code at `annotation_replacer.py:411`
**GOTCHA**: `/GroupNesting` entries after the first must be prefixed with `/` — format is `TextStringObject("/ABCDEF1234567890")`
**GOTCHA**: The root annotation must be registered (`_add_object`) BEFORE creating children, because children need its `IndirectObject` ref for `/IRT`
**GOTCHA**: ALL 7 annotations must be appended to the page's `/Annots` array. If any are missing, Bluebeam won't find the group members and grouping breaks.
**VALIDATE**: `cd backend && uv run pytest tests/test_annotation_replacer.py -v`

---

### Task 3: UPDATE `annotation_replacer.py` — Handle simple/fallback icons as compound groups too

Icons with `no_image: True` (FIBER, INFRA - Fiber Patch Panel) or those without gear images should still use compound groups but with fewer components.

**IMPLEMENT:**

For icons that `icon_renderer.can_render()` returns False:
- Still create a compound group with: root (ID text), circle, ID box border
- Skip: image square, brand text (if empty), model text (if empty)
- Minimum viable group: 3 annotations (root + circle + ID box)

Update `_create_simple_appearance()` to produce a simple circle AP stream for the circle component, and use the compound group builder.

If even compound groups aren't possible (edge case), fall back to the existing single-annotation approach.

**VALIDATE**: `cd backend && uv run pytest -v`

---

### Task 4: UPDATE `annotation_replacer.py` — Track sequence index

Bluebeam uses `/Sequence` with `/IID` (group identifier) and `/Index` (sequential counter across all groups in the PDF). Add a counter to the replacer.

**IMPLEMENT:**

Add a sequence counter to `AnnotationReplacer.__init__()`:
```python
self._sequence_counter = 0
```

Increment after each compound group is created. Reset in `replace_annotations()` alongside `self.id_assigner.reset()`.

The `/IID` should be the same for ALL groups in one conversion run (it's a document-level identifier). Generate once at the start of `replace_annotations()`.

**VALIDATE**: `cd backend && uv run pytest -v`

---

### Task 5: UPDATE tests — Adapt for compound annotation output

Update existing tests that check annotation counts and structure.

**IMPLEMENT:**

1. In `test_annotation_replacer.py`, update assertions that check for single annotations to expect 7 per converted icon (or the test's expected count * 7 total annotations).

2. Add a new test `test_compound_group_has_correct_structure()` that verifies:
   - Root has `/GroupNesting` with correct count
   - Root has no `/IRT`
   - All children have `/IRT` pointing to root
   - All share same `/Subj`, `/OC`
   - All have unique `/NM` values
   - `/GroupNesting` contains all `/NM` values

3. Update `test_icon_renderer.py` for the new `render_compound_icon()` method.

**VALIDATE**: `cd backend && uv run pytest -v`

---

### Task 6: Generate test PDF and validate

**IMPLEMENT:**

Run `test_conversion.py` to generate a converted PDF. Verify:
1. File generates without errors
2. Annotation count is ~7x previous (98 icons * 7 = ~686 annotations, plus preserved originals)
3. Open in a PDF reader to verify visual appearance

**VALIDATE**: `cd backend && uv run python scripts/test_conversion.py`

---

## TESTING STRATEGY

### Unit Tests

- `test_icon_renderer.py`: Test `render_compound_icon()` returns correct number of components with expected roles, rects, and AP refs
- `test_icon_renderer.py`: Test `_compute_component_rects()` produces valid non-overlapping rects centered on the given position
- `test_annotation_replacer.py`: Test `_create_compound_annotation_group()` creates proper IRT/GroupNesting structure

### Integration Tests

- `test_annotation_replacer.py`: Test full `replace_annotations()` produces valid PDF with compound groups
- `test_conversion.py`: End-to-end conversion produces valid PDF

### Edge Cases

- Icons with `no_image: True` — should produce fewer components but still a valid group
- Icons with empty `brand_text` — skip brand FreeText component
- Icons with multi-line model text (e.g., "GENERAL\nINTERNET") — handle in model FreeText
- Very small or very large annotation rects from bid PDF
- Icons without ID prefix config (no ID label) — handle `no_id_box` config

### Known Issues

- Pre-existing test failures (expected, should not block):
  - 1 in `test_annotation_replacer.py` — PyMuPDF/pypdf fixture incompatibility
  - 2 in `test_icon_renderer.py` — outdated assertions
  - 11 skipped tests

---

## VALIDATION COMMANDS

### Level 1: Syntax & Style

```bash
cd backend && uv run ruff check app/services/icon_renderer.py app/services/annotation_replacer.py
```

### Level 2: Unit Tests

```bash
cd backend && uv run pytest tests/test_icon_renderer.py tests/test_annotation_replacer.py -v
```

### Level 3: Full Test Suite

```bash
cd backend && uv run pytest --tb=short
```

Expected: 177+ passed, 3 failed (known), 11 skipped

### Level 4: End-to-End Conversion

```bash
cd backend && uv run python scripts/test_conversion.py
```

Expected: 98 converted, 2 skipped, output PDF generated

### Level 5: Manual Bluebeam Validation

Open converted PDF in Bluebeam Revu and verify:
1. Icons are visible at correct positions
2. Icons can be selected
3. Icons can be moved WITHOUT losing their appearance
4. Icons can be resized
5. Layer toggling still works (OC groups)
6. ID text is readable

---

## ACCEPTANCE CRITERIA

- [ ] Each converted icon produces 7 linked annotations (or fewer for simple icons)
- [ ] Root annotation has `/GroupNesting` with all member `/NM` values
- [ ] All children have `/IRT` pointing to root `IndirectObject`
- [ ] All annotations use absolute BBox `[x1,y1,x2,y2]` + Matrix `[1,0,0,1,-x1,-y1]`
- [ ] Content streams draw at absolute page coordinates
- [ ] Icons are visible in Bluebeam at correct positions
- [ ] Icons survive move operations (appearance preserved after drag)
- [ ] Icons are selectable, resizable, deletable in Bluebeam
- [ ] OCG layer toggling still works
- [ ] All validation commands pass (expected failures only)
- [ ] No regressions in existing functionality
- [ ] `converted_count` still reports logical icon count (not annotation count)

---

## COMPLETION CHECKLIST

- [ ] All tasks completed in order
- [ ] Each task validation passed immediately
- [ ] All validation commands executed successfully
- [ ] Full test suite passes (expected failures only)
- [ ] No linting errors
- [ ] End-to-end conversion generates valid PDF
- [ ] Manual Bluebeam testing confirms move-survivability

---

## NOTES

### Design Decisions

1. **Why 7 annotations?** This exactly matches Bluebeam's native structure. Fewer might work but risks incompatibility. More would be unnecessary.

2. **Why absolute coordinates everywhere?** Every annotation in the Bluebeam reference PDF uses absolute BBox + Matrix. This is confirmed across all 7 components of multiple icon groups. Zero-origin BBox was our invention and Bluebeam doesn't preserve it on move.

3. **Why `/FreeText` as root?** Bluebeam's root is always a `/FreeText` containing the ID text. This is the "primary" annotation that Bluebeam uses for selection, counting, and column management.

4. **`/BSIColumnData` omission**: The reference has 23-entry `/BSIColumnData` arrays on all annotations. This is a Bluebeam-specific extension for column management. We can omit it initially — Bluebeam will likely populate it on first edit. Add later if needed.

5. **`/DS` and `/RC` omission for FreeText**: The reference has `/DS` (default style CSS) and `/RC` (rich content XML) on FreeText annotations. These are optional — Bluebeam uses `/DA` + `/Contents` as the primary text source. We can add `/DS`/`/RC` later if text rendering is incorrect.

6. **Icon Tuner impact**: The Icon Tuner (`/tuner` route) renders preview icons using the combined approach. It doesn't need to change — it's purely for visual preview, not PDF output. The tuner canvas can continue using the combined rendering.

### Risk Assessment

- **Medium risk**: Getting the exact relative component positions right. The canonical 25x30 space math is well-tested, but transforming to absolute per-component rects is new code. Mitigate with careful unit tests.
- **Low risk**: IRT/GroupNesting linking — straightforward PDF dictionary construction.
- **Low risk**: Bluebeam compatibility — we're matching the exact structure from their own output.
- **Unknown**: Whether Bluebeam needs `/DS`/`/RC` on FreeText to render text correctly. Test without first, add if needed.
