# Plan: Add PDF Layer (OCG) Support to Converted PDFs

## Context

In Bluebeam, deployment icons are organized into "layers" (PDF Optional Content Groups). Currently, the converter outputs PDFs with no layer structure, requiring a manual workflow: open a reference PDF (EVENT26) in Bluebeam, add the converted map to inherit layers, then delete the reference file. This plan eliminates that manual step by embedding all 169 layers from EVENT26 directly into the converted PDF and assigning each annotation to its specific device layer.

## Approach

Create a new `LayerManager` service that reads the EVENT26 reference PDF, clones its full OCProperties structure (169 layers, hierarchy, activation states) into the output PdfWriter, and provides a `subject → OCG reference` lookup. The annotation replacer uses this lookup to add `/OC` entries to each deployment annotation. Also rename 3 fiber connector subjects to match EVENT26 layer names.

---

## Step 1: Rename Fiber Connector Subjects

Rename `HL - LC SM` → `HL - LC Fiber`, `HL - SC SM` → `HL - SC Fiber`, `HL - ST SM` → `HL - ST Fiber` to match EVENT26 layer names.

### Files to modify:
- **`backend/app/services/icon_config.py`** — Rename keys in `ICON_CATEGORIES`, `ICON_OVERRIDES`, `ICON_IMAGE_PATHS`
- **`backend/data/icon_overrides.json`** — Rename keys and `image_path` values
- **`backend/data/mapping.md`** — Update deployment subject column if present
- **`samples/icons/gearIcons/Hardlines/`** — Rename PNG files: `LC SM.png` → `LC Fiber.png`, etc.
- **`backend/tests/test_icon_renderer.py`** — Update any references

---

## Step 2: Add Config Setting

**File: `backend/app/config.py`** (line ~46, after `deployment_map_path`)

Add:
```python
layer_reference_pdf: Path = _PROJECT_ROOT / "samples" / "EVENT26 IT Deployment [v0.0] [USE TO IMPORT LAYER FORMATTING].pdf"
```

---

## Step 3: Create `LayerManager` Service

**New file: `backend/app/services/layer_manager.py`**

Follows the existing services pattern (like `btx_loader.py`).

```
class LayerManager:
    __init__(reference_pdf_path: Path)
    apply_to_writer(writer: PdfWriter) -> bool
    get_ocg_ref(deployment_subject: str) -> IndirectObject | None
    is_loaded: bool
    layer_count: int
```

### `apply_to_writer()` logic:
1. Open EVENT26 with `PdfReader`
2. Get `/OCProperties` from root catalog
3. Clone entire structure into writer via pypdf's `.clone(writer)` — this recursively copies all 169 OCG objects, the `/D` default config (with `/Order` hierarchy and `/AS` activation states), preserving internal references
4. Set `writer._root_object["/OCProperties"]` to the cloned object
5. Build `name → IndirectObject` lookup by iterating the cloned `/OCGs` array
6. Return `True` on success, `False` on any failure (graceful degradation)

### `get_ocg_ref()` logic:
- Simple dict lookup: `self._name_to_ref.get(deployment_subject)`
- Returns `None` if not loaded or no matching layer (e.g., `BOX - JCT`)

---

## Step 4: Integrate into `AnnotationReplacer`

**File: `backend/app/services/annotation_replacer.py`**

### 4a. Constructor (line 66-85)
Add optional `layer_manager` parameter:
```python
def __init__(self, ..., layer_manager: "LayerManager | None" = None):
    ...
    self.layer_manager = layer_manager
```

### 4b. `replace_annotations()` (after line 336, before line 338)
After copying pages to writer, apply layers:
```python
if self.layer_manager:
    self.layer_manager.apply_to_writer(writer)
```

### 4c. `_create_deployment_annotation_dict()` (line 236)
Add `ocg_ref=None` parameter. After line 274 (`/F` flag), add:
```python
if ocg_ref is not None:
    annot[NameObject("/OC")] = ocg_ref
```

### 4d. Conversion loop (line 430-439)
Before calling `_create_deployment_annotation_dict()`, look up OCG:
```python
ocg_ref = self.layer_manager.get_ocg_ref(deployment_subject) if self.layer_manager else None
```
Pass `ocg_ref=ocg_ref` to `_create_deployment_annotation_dict()`.

---

## Step 5: Wire Up in Convert Router

**File: `backend/app/routers/convert.py`** (between lines 99-101)

```python
from app.services.layer_manager import LayerManager

layer_manager = None
if settings.layer_reference_pdf.exists():
    layer_manager = LayerManager(settings.layer_reference_pdf)

replacer = AnnotationReplacer(
    ...,
    layer_manager=layer_manager,
)
```

---

## Step 6: Tests

**New file: `backend/tests/test_layer_manager.py`**

| Test | What it verifies |
|------|-----------------|
| `test_apply_with_real_event26` | 169 OCGs cloned, lookup populated (skip if file missing) |
| `test_missing_reference_pdf` | Returns `False`, `get_ocg_ref()` returns `None` |
| `test_known_subject_lookup` | `get_ocg_ref("AP - Cisco MR36H")` returns IndirectObject |
| `test_unknown_subject_lookup` | `get_ocg_ref("BOX - JCT")` returns `None` |
| `test_before_apply` | `get_ocg_ref()` returns `None` before `apply_to_writer()` |
| `test_fiber_names` | `HL - LC Fiber`, `HL - SC Fiber`, `HL - ST Fiber` all resolve |

Update existing tests for fiber rename in `test_icon_renderer.py`.

---

## Verification

1. **Unit tests**: `cd backend && uv run pytest tests/test_layer_manager.py -v`
2. **Full test suite**: `cd backend && uv run pytest` (expect same baseline: ~167 passed, 7 known failures)
3. **E2E conversion test**: `cd backend && uv run python scripts/test_conversion.py` — verify output PDF has layers
4. **Manual validation**: Open converted PDF in a PDF viewer that supports layers (or Bluebeam) and confirm:
   - All 169 layers appear in the layer panel
   - Toggling a device layer (e.g., "AP - Cisco MR36H") hides/shows only those annotations
   - Hierarchy groups (SWITCHES, ACCESS POINTS, etc.) toggle their children
   - Print/Export activation states preserved
