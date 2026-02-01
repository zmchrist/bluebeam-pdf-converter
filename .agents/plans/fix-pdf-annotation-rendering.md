# Feature: Fix PDF Annotation Rendering Issue

The following plan should be complete, but validate documentation and codebase patterns before implementing.

## Feature Description

Fix the critical bug where converted PDF annotations are invisible despite the conversion script reporting success. The root cause is that PyPDF2 cannot properly clone appearance streams (`/AP`) between PDFs - the indirect object references become invalid in the target PDF, and the `/AP` dictionary structure is malformed.

**Solution:** Migrate annotation creation from PyPDF2 to PyMuPDF (fitz), which automatically generates valid appearance streams when `annot.update()` is called.

## User Story

As a project estimator
I want converted deployment icons to be visible in the output PDF
So that I can verify the conversion was successful and use the deployment map immediately

## Problem Statement

The current implementation uses PyPDF2 to clone annotations from a reference PDF (DeploymentMap.pdf) to the output PDF. This fails because:

1. **Broken indirect object references**: The `/AP` dictionary contains references like `42 0 R` that point to objects in the source PDF, not the target PDF
2. **Malformed /AP structure**: Code assigns an IndirectObject directly to `/AP` instead of a dictionary with `/N` key
3. **Silent fallback failure**: When appearance extraction fails, the fallback path creates annotations with colors but NO appearance stream - making them invisible

**Evidence:** Scripts report "376/376 converted" but icons don't render in output PDF.

## Solution Statement

Replace PyPDF2-based annotation creation with PyMuPDF, which:
1. Creates annotations with native methods (`page.add_circle_annot()`, etc.)
2. Automatically generates valid appearance streams via `annot.update()`
3. Doesn't rely on cloning indirect objects between PDFs
4. Handles coordinate preservation naturally via `pymupdf.Rect`

## Feature Metadata

**Feature Type**: Bug Fix
**Estimated Complexity**: Medium
**Primary Systems Affected**: `annotation_replacer.py`, `pdf_parser.py`, `appearance_extractor.py`
**Dependencies**: PyMuPDF (add to requirements)

---

## CONTEXT REFERENCES

### Relevant Codebase Files - READ BEFORE IMPLEMENTING

| File | Why Read It |
|------|-------------|
| `backend/app/services/annotation_replacer.py` | Core file to rewrite - understand current API contracts |
| `backend/app/services/pdf_parser.py` (lines 126-196) | Coordinate extraction logic to preserve |
| `backend/app/services/appearance_extractor.py` | Will be simplified/replaced for color extraction |
| `backend/app/models/annotation.py` | Data models that must remain compatible |
| `backend/tests/test_annotation_replacer.py` | Test patterns to follow, mocking strategy |
| `backend/scripts/test_batch_clone.py` | Reference for what successful conversion looks like |
| `backend/data/mapping.md` | Mapping format for subject lookup |

### New Files to Create

None - this is a refactor of existing services.

### Files to Modify

- `backend/pyproject.toml` - Add PyMuPDF dependency
- `backend/requirements.txt` - Add PyMuPDF dependency
- `backend/app/services/annotation_replacer.py` - Rewrite to use PyMuPDF
- `backend/app/services/pdf_parser.py` - Migrate to PyMuPDF (optional, can be phase 2)
- `backend/app/services/appearance_extractor.py` - Simplify to color extraction only
- `backend/tests/test_annotation_replacer.py` - Update for new implementation

### Relevant Documentation - READ BEFORE IMPLEMENTING

| Resource | Section | Why |
|----------|---------|-----|
| [PyMuPDF Annot Class](https://pymupdf.readthedocs.io/en/latest/annot.html) | All methods | Core API for annotation manipulation |
| [PyMuPDF Annotation Recipes](https://pymupdf.readthedocs.io/en/latest/recipes-annotations.html) | Creating annotations | Code examples for add_circle_annot, set_colors, update |
| [PyMuPDF Page Methods](https://pymupdf.readthedocs.io/en/latest/page.html) | annots(), delete_annot | Iteration and deletion patterns |
| [PyMuPDF Rect Class](https://pymupdf.readthedocs.io/en/latest/rect.html) | Constructor | Coordinate handling |

### Patterns to Follow

**Naming Conventions:**
```python
# snake_case for functions/variables
def replace_annotations(...)
deployment_subject = ...

# PascalCase for classes
class AnnotationReplacer:
```

**Service Pattern:**
```python
class ServiceName:
    def __init__(self, dependency1, dependency2):
        self.dependency1 = dependency1

    def public_method(self, ...) -> ReturnType:
        """Docstring with Args/Returns."""
        ...
```

**Logging Pattern:**
```python
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Converted: {bid_subject} -> {deployment_subject}")
logger.warning(f"No mapping found for: {subject}")
logger.error(f"Error converting annotation: {e}")
```

**Error Handling:**
```python
try:
    # operation
except Exception as e:
    logger.error(f"Context: {e}")
    # continue or raise based on severity
```

---

## IMPLEMENTATION PLAN

### Phase 1: Add PyMuPDF Dependency

Add PyMuPDF to the project dependencies. PyMuPDF is actively maintained and provides robust annotation handling with automatic appearance stream generation.

**Tasks:**
- Add `pymupdf>=1.24.0` to pyproject.toml and requirements.txt
- Verify installation with `uv sync`

### Phase 2: Create PyMuPDF Annotation Replacer

Rewrite `annotation_replacer.py` to use PyMuPDF for annotation creation. The key insight is that PyMuPDF's `annot.update()` automatically generates valid appearance streams.

**Tasks:**
- Import pymupdf instead of PyPDF2 generic objects
- Replace `create_deployment_annotation()` to return PyMuPDF annotation
- Replace `replace_annotations()` to work with PyMuPDF page objects
- Simplify appearance handling - just extract colors from reference PDF
- Ensure coordinate preservation via `pymupdf.Rect`

### Phase 3: Simplify Appearance Extractor

The `AppearanceExtractor` can be simplified since we no longer need to clone appearance streams. We only need to extract colors from reference annotations.

**Tasks:**
- Migrate to PyMuPDF for reading reference PDF
- Extract only color information (fill, stroke)
- Remove broken indirect object cloning logic

### Phase 4: Update Tests

Update tests to work with the new PyMuPDF implementation while preserving test coverage for coordinate preservation and mapping logic.

**Tasks:**
- Update mocks if needed
- Add integration test that verifies icons render
- Ensure all existing test cases still pass

### Phase 5: Create Validation Script

Create a simple script to verify the fix by converting a sample PDF and checking that annotations exist and have appearance streams.

---

## STEP-BY-STEP TASKS

### Task 1: UPDATE `backend/pyproject.toml`

- **IMPLEMENT**: Add PyMuPDF dependency
- **PATTERN**: Follow existing dependency format in pyproject.toml
- **GOTCHA**: PyMuPDF uses AGPL license - acceptable for internal tool
- **VALIDATE**: `cd backend && uv sync`

```toml
# Add to dependencies list:
"pymupdf>=1.24.0",
```

### Task 2: UPDATE `backend/requirements.txt`

- **IMPLEMENT**: Add PyMuPDF for pip compatibility
- **VALIDATE**: `pip install -r backend/requirements.txt` (optional)

```
# Add line:
pymupdf>=1.24.0
```

### Task 3: REFACTOR `backend/app/services/annotation_replacer.py`

- **IMPLEMENT**: Complete rewrite using PyMuPDF
- **PATTERN**: Keep same public API signature for `replace_annotations()`
- **IMPORTS**: `import pymupdf` (modern import style)
- **GOTCHA**: Must call `annot.update()` after setting properties
- **GOTCHA**: PyMuPDF uses RGB tuples (0-1 range) for colors
- **GOTCHA**: Cannot modify annotations during iteration - collect first, then process
- **VALIDATE**: `cd backend && python -c "from app.services.annotation_replacer import AnnotationReplacer"`

**Key changes:**
1. Remove PyPDF2 imports (`ArrayObject`, `DictionaryObject`, etc.)
2. Add `import pymupdf`
3. Change `create_deployment_annotation()` to create via `page.add_*_annot()`
4. Change `replace_annotations()` to:
   - Accept file paths instead of page objects
   - Open PDF with pymupdf
   - Iterate annotations, collect info, delete old, add new
   - Call `annot.update()` on each new annotation
   - Save output PDF
5. Simplify `_apply_appearance_data()` to just set colors
6. Remove `_apply_btx_properties()` complex logic - use simple color defaults

**New signature for replace_annotations:**
```python
def replace_annotations(
    self,
    input_pdf: Path,
    output_pdf: Path,
) -> tuple[int, int, list[str]]:
    """
    Replace bid annotations with deployment annotations.

    Args:
        input_pdf: Path to input PDF with bid annotations
        output_pdf: Path to save converted PDF

    Returns:
        Tuple of (converted_count, skipped_count, skipped_subjects)
    """
```

### Task 4: REFACTOR `backend/app/services/appearance_extractor.py`

- **IMPLEMENT**: Simplify to only extract colors from reference PDF
- **PATTERN**: Use PyMuPDF for PDF reading
- **IMPORTS**: `import pymupdf`
- **GOTCHA**: PyMuPDF returns colors as dict with 'fill' and 'stroke' keys
- **VALIDATE**: `cd backend && python -c "from app.services.appearance_extractor import AppearanceExtractor"`

**Key changes:**
1. Replace PyPDF2 PdfReader with pymupdf.open()
2. Store only color information per subject (not indirect object refs)
3. Return dict with `fill` and `stroke` color tuples

**New data structure:**
```python
self.appearances[subject] = {
    "fill": (r, g, b),    # tuple of floats 0-1
    "stroke": (r, g, b),  # tuple of floats 0-1
    "opacity": float,     # 0-1
}
```

### Task 5: UPDATE `backend/tests/test_annotation_replacer.py`

- **IMPLEMENT**: Update tests for new API
- **PATTERN**: Keep mock-based testing approach
- **GOTCHA**: New API takes file paths, not page objects
- **VALIDATE**: `cd backend && python -m pytest tests/test_annotation_replacer.py -v`

**Key changes:**
1. Update imports (remove PyPDF2 generic objects if not needed)
2. Update `replace_annotations` tests to use temp files
3. Add integration test that creates a real PDF and verifies output
4. Ensure coordinate preservation tests still work

### Task 6: CREATE validation script `backend/scripts/validate_fix.py`

- **IMPLEMENT**: Script to verify conversion produces visible annotations
- **PATTERN**: Similar to existing test scripts in scripts/
- **VALIDATE**: `cd backend && python scripts/validate_fix.py`

**Script should:**
1. Load BidMap.pdf
2. Convert using new AnnotationReplacer
3. Open output PDF with PyMuPDF
4. Verify annotations exist and have appearance streams
5. Print success/failure with stats

---

## TESTING STRATEGY

### Unit Tests

**Scope:** Test AnnotationReplacer logic in isolation with mocked dependencies

**Test Cases:**
- `test_replace_annotations_empty_list` - No annotations to process
- `test_replace_annotations_with_mapping` - Successful conversion
- `test_replace_annotations_missing_mapping` - Skips unmapped subjects
- `test_replace_annotations_preserves_coordinates` - Critical: coords match input
- `test_replace_annotations_sets_subject` - Subject field updated
- `test_create_annotation_with_colors` - Colors applied correctly

### Integration Tests

**Scope:** Test with real PDF files to verify rendering

**Test Cases:**
- `test_converted_pdf_has_visible_annotations` - Open output, verify annots render
- `test_conversion_with_sample_bidmap` - Full pipeline with BidMap.pdf
- `test_coordinate_preservation_visual` - Compare input/output positions

### Edge Cases

- Empty subject in annotation
- Annotation type not in {Circle, Square, Polygon}
- Missing mapping for subject
- PDF with no annotations
- PDF with annotations but no matching subjects

---

## VALIDATION COMMANDS

### Level 1: Syntax & Dependencies

```bash
cd backend && uv sync
cd backend && python -c "import pymupdf; print(f'PyMuPDF {pymupdf.version}')"
cd backend && python -c "from app.services.annotation_replacer import AnnotationReplacer"
```

### Level 2: Unit Tests

```bash
cd backend && python -m pytest tests/test_annotation_replacer.py -v
cd backend && python -m pytest tests/ -v  # All tests
```

### Level 3: Integration Tests

```bash
cd backend && python scripts/validate_fix.py
```

### Level 4: Manual Validation

1. Run conversion on sample PDF:
```bash
cd backend && python -c "
from pathlib import Path
from app.services.annotation_replacer import AnnotationReplacer
from app.services.mapping_parser import MappingParser
from app.services.btx_loader import BTXReferenceLoader
from app.services.appearance_extractor import AppearanceExtractor

# Setup
mapping = MappingParser(Path('data/mapping.md'))
mapping.load_mappings()
btx = BTXReferenceLoader()
btx.load_toolchest(Path('../toolchest/bidTools'), Path('../toolchest/deploymentTools'))
appear = AppearanceExtractor()
appear.load_from_pdf(Path('../samples/maps/DeploymentMap.pdf'))

# Convert
replacer = AnnotationReplacer(mapping, btx, appear)
converted, skipped, subjects = replacer.replace_annotations(
    Path('../samples/maps/BidMap.pdf'),
    Path('../samples/maps/BidMap_converted_pymupdf.pdf')
)
print(f'Converted: {converted}, Skipped: {skipped}')
"
```

2. Open `samples/maps/BidMap_converted_pymupdf.pdf` in a PDF viewer
3. Verify icons are VISIBLE (not invisible)
4. Verify icons are in correct positions (overlay with original if possible)

---

## ACCEPTANCE CRITERIA

- [ ] PyMuPDF dependency added and installable
- [ ] `replace_annotations()` produces PDF with VISIBLE annotations
- [ ] Converted annotations preserve exact coordinates (x, y, width, height)
- [ ] Converted annotations have correct deployment subject names
- [ ] Converted annotations have appropriate colors (from reference PDF or defaults)
- [ ] All existing unit tests pass or are updated appropriately
- [ ] Integration test verifies annotations render in output PDF
- [ ] No regressions in mapping lookup or BTX loading
- [ ] Code follows existing project patterns (logging, error handling)
- [ ] Manual test with BidMap.pdf produces visible deployment icons

---

## COMPLETION CHECKLIST

- [ ] Task 1: pyproject.toml updated with PyMuPDF
- [ ] Task 2: requirements.txt updated
- [ ] Task 3: annotation_replacer.py refactored to PyMuPDF
- [ ] Task 4: appearance_extractor.py simplified
- [ ] Task 5: Tests updated and passing
- [ ] Task 6: Validation script created and working
- [ ] All validation commands pass
- [ ] Manual PDF inspection confirms icons visible
- [ ] Code reviewed for quality

---

## NOTES

### Why PyMuPDF over PyPDF2?

1. **Automatic appearance streams**: `annot.update()` generates valid /AP
2. **No indirect object issues**: Creates self-contained annotations
3. **Better performance**: 12x faster than PyPDF2 in benchmarks
4. **Active maintenance**: PyPDF2 is deprecated (use pypdf)
5. **Native annotation methods**: `add_circle_annot()`, `add_rect_annot()`, etc.

### Licensing

PyMuPDF uses AGPL license. For this internal tool, this is acceptable. If the tool becomes commercial/closed-source, a commercial license from Artifex would be needed.

### Backwards Compatibility

The `replace_annotations()` API signature changes from accepting page objects to accepting file paths. This is acceptable because:
- The API is internal (not exposed to users)
- The routers (not yet implemented) will be updated to use the new signature
- Tests will be updated

### Fallback Colors

When no reference appearance is available, use sensible defaults:
- Fill color: Orange `(1.0, 0.5, 0.0)` - visible on most backgrounds
- Stroke color: Black `(0, 0, 0)` - standard border
- Border width: 0.5 - thin but visible

### Future Considerations

- Consider migrating `pdf_parser.py` to PyMuPDF for consistency (Phase 2)
- Consider removing PyPDF2 dependency entirely after full migration
- Add support for more annotation types (Polygon, Stamp) if needed
