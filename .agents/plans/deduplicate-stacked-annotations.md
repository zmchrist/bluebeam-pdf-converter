# Deduplicate Hidden/Stacked Annotations During Conversion

## Context
The source Bluebeam PDFs contain duplicate annotations stacked on top of each other — a main visible icon and a smaller hidden copy underneath with the same bid subject. During conversion, both get processed, each consuming a device ID. This makes IDs appear to skip by 2 (e.g., j100, j102 instead of j100, j101) since the hidden duplicate gets the intermediate ID.

## Root Cause
In `annotation_replacer.py` lines 337-385, every annotation with a valid mapping is added to `annotations_to_replace` without any deduplication. If two annotations share the same bid subject and overlap spatially, both get converted and assigned separate IDs.

## Solution: Same-Subject Deduplication by Rect Size
After collecting `annotations_to_replace`, group entries by `(deployment_subject, page_position)` and keep only the largest annotation per group. Two annotations are considered duplicates if they:
1. Map to the same `deployment_subject`
2. Have overlapping or nearby rects (center-to-center distance within the larger rect's dimensions)

For each group of duplicates, keep the one with the largest area (`width * height`). Discard the rest.

## File
`backend/app/services/annotation_replacer.py`

## Changes

### Add dedup step between collection and replacement (after line 391, before line 392)

Insert a deduplication pass over `annotations_to_replace`:

```python
# Deduplicate stacked annotations: keep only the largest per subject+position
annotations_to_replace = self._deduplicate_stacked(annotations_to_replace)
```

### Add `_deduplicate_stacked` method to `AnnotationReplacer`

```python
def _deduplicate_stacked(
    self,
    annotations: list[dict],
) -> list[dict]:
    """
    Remove hidden/stacked duplicate annotations.

    Bluebeam PDFs sometimes contain a smaller duplicate annotation
    underneath the main one with the same subject. Group annotations
    by deployment subject + spatial overlap and keep only the largest.
    """
    if not annotations:
        return annotations

    # Group by deployment_subject
    from collections import defaultdict
    groups: dict[str, list[dict]] = defaultdict(list)
    for annot in annotations:
        groups[annot["deployment_subject"]].append(annot)

    result = []
    for subject, group in groups.items():
        if len(group) <= 1:
            result.extend(group)
            continue

        # Sort by rect area descending (largest first)
        def rect_area(a):
            r = a["rect"]
            return (r[2] - r[0]) * (r[3] - r[1])

        group.sort(key=rect_area, reverse=True)

        kept: list[dict] = []
        for annot in group:
            r = annot["rect"]
            cx = (r[0] + r[2]) / 2
            cy = (r[1] + r[3]) / 2
            is_dup = False
            for existing in kept:
                er = existing["rect"]
                ecx = (er[0] + er[2]) / 2
                ecy = (er[1] + er[3]) / 2
                ew = er[2] - er[0]
                eh = er[3] - er[1]
                # If centers are within the larger rect's dimensions → duplicate
                if abs(cx - ecx) < ew and abs(cy - ecy) < eh:
                    is_dup = True
                    break
            if not is_dup:
                kept.append(annot)
            else:
                logger.debug(
                    f"Dedup: skipping stacked duplicate for {subject} "
                    f"(rect area {rect_area(annot):.1f} vs {rect_area(kept[0]):.1f})"
                )
        result.extend(kept)

    return result
```

**Logic:**
- Groups all annotations by their `deployment_subject`
- For subjects with multiple annotations, sorts largest-first
- For each annotation, checks if its center falls within an already-kept annotation's rect
- If so, it's a stacked duplicate → skip it
- Otherwise, it's a genuinely separate icon at a different location → keep it

This preserves multiple icons of the same type at different locations (e.g., 20 access points across the map) while removing hidden duplicates stacked at the same position.

## Verification
1. `cd backend && uv run pytest` — expect same known failures only
2. Run conversion on a sample PDF and check that IDs increment by 1 (no skips):
   ```bash
   cd backend && uv run python scripts/test_conversion.py
   ```
3. Verify the converted PDF has the correct number of annotations (no hidden duplicates underneath the main icons)
