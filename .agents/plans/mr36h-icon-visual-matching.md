# Visual Appearance Matching Implementation Plan

## Objective

Make converted deployment icons look **exactly** like the reference icons in `samples/icons/deploymentIcons/accessPoints.pdf`.

**CRITICAL:** This is an iterative process. We focus on ONE icon (MR36H) until it's PERFECT, then apply the pattern to other icons.

---

## Target: MR36H Icon

### Reference Analysis (from accessPoints.pdf)

The MR36H icon (labeled "j100" in reference) consists of:

```
┌─────────────────────────────────┐
│          j100                   │  ← Top label (blue text, white box, border)
├─────────────────────────────────┤
│          ┌─────────┐            │
│          │ CISCO   │            │  ← White text, inside blue circle
│          │ ┌─────┐ │            │
│          │ │     │ │            │  ← Product image (black Cisco MR36H device)
│          │ │ ◯◯◯ │ │            │
│          │ └─────┘ │            │
│          │  MR36H  │            │  ← White text, inside blue circle
│          └─────────┘            │
│   (blue filled circle, ~navy)   │
├─────────────────────────────────┤
│         xx' xx°                 │  ← Bottom label (blue text, white box, border)
└─────────────────────────────────┘
```

### Visual Specifications

| Element | Specification |
|---------|--------------|
| **Circle Fill** | Navy blue RGB: (0.22, 0.34, 0.65) or similar |
| **Circle Border** | Thin dark outline (~0.5pt) |
| **"CISCO" Text** | White, bold, ~2pt font, top of circle interior |
| **Product Image** | `samples/icons/gearIcons/APs/AP - Cisco MR36H.png` |
| **"MR36H" Text** | White, bold, ~1.8pt font, bottom of circle interior |
| **Top Label** | Blue text on white background with border, "j100" format |
| **Bottom Label** | Blue text on white background with border, "xx' xx°" format |

### Bid → Deployment Mapping

```
Bid Subject: "Artist - Indoor Wi-Fi Access Point"
    ↓
Deployment Subject: "AP - Cisco MR36H"
```

---

## Implementation Approach

### Phase 1: Single Icon Test Script

Create `backend/scripts/test_mr36h_icon.py` that:

1. Opens `samples/maps/BidMap.pdf`
2. Finds ONE "Artist - Indoor Wi-Fi Access Point" annotation
3. Creates a deployment annotation with:
   - Blue filled circle
   - Embedded product image (MR36H.png)
   - "CISCO" text at top
   - "MR36H" text at bottom
4. Saves to `samples/maps/test_mr36h_output.pdf`
5. Visual comparison with `samples/icons/deploymentIcons/accessPoints.pdf`

### Phase 2: Iterate Until Perfect

**Iteration Loop:**
1. Run test script → generate output PDF
2. Open output PDF and compare visually to reference
3. Identify differences (color, positioning, font size, image scale)
4. Adjust parameters and re-run
5. Repeat until visually identical

**Key Parameters to Tune:**
- Circle fill color RGB values
- Image scale and positioning within circle
- Text font sizes and positions
- Border width and color

### Phase 3: Integrate into AnnotationReplacer

Once MR36H is perfect:
1. Extract the appearance-building logic into `appearance_extractor.py` or new `icon_renderer.py`
2. Update `annotation_replacer.py` to use the new renderer
3. Test full conversion with all MR36H icons in BidMap.pdf

### Phase 4: Extend to Other Icons

Apply the same pattern to:
- Other access points (MR78, 9166I, 9166D, 9120, MARLIN 4, DB10)
- Switches
- Other equipment

---

## Critical Files

### To Modify
| File | Changes |
|------|---------|
| `backend/scripts/test_mr36h_icon.py` | NEW - Focused test script for MR36H |
| `backend/app/services/annotation_replacer.py` | Update to use rich appearance streams |
| `backend/app/services/appearance_extractor.py` | Add appearance building (not just extraction) |

### Reference Files (Read-Only)
| File | Purpose |
|------|---------|
| `samples/icons/deploymentIcons/accessPoints.pdf` | Visual reference for MR36H (j100 icon) |
| `samples/maps/BidMap.pdf` | Input PDF with bid icons |
| `samples/icons/gearIcons/APs/AP - Cisco MR36H.png` | Product image to embed |

### Gear Icons Location
**IMPORTANT:** Use gear icons from `samples/icons/gearIcons/`, NOT from `toolchest/gearIcons/`.

Available AP icons in `samples/icons/gearIcons/APs/`:
- `AP - Cisco MR36H.png` ← **TARGET FOR THIS TASK**
- `AP - Cisco 9120.png`
- `AP - Cisco 9124.png`
- `AP - Cisco 9166.png`
- `AP - Cisco MR78.png`
- `AP - Cisco Marlin 4.png`
- `AP - DB10.png`

---

## Technical Implementation

### Using PyMuPDF (fitz) for Rich Appearances

PyMuPDF can create annotations with custom appearance streams:

```python
import pymupdf

# Create annotation
annot = page.add_circle_annot(rect)

# Build custom appearance
shape = page.new_shape()

# Draw filled circle
shape.draw_circle(center, radius)
shape.finish(color=(0, 0, 0), fill=(0.22, 0.34, 0.65), width=0.5)

# Insert image
page.insert_image(img_rect, filename=image_path)

# Add text
shape.insert_text(point, "CISCO", fontsize=2.2, color=(1, 1, 1))
shape.insert_text(point, "MR36H", fontsize=1.8, color=(1, 1, 1))

shape.commit()
annot.update()
```

### Alternative: Direct Appearance Stream Construction

If PyMuPDF shape building is insufficient, construct PDF appearance streams directly:

```python
# Appearance stream content (PDF drawing commands)
content = """
{r} {g} {b} rg  % Set fill color
0 0 0 RG        % Set stroke color
{x} {y} m       % Move to start
...bezier curves for circle...
B               % Fill and stroke

q               % Save state
{w} 0 0 {h} {x} {y} cm  % Transform for image
/Img Do         % Draw image
Q               % Restore state

BT              % Begin text
1 1 1 rg        % White text
/Helv 2.2 Tf    % Font
{x} {y} Td (CISCO) Tj
ET              % End text
"""
```

---

## Verification Steps

### After Each Iteration

1. **Visual Check:** Open output PDF and compare side-by-side with reference
2. **Color Match:** Verify circle fill matches reference blue
3. **Image Quality:** Ensure product image is sharp and properly scaled
4. **Text Clarity:** Check "CISCO" and "MR36H" are readable and positioned correctly
5. **Circle Shape:** Confirm perfect circle (not oval or irregular)

### Final Verification

1. Open `test_mr36h_output.pdf` in Bluebeam Revu
2. Place side-by-side with `accessPoints.pdf`
3. Icons should be visually indistinguishable
4. Verify annotation properties (subject name, type) are correct

---

## Iteration Workflow

```
┌──────────────────────────────────────────────────────────────────┐
│  START: Run test_mr36h_icon.py                                   │
└──────────────────────────────┬───────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────────┐
│  EVALUATE: Open output PDF, compare to reference                 │
│  - Does circle color match?                                      │
│  - Is image centered and scaled correctly?                       │
│  - Are texts positioned and sized correctly?                     │
└──────────────────────────────┬───────────────────────────────────┘
                               ↓
              ┌────────────────┴────────────────┐
              │                                 │
        Looks Good?                       Differences Found
              │                                 │
              ↓                                 ↓
┌─────────────────────────┐    ┌─────────────────────────────────────┐
│  OFFER SAMPLE TO USER   │    │  ADJUST: Modify parameters          │
│  for visual review      │    │  - Color values                     │
│                         │    │  - Position offsets                 │
└─────────────────────────┘    │  - Font sizes                       │
                               │  - Image scale                      │
                               └──────────────┬──────────────────────┘
                                              │
                                              ↓
                               ┌──────────────────────────────────────┐
                               │  RE-RUN: Generate new output         │
                               └──────────────────────────────────────┘
                                              │
                                              └───────→ (back to EVALUATE)
```

---

## Context Preservation (If Running Low)

If context runs low during iteration:

1. Run `/memorize` with current progress:
   - Current parameter values that work
   - What still needs adjustment
   - Which iteration we're on
2. Run `/clear`
3. Resume with: "Continue MR36H icon visual matching from memory"

---

## Success Criteria

**MR36H icon is "perfect" when:**

- [ ] Circle fill color matches reference exactly
- [ ] Product image is sharp, centered, and properly scaled
- [ ] "CISCO" text is white, positioned at top of circle interior
- [ ] "MR36H" text is white, positioned at bottom of circle interior
- [ ] Circle border is thin and dark
- [ ] Annotation subject is "AP - Cisco MR36H"
- [ ] User confirms visual match to reference

---

## Next Steps After MR36H

Once MR36H is perfect:
1. Create similar test scripts for other AP models
2. Abstract the icon rendering into a reusable service
3. Update annotation_replacer.py to use the new renderer
4. Full conversion test on BidMap.pdf
5. Move to API implementation (Phase 4)
