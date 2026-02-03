# Error Knowledge Base

Known errors and their solutions. Check this file before debugging unfamiliar errors.

---

## PyMuPDF / PDF Processing

### "cannot open broken document"
- **Error:** `fitz.fitz.FileDataError: cannot open broken document`
- **Cause:** Corrupted PDF, invalid file path, or file doesn't exist
- **Solution:** Validate file exists and is readable before opening with `fitz.open()`
- **Files:** `pdf_parser.py`, `annotation_replacer.py`
- **Date Found:** 2026-02-01

### "Annot not bound to page"
- **Error:** `RuntimeError: annot not bound to page`
- **Cause:** Deleting annotations while iterating with `for annot in page.annots()`
- **Solution:** Use xref-based deletion: collect xrefs first, then delete by xref after iteration
- **Files:** `annotation_replacer.py:85`
- **Date Found:** 2026-02-01
```python
# Wrong - causes "not bound to page"
for annot in page.annots():
    page.delete_annot(annot)

# Correct - use xref
xrefs_to_delete = [annot.xref for annot in page.annots() if should_delete(annot)]
for xref in xrefs_to_delete:
    page.delete_annot(page.annot_xrefs().index(xref))
```

### Invisible annotations after conversion
- **Error:** No visual error, but icons don't render in output PDF
- **Cause:** PyPDF2 cannot properly clone appearance streams (`/AP`) - indirect object references become invalid
- **Solution:** Use PyMuPDF instead. `annot.update()` automatically generates valid appearance streams
- **Files:** `annotation_replacer.py`
- **Date Found:** 2026-01-30

---

## Configuration / Paths

### "mapping.md not found"
- **Error:** `FileNotFoundError: mapping.md not found` or similar
- **Cause:** Using relative paths in config.py when running from different directories
- **Solution:** Use absolute paths via `Path(__file__).resolve().parent`
- **Files:** `config.py:15`
- **Date Found:** 2026-02-02
```python
# Wrong
MAPPING_FILE = Path("backend/data/mapping.md")

# Correct
BACKEND_DIR = Path(__file__).resolve().parent.parent
MAPPING_FILE = BACKEND_DIR / "data" / "mapping.md"
```

---

## BTX Parsing

### XML parsing fails on BTX files
- **Error:** `lxml.etree.XMLSyntaxError` on valid-looking BTX files
- **Cause:** UTF-8 BOM (`\xef\xbb\xbf`) at start of file
- **Solution:** Strip BOM before parsing: `content.lstrip('\xef\xbb\xbf')`
- **Files:** `btx_loader.py:42`
- **Date Found:** 2026-01-30

### BTX `<Name>` element has wrong subject
- **Error:** Subject names don't match between BTX and PDF
- **Cause:** `<Name>` is an internal ID, not the display subject
- **Solution:** Extract subject from decoded `<Raw>` field: look for `/Subj(Subject Name)`
- **Files:** `btx_loader.py:78`
- **Date Found:** 2026-01-30

---

## Pydantic / Data Models

### Accessing nested attribute that doesn't exist
- **Error:** `AttributeError: 'dict' object has no attribute 'mappings'`
- **Cause:** Assuming nested structure when service returns flat dict
- **Solution:** Check actual return type - `mapping_parser.mappings` is already a dict, not `mapping_parser.mappings.mappings`
- **Files:** `convert.py:35`
- **Date Found:** 2026-02-02

---

## asyncio

### "Event loop is closed"
- **Error:** `RuntimeError: Event loop is closed`
- **Cause:** Using `asyncio.get_event_loop()` after loop shutdown
- **Solution:** Use `asyncio.get_running_loop()` or `asyncio.new_event_loop()`
- **Files:** Various async contexts
- **Date Found:** N/A (preventive)

---

## Testing

### pytest can't find modules
- **Error:** `ModuleNotFoundError: No module named 'app'`
- **Cause:** Running pytest from wrong directory or missing `__init__.py`
- **Solution:** Run from `backend/` directory: `cd backend && uv run pytest`
- **Files:** All test files
- **Date Found:** N/A (common)

---

## Template for New Errors

When adding new errors, use this format:

```markdown
### [Short descriptive title]
- **Error:** [Exact error message or description]
- **Cause:** [Root cause, not just symptoms]
- **Solution:** [What fixed it]
- **Files:** [Affected files with line numbers if relevant]
- **Date Found:** [YYYY-MM-DD]
```

If there's a code fix, include a before/after example:
```python
# Wrong
[problematic code]

# Correct
[fixed code]
```
