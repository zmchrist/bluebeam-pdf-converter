# Fix Duplicate Icon Bug in PDF Conversion

## Context

When opening a converted PDF in Bluebeam and moving a deployment icon, the user sees duplicates behind it:
1. A **smaller duplicate with a new ID** — a second deployment annotation created from a `/Popup` annotation
2. A **same-size duplicate** — native circle rendering from `/IC`/`/C`/`/BS` properties alongside the `/AP` appearance stream

## Root Causes

### 1. No annotation subtype filtering
The code only skips `/Line` subtypes. Bluebeam PDFs pair `/Circle` annotations with `/Popup` annotations that share the same `/Subj`. Both get converted into deployment icons — producing two annotations per bid icon. The popup has a different (smaller) rect, explaining the "smaller duplicate with a new ID."

### 2. Native rendering properties alongside `/AP`
`_create_deployment_annotation_dict` always sets `/IC`, `/C`, `/BS` even when a rich `/AP` appearance stream is present. Bluebeam renders both the custom appearance AND the native circle fill, producing a same-size ghost.

### 3. Stale legend indices (secondary bug)
The replacement pass uses `del annots[idx]` + `append`, shifting array positions. The legend deletion pass then uses stale pre-shift indices, potentially deleting wrong annotations.

## Solution: Single-Pass Array Rebuild

Replace the current multi-pass approach with a single iteration that builds a fresh `ArrayObject`.

### File: `backend/app/services/annotation_replacer.py`

#### Change 1: Add `has_rich_appearance` parameter to `_create_deployment_annotation_dict`

When `True`, **omit** `/IC`, `/C`, `/BS` from the annotation dict. These cause Bluebeam to render a native circle underneath the `/AP` appearance stream.

```python
def _create_deployment_annotation_dict(
    self, rect, deployment_subject, appearance_ref,
    fill_color, stroke_color, annotation_type="/Circle",
    has_rich_appearance=False,  # NEW
) -> DictionaryObject:
    ...
    if not has_rich_appearance:
        # Only set native colors when no rich /AP — prevents ghost rendering
        annot[NameObject("/IC")] = ArrayObject([...])
        annot[NameObject("/C")] = ArrayObject([...])
        bs = DictionaryObject()
        bs[NameObject("/W")] = FloatObject(DEFAULT_BORDER_WIDTH)
        bs[NameObject("/S")] = NameObject("/S")
        annot[NameObject("/BS")] = bs
```

#### Change 2: Rewrite `replace_annotations` — single-pass with subtype whitelist

- Define `CONVERTIBLE_SUBTYPES = {"/Circle", "/Square"}` — only these represent bid icons
- Single loop: for each annotation, decide to **skip** (legend), **convert** (convertible subtype + valid mapping), or **preserve as-is** (everything else)
- Build `new_annots = ArrayObject()` and assign to `page[NameObject("/Annots")]`
- No `del`/`append` — eliminates all index management issues
- Legends excluded by simply not appending to `new_annots`
- Pass `has_rich_appearance=True` when rich rendering succeeds

## Verification

1. `cd backend && uv run pytest` — expect same 170 passed, 6 failed (known), 11 skipped
2. `cd backend && uv run python scripts/test_conversion.py` — verify annotation counts match (~376 converted)
3. Open converted PDF in Bluebeam, move icons — confirm no duplicates
4. Confirm legends/gear lists still removed from output
