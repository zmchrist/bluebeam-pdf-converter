# Feature: Fix Annotation Group Movement in Bluebeam

The following plan should be complete, but validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Fix compound annotation groups so that all 7 annotations per deployment icon move as a single unit in Bluebeam Revu, matching the behavior of native Bluebeam deployment icons. Currently, clicking on any component only moves that individual piece rather than the entire icon group.

## User Story

As a deployment technician using Bluebeam Revu
I want converted deployment icons to move as a single grouped unit when I click any part of them
So that I can reposition icons on the map without them splitting apart into individual pieces

## Problem Statement

The converter emits 7 annotations per deployment icon linked via `/IRT` and `/GroupNesting`. In Bluebeam's markup list, these correctly appear grouped under a parent heading. However, when a user clicks and drags any component, only that single annotation moves — the other 6 stay in place. Native Bluebeam deployment icons move as one unit. Two critical PDF properties are missing from our output that control physical group behavior.

## Solution Statement

Add the missing `/RT /Group` relationship type to child annotations and move `/GroupNesting` to the root annotation only (matching native Bluebeam structure). Additionally, add `/DS` (Default Style), `/RC` (Rich Content), and `/IT` (Intent) properties to match Bluebeam's native FreeText and image annotation format, ensuring text survives move/regeneration operations. Users should not be able to edit text on any annotation except hardline bottom text.

## Feature Metadata

**Feature Type**: Bug Fix
**Estimated Complexity**: Low-Medium
**Primary Systems Affected**: `annotation_replacer.py`, `icon_renderer.py`
**Dependencies**: pypdf (existing)

---

## CONTEXT REFERENCES

### Relevant Codebase Files — MUST READ BEFORE IMPLEMENTING

- `backend/app/services/annotation_replacer.py` (lines 247-357) — `_create_compound_annotation_group()` method. This is where the 7 annotations are created with shared properties, root `/Sequence`, and child `/IRT`. The critical fixes (add `/RT /Group`, move `/GroupNesting` to root only) happen here.
- `backend/app/services/annotation_replacer.py` (lines 314-338) — Extra properties handling section. New `/DS`, `/RC`, `/IT` handling must be added here.
- `backend/app/services/icon_renderer.py` (lines 583-788) — `render_compound_icon()` method. Returns component dicts with `extra_props`. New `/DS`, `/RC`, `/IT` properties must be added to the `extra_props` dicts here.
- `backend/app/services/icon_renderer.py` (lines 655-786) — Individual component creation (root ID text, ID box, container, circle, image, model text, brand text). Each FreeText component's `extra_props` needs `/DS` added, and those with text content need `/RC`.
- `backend/tests/test_annotation_replacer.py` (lines 417-496) — `TestCompoundAnnotationGroup` class. Assertions at lines 493-496 check that ALL annotations have `/GroupNesting` — this must change to root only. New assertions for `/RT /Group` on children needed.
- `.agents/plans/compound-annotation-groups.md` (lines 44-82) — Reference data showing native Bluebeam compound annotation structure from `DeploymentMap.pdf`. Shows the 7-annotation structure we're matching.

### New Files to Create

- `backend/scripts/diagnose_group_properties.py` — Diagnostic script to compare native Bluebeam icon properties vs converter output side-by-side

### Patterns to Follow

**Existing annotation property pattern** (from `annotation_replacer.py:316-338`):
```python
# Extra props are passed from icon_renderer as a dict and applied individually
if "/DA" in extra:
    annot[NameObject("/DA")] = TextStringObject(extra["/DA"])
if "/Contents" in extra:
    annot[NameObject("/Contents")] = TextStringObject(extra["/Contents"])
# ... same pattern for /IC, /C, /BS, /RD
```

**Component extra_props pattern** (from `icon_renderer.py:661-674`):
```python
components.append({
    "role": "root_id_text",
    "subtype": "/FreeText",
    "rect": id_rect,
    "ap_ref": id_ap,
    "extra_props": {
        "/DA": "0.2196 0.3412 0.6471 rg /HelvBld 3.90 Tf",
        "/Contents": "j100",
        "/C": [],
        "/BS": {"W": 0},
    },
})
```

**PDF annotation relationship types** (PDF spec 1.7):
- `/RT /R` (default when `/RT` absent) — Reply relationship (like a comment)
- `/RT /Group` — Group relationship (physically grouped annotations)

---

## IMPLEMENTATION PLAN

### Phase 1: Critical Fixes (Group Movement)

Fix the two properties that cause broken group movement. This is the minimum viable fix.

### Phase 2: Secondary Fixes (Text Rendering & Bluebeam Compatibility)

Add `/DS`, `/RC`, and `/IT` properties to match native Bluebeam structure and ensure text survives move/regeneration.

### Phase 3: Testing & Validation

Update tests, generate test PDF, validate in Bluebeam.

---

## STEP-BY-STEP TASKS

### Task 1: UPDATE `annotation_replacer.py` — Add `/RT /Group` to child annotations

This is the primary fix for group movement. One line addition.

**IMPLEMENT:**

In `_create_compound_annotation_group()` (line 350-353), add `/RT /Group` after `/IRT`:

```python
# BEFORE (lines 350-353):
else:
    # Child annotation — /IRT points to root
    annot[NameObject("/IRT")] = root_ref
    ref = writer._add_object(annot)

# AFTER:
else:
    # Child annotation — /IRT points to root, /RT marks as group member
    annot[NameObject("/IRT")] = root_ref
    annot[NameObject("/RT")] = NameObject("/Group")
    ref = writer._add_object(annot)
```

**PATTERN**: Follow existing property assignment pattern at lines 288-307
**GOTCHA**: Without `/RT /Group`, `/IRT` alone defaults to `/RT /R` (reply relationship). Bluebeam treats replies as comments in the markup list, not as physically grouped annotations. This is almost certainly the primary cause of broken group movement.
**VALIDATE**: `cd backend && uv run pytest tests/test_annotation_replacer.py -v`

---

### Task 2: UPDATE `annotation_replacer.py` — Move `/GroupNesting` to root only

Native Bluebeam icons only put `/GroupNesting` on the root annotation, not on children.

**IMPLEMENT:**

1. Remove line 304 from the shared properties section:
```python
# REMOVE this line (currently line 304):
annot[NameObject("/GroupNesting")] = group_nesting
```

2. Add it inside the `if i == 0:` root block (after line 340):
```python
if i == 0:
    # Root annotation — /GroupNesting, /Sequence, NO /IRT
    annot[NameObject("/GroupNesting")] = group_nesting
    annot[NameObject("/Sequence")] = DictionaryObject({
        NameObject("/IID"): TextStringObject(self._sequence_iid),
        NameObject("/Index"): NumberObject(self._sequence_counter),
    })
    self._sequence_counter += 1
    ...
```

**PATTERN**: `/GroupNesting` is already built correctly at lines 274-278. Just moving where it's assigned.
**GOTCHA**: Having `/GroupNesting` on children may confuse Bluebeam's group resolution — each child might be treated as its own group root.
**VALIDATE**: `cd backend && uv run pytest tests/test_annotation_replacer.py -v`

---

### Task 3: UPDATE `icon_renderer.py` — Add `/DS` helper method and `/RC` helper method

Add two helper methods for generating Bluebeam-compatible text style and rich content strings.

**IMPLEMENT:**

Add as static methods or module-level functions near the top of `IconRenderer` class (after existing helpers):

```python
@staticmethod
def _make_ds_string(
    font_size: float,
    color_rgb: tuple[float, float, float],
    text_valign: str = "middle",
) -> str:
    """Generate Bluebeam /DS (Default Style) CSS string for FreeText."""
    hex_color = "#{:02X}{:02X}{:02X}".format(
        int(color_rgb[0] * 255),
        int(color_rgb[1] * 255),
        int(color_rgb[2] * 255),
    )
    line_height = round(font_size * 0.575, 4)
    return (
        f"font: bold Helvetica {font_size}pt; text-align:center; "
        f"text-valign:{text_valign}; margin:0pt; "
        f"line-height:{line_height}pt; color:{hex_color}"
    )

@staticmethod
def _make_rc_string(
    text: str,
    font_size: float,
    color_rgb: tuple[float, float, float],
) -> str:
    """Generate Bluebeam /RC (Rich Content) XHTML string for FreeText."""
    hex_color = "#{:02X}{:02X}{:02X}".format(
        int(color_rgb[0] * 255),
        int(color_rgb[1] * 255),
        int(color_rgb[2] * 255),
    )
    line_height = round(font_size * 0.575, 4)
    return (
        f'<?xml version="1.0"?>'
        f'<body xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/" '
        f'xfa:contentType="text/html" '
        f'xfa:APIVersion="BluebeamPDFRevu:2018" xfa:spec="2.2.0" '
        f'style="font:bold Helvetica {font_size}pt; text-align:center; '
        f'text-valign:middle; margin:0pt; line-height:{line_height}pt; '
        f'color:{hex_color}" '
        f'xmlns="http://www.w3.org/1999/xhtml">'
        f'<p>{text}</p></body>'
    )
```

**PATTERN**: Static methods are consistent with the renderer's style — data transformation helpers
**GOTCHA**: The `line_height` ratio (0.575) comes from analyzing native Bluebeam `/DS` strings in the reference `DeploymentMap.pdf`. The `xfa:APIVersion="BluebeamPDFRevu:2018"` matches the reference but any version should work.
**VALIDATE**: `cd backend && uv run pytest tests/test_icon_renderer.py -v`

---

### Task 4: UPDATE `icon_renderer.py` — Add `/DS`, `/RC`, `/IT` to component extra_props

Add the new properties to each component's `extra_props` dict in `render_compound_icon()`.

**IMPLEMENT:**

1. **Root ID text** (lines 661-675) — Add `/DS` and `/RC`:
```python
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
        "/DS": self._make_ds_string(id_font_size, id_text_color),
        "/RC": self._make_rc_string(
            id_label if not no_id_box else "", id_font_size, id_text_color
        ),
    },
})
```

2. **Container** (lines 697-708) — Add `/DS` only (no `/RC` — empty text):
```python
"extra_props": {
    "/DA": "0 0 0 rg /HelvBld 1 Tf",
    "/Contents": "",
    "/C": [],
    "/BS": {"W": 0},
    "/DS": self._make_ds_string(1.0, circle_color),
},
```

3. **Image** (lines 733-742) — Add `/IT`:
```python
"extra_props": {
    "/C": [1.0, 0.0, 0.0],
    "/BS": {"W": 0},
    "/IT": "/SquareImage",
},
```

4. **Model text** (lines 750-764) — Add `/DS` and `/RC`:
```python
"extra_props": {
    "/DA": (
        f"{text_color[0]:.4f} {text_color[1]:.4f} "
        f"{text_color[2]:.4f} rg /HelvBld {model_font_size:.2f} Tf"
    ),
    "/Contents": model_text,
    "/C": [],
    "/BS": {"W": 0},
    "/DS": self._make_ds_string(model_font_size, text_color),
    "/RC": self._make_rc_string(model_text, model_font_size, text_color),
},
```

5. **Brand text** (lines 771-786) — Add `/DS` and `/RC`:
```python
"extra_props": {
    "/DA": (
        f"{text_color[0]:.4f} {text_color[1]:.4f} "
        f"{text_color[2]:.4f} rg /HelvBld {brand_font_size:.2f} Tf"
    ),
    "/Contents": brand_text,
    "/C": [],
    "/BS": {"W": 0},
    "/DS": self._make_ds_string(brand_font_size, text_color),
    "/RC": self._make_rc_string(brand_text, brand_font_size, text_color),
},
```

**PATTERN**: Mirror existing `extra_props` structure — just adding new keys
**GOTCHA**: ID box border (Square) and Circle do NOT get `/DS` or `/RC` — those are FreeText-only properties. Only the image Square gets `/IT`.
**VALIDATE**: `cd backend && uv run pytest tests/test_icon_renderer.py -v`

---

### Task 5: UPDATE `annotation_replacer.py` — Handle new extra_props keys

Add handling for `/DS`, `/RC`, and `/IT` in the extra properties processing section.

**IMPLEMENT:**

After the existing extra_props handling block (after line 338, before the `if i == 0:` block):

```python
if "/DS" in extra:
    annot[NameObject("/DS")] = TextStringObject(extra["/DS"])
if "/RC" in extra:
    annot[NameObject("/RC")] = TextStringObject(extra["/RC"])
if "/IT" in extra:
    annot[NameObject("/IT")] = NameObject(extra["/IT"])
```

**PATTERN**: Exactly mirrors existing `/DA`, `/Contents`, `/IC`, `/C`, `/BS`, `/RD` handling at lines 316-338
**GOTCHA**: `/DS` and `/RC` use `TextStringObject` (string values). `/IT` uses `NameObject` (PDF name value like `/SquareImage`).
**VALIDATE**: `cd backend && uv run pytest tests/test_annotation_replacer.py -v`

---

### Task 6: UPDATE `test_annotation_replacer.py` — Fix assertions for new grouping structure

Update the test assertions that check compound group structure to match the corrected behavior.

**IMPLEMENT:**

1. Replace lines 493-496 (assertion that ALL annotations have `/GroupNesting`):

```python
# BEFORE (lines 493-496):
# All should share same /GroupNesting
for annot in compound_annots:
    gn = annot.get("/GroupNesting")
    assert gn is not None, "All annotations must have /GroupNesting"

# AFTER:
# Only root should have /GroupNesting
for annot in compound_annots:
    if annot.get("/IRT") is None:
        # Root: must have /GroupNesting
        gn = annot.get("/GroupNesting")
        assert gn is not None, "Root must have /GroupNesting"
    else:
        # Child: must NOT have /GroupNesting
        assert annot.get("/GroupNesting") is None, (
            "Children must NOT have /GroupNesting"
        )

# All children should have /RT /Group
for child in children:
    rt = child.get("/RT")
    assert rt is not None, "Children must have /RT"
    assert str(rt) == "/Group", f"Children /RT must be /Group, got {rt}"
```

**PATTERN**: Follow existing assertion style in the test class (lines 465-491)
**GOTCHA**: The `children` variable is already defined at line 486: `children = [a for a in compound_annots if a.get("/IRT") is not None]`
**VALIDATE**: `cd backend && uv run pytest tests/test_annotation_replacer.py::TestCompoundAnnotationGroup -v`

---

### Task 7: CREATE `backend/scripts/diagnose_group_properties.py` — Diagnostic comparison script

Create a script that dumps all properties from a native Bluebeam icon group and our converter output for side-by-side comparison.

**IMPLEMENT:**

```python
#!/usr/bin/env python
"""
Compare native Bluebeam icon group properties vs converter output.

Usage:
    uv run python scripts/diagnose_group_properties.py [converter_output.pdf]

If no converter output is provided, only analyzes the native DeploymentMap.pdf.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from pypdf import PdfReader


def dump_group_properties(pdf_path: Path, target_subject: str = "AP - Cisco MR36H"):
    """Find and dump all properties of one compound annotation group."""
    reader = PdfReader(pdf_path)
    print(f"\n{'='*80}")
    print(f"PDF: {pdf_path.name}")
    print(f"Looking for group: {target_subject}")
    print(f"{'='*80}")

    for page_num, page in enumerate(reader.pages):
        annots = page.get("/Annots", [])
        group_annots = []

        for annot_ref in annots:
            annot = annot_ref.get_object()
            subj = str(annot.get("/Subj", ""))
            if subj == target_subject:
                group_annots.append(annot)

        if not group_annots:
            continue

        print(f"\nPage {page_num + 1}: Found {len(group_annots)} annotations")

        # Sort: root first (no /IRT), then children
        roots = [a for a in group_annots if a.get("/IRT") is None]
        children = [a for a in group_annots if a.get("/IRT") is not None]

        for idx, annot in enumerate(roots + children):
            is_root = annot.get("/IRT") is None
            subtype = str(annot.get("/Subtype", "?"))
            role = "ROOT" if is_root else "CHILD"
            print(f"\n  --- {role} #{idx + 1} ({subtype}) ---")

            for key in sorted(annot.keys()):
                value = annot[key]
                value_str = str(value)
                if len(value_str) > 150:
                    value_str = value_str[:150] + "..."
                print(f"    {key}: {value_str}")

        # Only analyze first group found
        break


def main():
    project_root = Path(__file__).parent.parent.parent

    # Native Bluebeam reference
    native_pdf = project_root / "samples" / "maps" / "DeploymentMap.pdf"
    if native_pdf.exists():
        dump_group_properties(native_pdf)
    else:
        print(f"WARNING: Native reference not found: {native_pdf}")

    # Converter output (optional argument)
    if len(sys.argv) > 1:
        converter_pdf = Path(sys.argv[1])
        if converter_pdf.exists():
            dump_group_properties(converter_pdf)
        else:
            print(f"ERROR: Converter output not found: {converter_pdf}")


if __name__ == "__main__":
    main()
```

**VALIDATE**: `cd backend && uv run python scripts/diagnose_group_properties.py`

---

### Task 8: Run full test suite and generate test PDF

**IMPLEMENT:**

1. Run full test suite:
```bash
cd backend && uv run pytest --tb=short
```

2. Generate test conversion PDF:
```bash
cd backend && uv run python scripts/test_conversion.py
```

3. Run diagnostic script on the converter output to verify properties match native:
```bash
cd backend && uv run python scripts/diagnose_group_properties.py <path-to-converter-output.pdf>
```

**VALIDATE**: Tests: ~186 passed, 3 known failures, 11 skipped. Conversion: 98 converted, 2 skipped.

---

## TESTING STRATEGY

### Unit Tests

- `test_annotation_replacer.py::TestCompoundAnnotationGroup::test_compound_group_structure` — Updated to verify:
  - Root has `/GroupNesting`, children do NOT
  - All children have `/RT /Group`
  - All children have `/IRT` pointing to root
  - All annotations have unique `/NM`
- `test_annotation_replacer.py::TestCompoundAnnotationGroup::test_compound_converted_count_is_logical` — Unchanged, still verifies count = logical icons

### Integration Tests

- `test_conversion.py` script — End-to-end conversion produces valid PDF with 98 icons

### Edge Cases

- Icons with fewer than 7 components (no image, no brand) — must still have `/RT /Group` on all children
- Icons with `no_id_box: True` — fewer components but same grouping structure
- Hardline icons — bottom text FreeText should remain editable (no additional lock flags)

### Known Issues

- Pre-existing: 1 failure in `test_annotation_replacer.py` (PyMuPDF/pypdf fixture incompatibility)
- Pre-existing: 2 failures in `test_icon_renderer.py` (outdated assertions)
- Pre-existing: 11 skipped tests

---

## VALIDATION COMMANDS

### Level 1: Syntax & Style

```bash
cd backend && uv run ruff check app/services/annotation_replacer.py app/services/icon_renderer.py
```

### Level 2: Unit Tests

```bash
cd backend && uv run pytest tests/test_annotation_replacer.py tests/test_icon_renderer.py -v
```

### Level 3: Full Test Suite

```bash
cd backend && uv run pytest --tb=short
```

Expected: ~186 passed, 3 failed (known), 11 skipped

### Level 4: End-to-End Conversion

```bash
cd backend && uv run python scripts/test_conversion.py
```

Expected: 98 converted, 2 skipped, output PDF generated

### Level 5: Diagnostic Comparison

```bash
cd backend && uv run python scripts/diagnose_group_properties.py <converter-output.pdf>
```

Verify: Children have `/RT /Group`, only root has `/GroupNesting`, FreeText has `/DS` and `/RC`

### Level 6: Manual Bluebeam Validation

Open converted PDF in Bluebeam Revu and verify:
1. Click any component of a deployment icon → entire group selects
2. Drag the selected icon → all 7 annotations move together
3. Icons appear correctly grouped in the Markup List
4. Layer toggling still works (OC groups)
5. Text is NOT editable on standard icons (try double-clicking)
6. Hardline bottom text IS editable

---

## ACCEPTANCE CRITERIA

- [ ] Children have `/RT /Group` set (verified by test + diagnostic script)
- [ ] Only root has `/GroupNesting` (verified by test)
- [ ] FreeText annotations have `/DS` and `/RC` properties
- [ ] Image Square has `/IT /SquareImage`
- [ ] Icons move as a single unit in Bluebeam (manual test)
- [ ] All validation commands pass (expected known failures only)
- [ ] No regressions in existing functionality
- [ ] `converted_count` still reports logical icon count (not annotation count)
- [ ] Diagnostic script shows converter output matches native structure

---

## COMPLETION CHECKLIST

- [ ] All tasks completed in order (1-8)
- [ ] Each task validation passed immediately
- [ ] All validation commands executed successfully
- [ ] Full test suite passes (expected failures only)
- [ ] No linting errors
- [ ] End-to-end conversion generates valid PDF
- [ ] Diagnostic comparison confirms property alignment with native Bluebeam icons

---

## NOTES

### Design Decisions

1. **Why `/RT /Group` is the fix**: The PDF 1.7 spec defines `/RT` as the relationship type for `/IRT`. Without `/RT`, the default is `/R` (reply), which Bluebeam treats as a comment-style relationship (visible in markup list hierarchy but individually movable). `/RT /Group` explicitly tells Bluebeam these are physically grouped annotations that should move together.

2. **Why move `/GroupNesting` to root only**: Native Bluebeam icons only put `/GroupNesting` on the root. Having it on children is redundant at best and potentially confusing — Bluebeam may interpret each child as a separate group root.

3. **`/DS` and `/RC` are secondary but important**: These ensure Bluebeam can properly regenerate FreeText content after move operations. Without them, text may not render correctly if Bluebeam regenerates the appearance stream from annotation-level properties.

4. **Text editability**: The user requires that text should NOT be editable except for hardline bottom text. With `/RT /Group`, the group moves as one unit. If testing shows text is still editable on non-hardline icons after the grouping fix, we can add the LockedContents annotation flag (`/F` bit 10 = 512) as a follow-up task. Native Bluebeam icons use `/F 4` (Print only) so this may need separate investigation.

5. **`/BSIColumnData` omitted**: Native icons have 23-entry `/BSIColumnData` arrays (Bluebeam column tracking). We continue omitting this — Bluebeam populates it on first edit. Not needed for group movement.

### Risk Assessment

- **Low risk**: `/RT /Group` is a single line addition, directly from the PDF spec
- **Low risk**: Moving `/GroupNesting` is a simple code rearrangement
- **Low risk**: `/DS`/`/RC`/`/IT` are additive properties — they can't break existing functionality
- **Unknown**: Whether `/RT /Group` fully solves group movement in Bluebeam. If it doesn't, the diagnostic script will help identify remaining differences. The most likely alternative would be Bluebeam-specific proprietary properties (like `/BSI*` keys) that we'd need to reverse-engineer from the reference PDF.
