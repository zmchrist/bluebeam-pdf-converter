# Feature: Clone Deployment Icons from Reference PDF

The following plan should be complete, but validate documentation and codebase patterns before implementing.

Pay special attention to coordinate transformation - all PDF coordinates are absolute page space.

## Feature Description

Convert bid icons to deployment icons by **cloning complete annotations** from DeploymentMap.pdf (which has Bluebeam's perfect rendering) rather than generating appearance streams from scratch. This leverages Bluebeam's native icon rendering by copying self-contained vector graphics and transforming coordinates to the target position.

## User Story

As a project estimator
I want bid icon markups automatically converted to deployment icons with perfect visual fidelity
So that converted maps look identical to icons placed manually in Bluebeam

## Problem Statement

Previous attempts to generate deployment icon appearance streams programmatically resulted in imperfect rendering (squares instead of circles, missing graphics). The deployment icons in Bluebeam's toolchest are complex (6-child annotation groups), but DeploymentMap.pdf already contains perfectly-rendered deployment annotations that are self-contained vector graphics.

## Solution Statement

Clone complete annotation objects from DeploymentMap.pdf (which contains all deployment icon types rendered by Bluebeam) and transform their coordinates to match bid icon positions. The appearance streams are self-contained (~40-300 bytes of PDF operators) with no external dependencies, making them perfectly portable.

## Feature Metadata

**Feature Type**: Enhancement (improving icon conversion visual quality)
**Estimated Complexity**: Medium
**Primary Systems Affected**: Annotation replacement pipeline
**Dependencies**: PyPDF2, DeploymentMap.pdf reference file

---

## CONTEXT REFERENCES

### Relevant Codebase Files - READ BEFORE IMPLEMENTING

- `backend/app/services/annotation_replacer.py` - Current replacement logic, will need updating
- `backend/app/services/appearance_extractor.py` - Existing appearance extraction (reference only)
- `backend/scripts/test_single_icon.py` - Previous test script approach (shows what NOT to do)
- `samples/maps/DeploymentMap.pdf` - Source of template annotations to clone
- `samples/maps/BidMap.pdf` - Target PDF with bid icons to convert

### New Files to Create

- `backend/scripts/test_clone_icon.py` - Test script for single icon cloning
- `backend/app/services/annotation_cloner.py` - Reusable cloning service (future)

### Key Discovery: DeploymentMap.pdf Annotation Structure

From exploration, each deployment annotation has:
```
/Type:      /Annot
/Subtype:   /Circle (or /Square)
/Subj:      "AP - Cisco MR36H"
/Rect:      [5054.46, 5883.09, 5077.369, 5906.007]  # Absolute page coords
/IC:        [0.2196078, 0.3411765, 0.6470588]       # Blue fill
/C:         [0, 0, 0]                                # Black border
/AP:        {/N: FormXObject}                        # Appearance stream
```

The `/AP/N` Form XObject contains:
```
/Type:      /XObject
/Subtype:   /Form
/BBox:      [5054.46, 5883.09, 5077.369, 5906.007]  # Matches /Rect
/Matrix:    [1, 0, 0, 1, -5054.46, -5883.09]        # Origin offset
/Resources: {/ProcSet [/PDF]}                        # Self-contained!
[Stream]:   PDF vector drawing operators (absolute coords)
```

**Critical**: Appearance streams have NO external dependencies - just `/ProcSet [/PDF]`.

### Patterns to Follow

**Coordinate Transformation:**
```python
# To move annotation from template position to target position:
delta_x = target_rect[0] - template_rect[0]
delta_y = target_rect[1] - template_rect[1]

# Update /Rect
new_rect = [r + delta for r, delta in zip(template_rect, [delta_x, delta_y, delta_x, delta_y])]

# Update /BBox in appearance
new_bbox = new_rect  # Same as /Rect

# Update /Matrix
new_matrix = [1, 0, 0, 1, -new_rect[0], -new_rect[1]]

# Update stream coordinates (regex replace numeric values)
```

**Stream Content Example (299 bytes):**
```
0 0 0 RG                                    # Stroke black
0.5968134 w                                 # Line width
0.2196078 0.3411765 0.6470588 rg           # Fill blue
5065.915 5883.687 m                         # Move to (absolute coords!)
5071.911 5883.687 5076.772 5888.549 5076.772 5894.548 c
...
h B                                         # Close & fill/stroke
```

---

## IMPLEMENTATION PLAN

### Phase 1: Template Extraction

Extract one deployment annotation template from DeploymentMap.pdf for testing.

**Tasks:**
- Load DeploymentMap.pdf with PyPDF2
- Find annotation with subject "AP - Cisco 9120" (or similar)
- Extract complete annotation dictionary including /AP appearance stream
- Verify appearance stream is self-contained

### Phase 2: Coordinate Transformation

Implement coordinate transformation to move template to target position.

**Tasks:**
- Calculate delta (offset) from template position to target position
- Update /Rect field with new coordinates
- Update /BBox in appearance Form XObject
- Update /Matrix to reflect new origin offset
- Transform all numeric coordinates in stream content

### Phase 3: Clone & Insert

Clone the transformed annotation into target PDF.

**Tasks:**
- Deep copy annotation dictionary
- Update /Subj to deployment subject
- Generate new /NM (unique name)
- Update timestamps
- Remove bid annotation from target page
- Insert cloned annotation at same position
- Save modified PDF

### Phase 4: Verification

Verify the cloned icon renders correctly.

**Tasks:**
- Open output PDF in viewer
- Compare to original deployment icon in DeploymentMap.pdf
- Verify position matches original bid icon
- Test opening in Bluebeam (if available)

---

## STEP-BY-STEP TASKS

### Task 1: CREATE `backend/scripts/test_clone_icon.py`

**IMPLEMENT**: Test script skeleton with imports and paths
```python
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import (
    ArrayObject, DictionaryObject, FloatObject,
    NameObject, StreamObject, TextStringObject
)
import copy
import re

PROJECT_ROOT = Path(__file__).parent.parent.parent
DEPLOYMENT_PDF = PROJECT_ROOT / "samples" / "maps" / "DeploymentMap.pdf"
BID_PDF = PROJECT_ROOT / "samples" / "maps" / "BidMap.pdf"
OUTPUT_PDF = PROJECT_ROOT / "samples" / "maps" / "test_clone_output.pdf"

BID_SUBJECT = "Artist - Indoor Wi-Fi Access Point"
DEPLOYMENT_SUBJECT = "AP - Cisco 9120"
```
**VALIDATE**: `python -c "from pathlib import Path; print(Path('backend/scripts/test_clone_icon.py').exists())"`

### Task 2: IMPLEMENT Template Extraction Function

**IMPLEMENT**: Function to find and extract template annotation from DeploymentMap.pdf
```python
def find_template_annotation(pdf_path: Path, subject: str) -> tuple[dict, dict]:
    """
    Find annotation with given subject and extract it with appearance stream.

    Returns:
        Tuple of (annotation_dict, appearance_stream_dict)
    """
    reader = PdfReader(str(pdf_path))
    page = reader.pages[0]
    annots = page.get('/Annots')

    for annot_ref in annots:
        annot = annot_ref.get_object()
        subj = str(annot.get('/Subj', ''))
        if subj == subject:
            # Get appearance stream
            ap = annot.get('/AP')
            ap_n = ap['/N'].get_object() if ap else None
            return annot, ap_n

    return None, None
```
**GOTCHA**: Some annotations may not have the exact subject - search flexibly
**VALIDATE**: Run script and verify template is found

### Task 3: IMPLEMENT Coordinate Transformation Function

**IMPLEMENT**: Function to transform all coordinates in annotation
```python
def transform_coordinates(
    template_annot: dict,
    template_ap: dict,
    target_rect: list[float]
) -> tuple[DictionaryObject, StreamObject]:
    """
    Transform template annotation coordinates to target position.

    Returns:
        Tuple of (new_annotation, new_appearance_stream)
    """
    # Get template rect
    template_rect = [float(r) for r in template_annot['/Rect']]

    # Calculate delta
    delta_x = target_rect[0] - template_rect[0]
    delta_y = target_rect[1] - template_rect[1]

    # Transform stream content
    stream_data = template_ap.get_data().decode('latin-1')
    transformed_stream = transform_stream_coordinates(stream_data, delta_x, delta_y)

    # Build new annotation...
```
**PATTERN**: Use regex to find and replace numeric coordinates in stream
**GOTCHA**: Preserve non-coordinate numbers (colors, line widths)

### Task 4: IMPLEMENT Stream Coordinate Transformation

**IMPLEMENT**: Regex-based coordinate transformation for PDF stream content
```python
def transform_stream_coordinates(stream: str, delta_x: float, delta_y: float) -> bytes:
    """
    Transform absolute coordinates in PDF stream content.

    PDF operators that use coordinates:
    - 'm' (moveto): x y m
    - 'l' (lineto): x y l
    - 'c' (curveto): x1 y1 x2 y2 x3 y3 c
    - 're' (rectangle): x y w h re

    Numbers for colors (rg, RG) and line width (w) should NOT be transformed.
    """
    lines = stream.split('\n')
    transformed = []

    for line in lines:
        # Skip color and width commands
        if line.strip().endswith(('rg', 'RG', 'w', 'd')):
            transformed.append(line)
            continue

        # Transform coordinate commands
        if line.strip().endswith(('m', 'l', 'c', 're', 'h', 'B', 'S')):
            # Parse and transform coordinates
            transformed.append(transform_line_coords(line, delta_x, delta_y))
        else:
            transformed.append(line)

    return '\n'.join(transformed).encode('latin-1')
```
**GOTCHA**: The 're' operator is `x y width height re` - only transform x,y not width,height

### Task 5: IMPLEMENT Clone and Insert Function

**IMPLEMENT**: Main function to clone template to target position
```python
def clone_annotation_to_position(
    writer: PdfWriter,
    page_idx: int,
    template_annot: dict,
    template_ap: dict,
    target_rect: list[float],
    new_subject: str
) -> None:
    """
    Clone template annotation to new position on page.
    """
    # Transform coordinates
    new_annot, new_ap = transform_coordinates(template_annot, template_ap, target_rect)

    # Update subject
    new_annot[NameObject('/Subj')] = TextStringObject(new_subject)

    # Generate unique name
    import uuid
    new_annot[NameObject('/NM')] = TextStringObject(str(uuid.uuid4())[:16].upper())

    # Create appearance dictionary
    ap_ref = writer._add_object(new_ap)
    ap_dict = DictionaryObject()
    ap_dict[NameObject('/N')] = ap_ref
    new_annot[NameObject('/AP')] = ap_dict

    # Add to page
    page = writer.pages[page_idx]
    if '/Annots' not in page:
        page[NameObject('/Annots')] = ArrayObject()
    page['/Annots'].append(new_annot)
```

### Task 6: IMPLEMENT Main Test Function

**IMPLEMENT**: Main function that ties everything together
```python
def main():
    print("=" * 60)
    print("Clone Icon Test")
    print("=" * 60)

    # 1. Load template from DeploymentMap.pdf
    print(f"\nLoading template: {DEPLOYMENT_SUBJECT}")
    template_annot, template_ap = find_template_annotation(DEPLOYMENT_PDF, DEPLOYMENT_SUBJECT)
    if not template_annot:
        # Try partial match
        template_annot, template_ap = find_template_annotation_partial(DEPLOYMENT_PDF, "Cisco 9120")

    print(f"  Template rect: {template_annot['/Rect']}")
    print(f"  AP stream size: {len(template_ap.get_data())} bytes")

    # 2. Load BidMap.pdf and find target annotation
    print(f"\nLoading bid PDF and finding: {BID_SUBJECT}")
    bid_reader = PdfReader(str(BID_PDF))
    writer = PdfWriter()
    for page in bid_reader.pages:
        writer.add_page(page)

    # Find bid annotation
    page = writer.pages[0]
    annots = page['/Annots']
    target_rect = None
    target_idx = None

    for idx, annot_ref in enumerate(annots):
        annot = annot_ref.get_object()
        if str(annot.get('/Subj', '')) == BID_SUBJECT:
            target_rect = [float(r) for r in annot['/Rect']]
            target_idx = idx
            break

    print(f"  Target rect: {target_rect}")

    # 3. Remove bid annotation
    del annots[target_idx]

    # 4. Clone deployment annotation to target position
    print(f"\nCloning to position...")
    clone_annotation_to_position(
        writer, 0, template_annot, template_ap,
        target_rect, DEPLOYMENT_SUBJECT
    )

    # 5. Save
    print(f"\nSaving to: {OUTPUT_PDF}")
    with open(OUTPUT_PDF, 'wb') as f:
        writer.write(f)

    print("\nSUCCESS! Open PDF to verify.")

if __name__ == "__main__":
    main()
```
**VALIDATE**: `cd backend && python scripts/test_clone_icon.py`

---

## TESTING STRATEGY

### Manual Visual Test
1. Run `python scripts/test_clone_icon.py`
2. Open `samples/maps/test_clone_output.pdf`
3. Navigate to the cloned icon location
4. Compare visually to:
   - Surrounding bid icons (should be same size/position)
   - DeploymentMap.pdf original (should look identical)

### Automated Verification
```python
# Verify cloned annotation exists with correct subject
reader = PdfReader('samples/maps/test_clone_output.pdf')
page = reader.pages[0]
found = False
for annot_ref in page['/Annots']:
    annot = annot_ref.get_object()
    if str(annot.get('/Subj', '')) == 'AP - Cisco 9120':
        found = True
        assert '/AP' in annot, "Missing appearance stream"
        assert annot['/AP']['/N'] is not None, "Missing /N appearance"
        break
assert found, "Cloned annotation not found"
```

---

## VALIDATION COMMANDS

### Level 1: Script Runs Without Error
```bash
cd backend && python scripts/test_clone_icon.py
```
Expected: "SUCCESS!" message, output PDF created

### Level 2: Output PDF Valid
```bash
cd backend && python -c "from PyPDF2 import PdfReader; r = PdfReader('../samples/maps/test_clone_output.pdf'); print(f'Pages: {len(r.pages)}, Valid: True')"
```
Expected: "Pages: 1, Valid: True"

### Level 3: Cloned Annotation Exists
```bash
cd backend && python -c "
from PyPDF2 import PdfReader
r = PdfReader('../samples/maps/test_clone_output.pdf')
found = any(str(a.get_object().get('/Subj',''))=='AP - Cisco 9120' for a in r.pages[0]['/Annots'])
print(f'Deployment icon found: {found}')
"
```
Expected: "Deployment icon found: True"

### Level 4: Visual Verification
Open `samples/maps/test_clone_output.pdf` in PDF viewer or Bluebeam and verify:
- [ ] Icon renders as blue circle (not square)
- [ ] Position matches original bid icon location
- [ ] Size matches surrounding icons
- [ ] "CISCO" and model text visible (if present in template)

---

## ACCEPTANCE CRITERIA

- [ ] Test script runs without errors
- [ ] Output PDF opens without corruption
- [ ] Cloned annotation has correct subject "AP - Cisco 9120"
- [ ] Cloned annotation has /AP appearance stream
- [ ] Icon renders visually identical to DeploymentMap.pdf source
- [ ] Icon position matches original bid icon position
- [ ] Icon size matches original bid icon size

---

## COMPLETION CHECKLIST

- [ ] Template extraction working
- [ ] Coordinate transformation working
- [ ] Stream content transformation working
- [ ] Clone and insert working
- [ ] Visual verification passed
- [ ] Ready to scale to all icons

---

## NOTES

### Why Clone vs Generate?
- DeploymentMap.pdf icons are rendered by Bluebeam = perfect quality
- Appearance streams are self-contained vector graphics
- No need to understand complex BTX group structure
- Much simpler code (clone + transform vs generate from scratch)

### Potential Issues
1. **Different icon sizes**: Template may be different size than target. May need to scale.
2. **Missing templates**: Not all deployment subjects may exist in DeploymentMap.pdf
3. **Complex annotations**: Some may have linked text labels (/IRT references)

### Future Enhancements
1. Build complete template dictionary for all deployment subjects
2. Handle icon scaling if sizes differ
3. Clone linked text labels alongside icons
4. Integrate into main annotation_replacer.py service
