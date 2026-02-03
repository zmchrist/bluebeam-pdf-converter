# Feature: Expand Icon Coverage

The following plan should be complete, but it's important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils, types, and models. Import from the right files, etc.

## Feature Description

Expand the icon configuration system from **39 currently configured icons** to cover **79 additional deployment icons** that have corresponding gear images available. This will significantly improve the visual quality of PDF conversions by ensuring more icons render with proper gear images, brand text, and model labels instead of falling back to simple colored shapes.

## User Story

As a **project estimator**,
I want **all deployment icons to render with their proper visual appearance (gear images, brand text, model labels)**,
So that **converted PDF maps accurately represent the specific equipment being deployed, not generic placeholders**.

## Problem Statement

Currently, only 39 of 118 deployment icon subjects are configured in `icon_config.py`. When the annotation replacer encounters an unconfigured icon, it falls back to rendering a simple colored circle without a gear image. This means:
- 79 deployment icons render as generic shapes instead of proper equipment images
- Users see inconsistent visual quality across different icon types
- The 93.5% conversion success rate could improve with fuller icon coverage

## Solution Statement

Add configurations for all deployment icons that have corresponding gear images in `samples/icons/gearIcons/`. This involves:
1. Adding entries to `ICON_CATEGORIES` mapping subjects to rendering categories
2. Adding entries to `ICON_IMAGE_PATHS` mapping subjects to PNG file paths
3. Adding `ICON_OVERRIDES` for icons that need custom brand text or positioning
4. Updating `get_model_text()` to handle new brand name patterns
5. Adding unit tests for new configurations

## Feature Metadata

**Feature Type**: Enhancement
**Estimated Complexity**: Medium (configuration additions, minimal code changes)
**Primary Systems Affected**: `icon_config.py`, `test_icon_renderer.py`
**Dependencies**: Existing gear PNG images in `samples/icons/gearIcons/`

---

## CONTEXT REFERENCES

### Relevant Codebase Files - IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

- `backend/app/services/icon_config.py` (lines 1-420) - **CRITICAL**: Main file to modify. Contains all four dictionaries that need expansion.
- `backend/app/services/icon_renderer.py` (lines 1-200) - Rendering logic. Understand how config is consumed.
- `backend/tests/test_icon_renderer.py` (lines 1-200) - Test patterns to follow for new tests.
- `backend/data/mapping.md` - Bid→deployment mappings. May need updates for new icons.

### Files That Will Be Modified

1. `backend/app/services/icon_config.py` - Add new icons to all four dictionaries
2. `backend/tests/test_icon_renderer.py` - Add tests for new configurations
3. `backend/data/mapping.md` - Add any missing bid→deployment mappings (if needed)

### Gear Icons Available (Not Currently Configured)

**Switches (13 unconfigured with images):**
```
Switches/1x4 PoE Extender.png
Switches/48V PoE Injector.png
Switches/Cisco 3560CX 12-P.png
Switches/Cisco 9300 48-P.png
Switches/Cisco 9500 48-P.png
Switches/Cisco MX.png
Switches/Fortinet 108F 8-P.png
Switches/Fortinet FortiGate.png
Switches/IDF.png
Switches/Media Converter.png
Switches/Netgear M4250 26-P.png
Switches/Netgear M4300 12x12F.png
Switches/Netonix 12-P AC.png
Switches/Netonix 6-P DC.png
Switches/Netonix 8-P DC.png
Switches/Raspberry Pi.png
```

**P2Ps (5 unconfigured with images):**
```
P2Ps/P2P - PrismStation w_ RF Elements 60° Horn.png
P2Ps/P2P - PrismStation w_ RF Elements 90° Horn.png
P2Ps/P2P - Ubiquiti Wave AP Micro.png
P2Ps/P2P - Ubiquiti Wave Nano.png
P2Ps/P2P - Ubiquiti Wave Pico.png
```

**IoT/Misc (21 unconfigured with images):**
```
Misc/AXIS M5526-E.png
Misc/Bike Rack.png
Misc/Conduit Well.png
Misc/Conduit.png
Misc/Dri Box.png
Misc/EcoFlow Battery.png
Misc/EcoFlow Solar Panel.png
Misc/Liebert UPS.png
Misc/Lock Box.png
Misc/Lock Box 2.png
Misc/Meraki MT15.png
Misc/Meraki MT40.png
Misc/MV93X.png
Misc/Patch Box.png
Misc/Patch Panel.png
Misc/Pinty Battery.png
Misc/Quad Box.png
Misc/Zarges Junction Box.png
Misc/Zarges XL Junction Box.png
```

**Hardlines (3 fiber connector types - unconfigured):**
```
Hardlines/LC SM.png
Hardlines/SC SM.png
Hardlines/ST SM.png
```

**Hardware (25 images - different use case, may skip):**
Hardware icons represent mounting equipment, not network gear. Consider adding a new "Hardware" category if these need rendering.

### BTX Deployment Subjects (Full Reference)

From BTX analysis, these are all 118 deployment subjects. Icons marked with ✅ are already configured:

**Access Points (10):**
- ✅ AP - Cisco MR36H
- ✅ AP - Cisco 9120
- ✅ AP - Cisco 9166I
- ✅ AP - Cisco 9166D
- ✅ AP - Cisco MR78
- ✅ AP - Cisco Marlin 4
- ✅ AP - Cisco DB10
- ❌ ANT - Internal (antenna, no gear image)
- ❌ ANT - Trout (External) (antenna, no gear image)
- ❌ ANT - Trout (Fixed) (antenna, no gear image)

**Switches (26):**
- ✅ SW - Cisco Micro 4P
- ✅ SW - Cisco 9200 12P
- ✅ SW - IDF Cisco 9300 24X
- ✅ DIST - Mini NOC
- ✅ DIST - Micro NOC
- ✅ DIST - Standard NOC
- ✅ DIST - Pelican NOC
- ✅ DIST - MikroTik Hex
- ✅ DIST - Starlink
- ❌ DIST - Cisco MX → Switches/Cisco MX.png
- ❌ DIST - Fortinet FortiGate → Switches/Fortinet FortiGate.png
- ❌ DIST - Mega NOC → Switches/NOC.png (reuse)
- ❌ SW - 1G 60W PoE Extender → Switches/1x4 PoE Extender.png
- ❌ SW - 1G PoE+ Injectors → Switches/48V PoE Injector.png
- ❌ SW - 1G PoE+ Media Converter → Switches/Media Converter.png
- ❌ SW - Cisco 9300 12X36M → Switches/Cisco 9300 24-P.png (similar)
- ❌ SW - Cisco 9300X 24X → Switches/Cisco 9300 24-P.png
- ❌ SW - Cisco 9300X 24Y → Switches/Cisco 9300 24-P.png
- ❌ SW - Cisco 9500 48Y4C → Switches/Cisco 9500 48-P.png
- ❌ SW - Fortinet 108F 8P → Switches/Fortinet 108F 8-P.png
- ❌ SW - IDF Cisco 9300 12X36M → Switches/Cisco 9300 24-P.png
- ❌ SW - IDF Cisco 9300X 24X → Switches/Cisco 9300 24-P.png
- ❌ SW - IDF Cisco 9300X 24Y → Switches/Cisco 9300 24-P.png
- ❌ SW - IDF Cisco 9500 48Y4C → Switches/Cisco 9500 48-P.png
- ❌ SW - Raspberry Pi → Switches/Raspberry Pi.png

**Point-to-Points (8):**
- ✅ P2P - Ubiquiti NanoBeam
- ✅ P2P - Ubiquiti LiteAP
- ✅ P2P - Ubiquiti GigaBeam
- ✅ P2P - Ubiquiti GigaBeam LR
- ❌ P2P - Link (generic, no specific image)
- ❌ P2P - Ubiquiti Wave AP Micro → P2Ps/P2P - Ubiquiti Wave AP Micro.png
- ❌ P2P - Ubiquiti Wave Nano → P2Ps/P2P - Ubiquiti Wave Nano.png
- ❌ P2P - Ubiquiti Wave Pico → P2Ps/P2P - Ubiquiti Wave Pico.png

**Hardlines (21):**
- ✅ HL - Artist (9 configured, all use CAT6 Cable.png)
- ❌ HL - (empty suffix) → Hardlines/CAT6 Cable.png
- ❌ HL - CCTV → Hardlines/CAT6 Cable.png
- ❌ HL - Clair → Hardlines/CAT6 Cable.png
- ❌ HL - IPTV → Hardlines/CAT6 Cable.png
- ❌ HL - LC SM → Hardlines/LC SM.png (fiber connector)
- ❌ HL - Lighting → Hardlines/CAT6 Cable.png
- ❌ HL - Media → Hardlines/CAT6 Cable.png
- ❌ HL - Radios → Hardlines/CAT6 Cable.png
- ❌ HL - SC SM → Hardlines/SC SM.png (fiber connector)
- ❌ HL - ST SM → Hardlines/ST SM.png (fiber connector)
- ❌ HL - Streaming → Hardlines/CAT6 Cable.png
- ❌ HL - Video → Hardlines/CAT6 Cable.png

**IoT (13):**
- ✅ VOIP - Yealink T29G
- ✅ VOIP - Yealink CP965
- ✅ CCTV - AXIS P5655-E
- ✅ CCTV - AXIS S9302
- ✅ EAS - Command Unit
- ✅ EAS - Laptop
- ✅ EAS - Trigger Box
- ✅ IPTV - BrightSign XT1144
- ❌ CCTV - AXIS M5526-E → Misc/AXIS M5526-E.png
- ❌ CCTV - Cisco MV93X → Misc/MV93X.png
- ❌ SEN - Meraki MT15 → Misc/Meraki MT15.png
- ❌ SEN - Meraki MT40 → Misc/Meraki MT40.png
- ❌ SEN - NetBeez Wi-Fi Sensor (no image available)

**Hardware (18):** Skip for now - mounting hardware, not network equipment

**Miscellaneous (20):**
- ✅ INFRA - Fiber Patch Panel (no_image: True)
- ❌ BOX - Dri Box → Misc/Dri Box.png
- ❌ BOX - Lock Box → Misc/Lock Box.png
- ❌ BOX - Patch Box → Misc/Patch Box.png
- ❌ BOX - Zarges Box → Misc/Zarges Junction Box.png
- ❌ BOX - Zarges XL Box → Misc/Zarges XL Junction Box.png
- ❌ INFRA - Conduit → Misc/Conduit.png
- ❌ INFRA - Conduit Well → Misc/Conduit Well.png
- ❌ MISC - Bike Rack → Misc/Bike Rack.png
- ❌ PWR - EcoFlow Battery → Misc/EcoFlow Battery.png
- ❌ PWR - EcoFlow Solar Panel → Misc/EcoFlow Solar Panel.png
- ❌ PWR - Liebert UPS → Misc/Liebert UPS.png
- ❌ PWR - Pinty Battery → Misc/Pinty Battery.png
- ❌ PWR - Quad Box → Misc/Quad Box.png
- ❌ Aerial, Conduit, Road Tape, Trench (infrastructure markers, no_image)
- ❌ MISC - Cable Ramp (no image available)

**Cables (2):**
- ✅ FIBER (no_image: True)
- ❌ Note (non-icon item, skip)

### Patterns to Follow

**ICON_CATEGORIES Pattern:**
```python
# Format: "Subject Name": "RenderingCategory"
"SW - Cisco Micro 4P": "Switches",
"DIST - Mini NOC": "Switches",  # DIST uses Switches category
```

**ICON_IMAGE_PATHS Pattern:**
```python
# Format: "Subject Name": "Category/Filename.png" or None
"SW - Cisco Micro 4P": "Switches/Cisco Micro 4-P.png",  # Note hyphen difference
"VOIP - Yealink CP965": "Misc/Yealink P965.png",  # Filename differs from subject
```

**ICON_OVERRIDES Pattern:**
```python
# Only add when value differs from category default
"SW - Cisco Micro 4P": {
    "brand_text": "CISCO",  # Switches default is empty
},
"DIST - Fortinet FortiGate": {
    "brand_text": "FORTINET",
},
```

**get_model_text() Brand Stripping:**
```python
# Brands to strip from model text (line 401)
for brand in ["Cisco ", "Ubiquiti ", "Axis ", "Yealink ", "BrightSign "]:
```

---

## IMPLEMENTATION PLAN

### Phase 1: Add New Rendering Categories

Add new categories needed for power equipment and infrastructure boxes.

**Tasks:**
- Add "Power" category to CATEGORY_DEFAULTS (brown/orange, similar to IoT)
- Add "Boxes" category to CATEGORY_DEFAULTS (gray, for junction/lock boxes)

### Phase 2: Expand Switches Configuration

Add 15 new switch/distribution icons.

**Tasks:**
- Add entries to ICON_CATEGORIES
- Add entries to ICON_IMAGE_PATHS
- Add ICON_OVERRIDES for brand text

### Phase 3: Expand P2Ps Configuration

Add 3 Ubiquiti Wave series P2P icons.

**Tasks:**
- Add entries to ICON_CATEGORIES
- Add entries to ICON_IMAGE_PATHS

### Phase 4: Expand Hardlines Configuration

Add 12 new hardline icons (copper and fiber).

**Tasks:**
- Add entries to ICON_CATEGORIES
- Add entries to ICON_IMAGE_PATHS
- Update category to "Fiber" for fiber connector types with appropriate color

### Phase 5: Expand IoT Configuration

Add 4 new IoT icons (CCTV, sensors).

**Tasks:**
- Add entries to ICON_CATEGORIES
- Add entries to ICON_IMAGE_PATHS
- Add ICON_OVERRIDES for brand text

### Phase 6: Expand Miscellaneous Configuration

Add 14 new misc icons (boxes, power, infrastructure).

**Tasks:**
- Add entries to ICON_CATEGORIES
- Add entries to ICON_IMAGE_PATHS
- Add ICON_OVERRIDES for brand text

### Phase 7: Update Helper Functions

Update `get_model_text()` to handle new brand patterns.

**Tasks:**
- Add new brand prefixes to strip list

### Phase 8: Add Unit Tests

Add comprehensive tests for new configurations.

**Tasks:**
- Test new category defaults exist
- Test new icon configs return correct values
- Test model text extraction for new patterns

---

## STEP-BY-STEP TASKS

IMPORTANT: Execute every task in order, top to bottom. Each task is atomic and independently testable.

### Task 1: UPDATE `icon_config.py` - Add New Category Defaults

**IMPLEMENT**: Add "Power" and "Fiber" category defaults to support new icon types.

**PATTERN**: Follow existing category structure at lines 91-227

**LOCATION**: Add after line 226 (before closing brace of CATEGORY_DEFAULTS)

```python
    "Power": {
        "circle_color": (0.4, 0.25, 0.1),  # Dark brown for power equipment
        "circle_border_width": 0.5,
        "circle_border_color": (0.0, 0.0, 0.0),
        "id_box_height": 4.0,
        "id_box_width_ratio": 0.55,
        "id_box_border_width": 0.6,
        "img_scale_ratio": 0.70,
        "brand_text": "",
        "brand_font_size": 1.9,
        "brand_y_offset": -3.0,
        "brand_x_offset": -0.2,
        "model_font_size": 1.6,
        "model_y_offset": 2.5,
        "model_x_offset": -0.7,
        "font_name": "/Helvetica-Bold",
        "text_color": (1.0, 1.0, 1.0),
        "id_text_color": None,
    },
    "Fiber": {
        "circle_color": (0.9, 0.5, 0.0),  # Orange for fiber connections
        "circle_border_width": 0.5,
        "circle_border_color": (0.0, 0.0, 0.0),
        "id_box_height": 4.0,
        "id_box_width_ratio": 0.55,
        "id_box_border_width": 0.6,
        "img_scale_ratio": 0.70,
        "brand_text": "FIBER",
        "brand_font_size": 1.9,
        "brand_y_offset": -3.0,
        "brand_x_offset": -0.2,
        "model_font_size": 1.6,
        "model_y_offset": 2.5,
        "model_x_offset": -0.7,
        "font_name": "/Helvetica-Bold",
        "text_color": (1.0, 1.0, 1.0),
        "id_text_color": None,
    },
    "Boxes": {
        "circle_color": (0.35, 0.35, 0.4),  # Dark gray for boxes
        "circle_border_width": 0.5,
        "circle_border_color": (0.0, 0.0, 0.0),
        "id_box_height": 4.0,
        "id_box_width_ratio": 0.55,
        "id_box_border_width": 0.6,
        "img_scale_ratio": 0.70,
        "brand_text": "",
        "brand_font_size": 1.9,
        "brand_y_offset": -3.0,
        "brand_x_offset": -0.2,
        "model_font_size": 1.6,
        "model_y_offset": 2.5,
        "model_x_offset": -0.7,
        "font_name": "/Helvetica-Bold",
        "text_color": (1.0, 1.0, 1.0),
        "id_text_color": None,
    },
```

**VALIDATE**: `cd backend && uv run python -c "from app.services.icon_config import CATEGORY_DEFAULTS; print('Power' in CATEGORY_DEFAULTS, 'Fiber' in CATEGORY_DEFAULTS, 'Boxes' in CATEGORY_DEFAULTS)"`

---

### Task 2: UPDATE `icon_config.py` - Add Switches to ICON_CATEGORIES

**IMPLEMENT**: Add 16 new switch/distribution subjects to ICON_CATEGORIES dict.

**LOCATION**: After line 55 (after existing DIST - Starlink entry)

```python
    # === Additional Switches ===
    "DIST - Cisco MX": "Switches",
    "DIST - Fortinet FortiGate": "Switches",
    "DIST - Mega NOC": "Switches",
    "SW - 1G 60W PoE Extender": "Switches",
    "SW - 1G PoE+ Injectors": "Switches",
    "SW - 1G PoE+ Media Converter": "Switches",
    "SW - Cisco 9300 12X36M": "Switches",
    "SW - Cisco 9300X 24X": "Switches",
    "SW - Cisco 9300X 24Y": "Switches",
    "SW - Cisco 9500 48Y4C": "Switches",
    "SW - Fortinet 108F 8P": "Switches",
    "SW - IDF Cisco 9300 12X36M": "Switches",
    "SW - IDF Cisco 9300X 24X": "Switches",
    "SW - IDF Cisco 9300X 24Y": "Switches",
    "SW - IDF Cisco 9500 48Y4C": "Switches",
    "SW - Raspberry Pi": "Switches",
```

**VALIDATE**: `cd backend && uv run python -c "from app.services.icon_config import ICON_CATEGORIES; print(len([k for k in ICON_CATEGORIES if k.startswith('SW') or k.startswith('DIST')]))"`

---

### Task 3: UPDATE `icon_config.py` - Add P2Ps to ICON_CATEGORIES

**IMPLEMENT**: Add 3 Wave series P2P subjects.

**LOCATION**: After line 60 (after existing P2P entries)

```python
    # === Additional Point-to-Points ===
    "P2P - Ubiquiti Wave AP Micro": "P2Ps",
    "P2P - Ubiquiti Wave Nano": "P2Ps",
    "P2P - Ubiquiti Wave Pico": "P2Ps",
```

**VALIDATE**: `cd backend && uv run python -c "from app.services.icon_config import ICON_CATEGORIES; print(len([k for k in ICON_CATEGORIES if k.startswith('P2P')]))"`

---

### Task 4: UPDATE `icon_config.py` - Add Hardlines to ICON_CATEGORIES

**IMPLEMENT**: Add 12 new hardline subjects (including fiber connectors).

**LOCATION**: After line 82 (after existing HL entries)

```python
    # === Additional Hardlines (copper) ===
    "HL -": "Hardlines",  # Empty suffix variant
    "HL - CCTV": "Hardlines",
    "HL - Clair": "Hardlines",
    "HL - IPTV": "Hardlines",
    "HL - Lighting": "Hardlines",
    "HL - Media": "Hardlines",
    "HL - Radios": "Hardlines",
    "HL - Streaming": "Hardlines",
    "HL - Video": "Hardlines",
    # === Fiber Connectors (use Fiber category) ===
    "HL - LC SM": "Fiber",
    "HL - SC SM": "Fiber",
    "HL - ST SM": "Fiber",
```

**VALIDATE**: `cd backend && uv run python -c "from app.services.icon_config import ICON_CATEGORIES; print(len([k for k in ICON_CATEGORIES if k.startswith('HL')]))"`

---

### Task 5: UPDATE `icon_config.py` - Add IoT to ICON_CATEGORIES

**IMPLEMENT**: Add 4 new IoT subjects.

**LOCATION**: After line 72 (after existing IoT entries)

```python
    # === Additional IoT / CCTV ===
    "CCTV - AXIS M5526-E": "IoT",
    "CCTV - Cisco MV93X": "IoT",
    # === IoT / Sensors ===
    "SEN - Meraki MT15": "IoT",
    "SEN - Meraki MT40": "IoT",
```

**VALIDATE**: `cd backend && uv run python -c "from app.services.icon_config import ICON_CATEGORIES; print(len([k for k in ICON_CATEGORIES if k.startswith('CCTV') or k.startswith('SEN')]))"`

---

### Task 6: UPDATE `icon_config.py` - Add Misc/Power/Boxes to ICON_CATEGORIES

**IMPLEMENT**: Add 14 new miscellaneous, power, and box subjects.

**LOCATION**: After line 86 (after existing Misc entries)

```python
    # === Boxes (junction boxes, lock boxes) ===
    "BOX - Dri Box": "Boxes",
    "BOX - Lock Box": "Boxes",
    "BOX - Patch Box": "Boxes",
    "BOX - Zarges Box": "Boxes",
    "BOX - Zarges XL Box": "Boxes",
    # === Power Equipment ===
    "PWR - EcoFlow Battery": "Power",
    "PWR - EcoFlow Solar Panel": "Power",
    "PWR - Liebert UPS": "Power",
    "PWR - Pinty Battery": "Power",
    "PWR - Quad Box": "Power",
    # === Infrastructure (with images) ===
    "INFRA - Conduit": "Misc",
    "INFRA - Conduit Well": "Misc",
    "MISC - Bike Rack": "Misc",
```

**VALIDATE**: `cd backend && uv run python -c "from app.services.icon_config import ICON_CATEGORIES; print(len([k for k in ICON_CATEGORIES if k.startswith('BOX') or k.startswith('PWR') or k.startswith('INFRA') or k.startswith('MISC')]))"`

---

### Task 7: UPDATE `icon_config.py` - Add Switches to ICON_IMAGE_PATHS

**IMPLEMENT**: Add image paths for all 16 new switches.

**LOCATION**: After line 304 (after existing switch image paths)

```python
    # === Additional Switches / Distribution ===
    "DIST - Cisco MX": "Switches/Cisco MX.png",
    "DIST - Fortinet FortiGate": "Switches/Fortinet FortiGate.png",
    "DIST - Mega NOC": "Switches/NOC.png",  # Reuse standard NOC image
    "SW - 1G 60W PoE Extender": "Switches/1x4 PoE Extender.png",
    "SW - 1G PoE+ Injectors": "Switches/48V PoE Injector.png",
    "SW - 1G PoE+ Media Converter": "Switches/Media Converter.png",
    "SW - Cisco 9300 12X36M": "Switches/Cisco 9300 24-P.png",  # Similar model
    "SW - Cisco 9300X 24X": "Switches/Cisco 9300 24-P.png",
    "SW - Cisco 9300X 24Y": "Switches/Cisco 9300 24-P.png",
    "SW - Cisco 9500 48Y4C": "Switches/Cisco 9500 48-P.png",
    "SW - Fortinet 108F 8P": "Switches/Fortinet 108F 8-P.png",
    "SW - IDF Cisco 9300 12X36M": "Switches/Cisco 9300 24-P.png",
    "SW - IDF Cisco 9300X 24X": "Switches/Cisco 9300 24-P.png",
    "SW - IDF Cisco 9300X 24Y": "Switches/Cisco 9300 24-P.png",
    "SW - IDF Cisco 9500 48Y4C": "Switches/Cisco 9500 48-P.png",
    "SW - Raspberry Pi": "Switches/Raspberry Pi.png",
```

**VALIDATE**: `cd backend && uv run python -c "from app.services.icon_config import ICON_IMAGE_PATHS; print(len([k for k in ICON_IMAGE_PATHS if 'Switches' in str(ICON_IMAGE_PATHS.get(k, ''))]))"`

---

### Task 8: UPDATE `icon_config.py` - Add P2Ps to ICON_IMAGE_PATHS

**IMPLEMENT**: Add image paths for 3 Wave series P2Ps.

**LOCATION**: After line 309 (after existing P2P image paths)

```python
    # === Additional Point-to-Points ===
    "P2P - Ubiquiti Wave AP Micro": "P2Ps/P2P - Ubiquiti Wave AP Micro.png",
    "P2P - Ubiquiti Wave Nano": "P2Ps/P2P - Ubiquiti Wave Nano.png",
    "P2P - Ubiquiti Wave Pico": "P2Ps/P2P - Ubiquiti Wave Pico.png",
```

**VALIDATE**: `cd backend && uv run python -c "from app.services.icon_config import ICON_IMAGE_PATHS; print(len([k for k in ICON_IMAGE_PATHS if k.startswith('P2P')]))"`

---

### Task 9: UPDATE `icon_config.py` - Add Hardlines to ICON_IMAGE_PATHS

**IMPLEMENT**: Add image paths for 12 new hardlines (copper use CAT6, fiber use specific).

**LOCATION**: After line 331 (after existing HL image paths)

```python
    # === Additional Hardlines (copper - use CAT6 Cable) ===
    "HL -": "Hardlines/CAT6 Cable.png",
    "HL - CCTV": "Hardlines/CAT6 Cable.png",
    "HL - Clair": "Hardlines/CAT6 Cable.png",
    "HL - IPTV": "Hardlines/CAT6 Cable.png",
    "HL - Lighting": "Hardlines/CAT6 Cable.png",
    "HL - Media": "Hardlines/CAT6 Cable.png",
    "HL - Radios": "Hardlines/CAT6 Cable.png",
    "HL - Streaming": "Hardlines/CAT6 Cable.png",
    "HL - Video": "Hardlines/CAT6 Cable.png",
    # === Fiber Connectors (specific images) ===
    "HL - LC SM": "Hardlines/LC SM.png",
    "HL - SC SM": "Hardlines/SC SM.png",
    "HL - ST SM": "Hardlines/ST SM.png",
```

**VALIDATE**: `cd backend && uv run python -c "from app.services.icon_config import ICON_IMAGE_PATHS; print(len([k for k in ICON_IMAGE_PATHS if k.startswith('HL')]))"`

---

### Task 10: UPDATE `icon_config.py` - Add IoT to ICON_IMAGE_PATHS

**IMPLEMENT**: Add image paths for 4 new IoT devices.

**LOCATION**: After line 321 (after existing IoT image paths)

```python
    # === Additional IoT / CCTV ===
    "CCTV - AXIS M5526-E": "Misc/AXIS M5526-E.png",
    "CCTV - Cisco MV93X": "Misc/MV93X.png",
    # === IoT / Sensors ===
    "SEN - Meraki MT15": "Misc/Meraki MT15.png",
    "SEN - Meraki MT40": "Misc/Meraki MT40.png",
```

**VALIDATE**: `cd backend && uv run python -c "from app.services.icon_config import ICON_IMAGE_PATHS; print(len([k for k in ICON_IMAGE_PATHS if 'Misc/' in str(ICON_IMAGE_PATHS.get(k, ''))]))"`

---

### Task 11: UPDATE `icon_config.py` - Add Misc/Power/Boxes to ICON_IMAGE_PATHS

**IMPLEMENT**: Add image paths for 13 new misc/power/box devices.

**LOCATION**: After line 335 (after existing Misc image paths)

```python
    # === Boxes ===
    "BOX - Dri Box": "Misc/Dri Box.png",
    "BOX - Lock Box": "Misc/Lock Box.png",
    "BOX - Patch Box": "Misc/Patch Box.png",
    "BOX - Zarges Box": "Misc/Zarges Junction Box.png",
    "BOX - Zarges XL Box": "Misc/Zarges XL Junction Box.png",
    # === Power Equipment ===
    "PWR - EcoFlow Battery": "Misc/EcoFlow Battery.png",
    "PWR - EcoFlow Solar Panel": "Misc/EcoFlow Solar Panel.png",
    "PWR - Liebert UPS": "Misc/Liebert UPS.png",
    "PWR - Pinty Battery": "Misc/Pinty Battery.png",
    "PWR - Quad Box": "Misc/Quad Box.png",
    # === Infrastructure ===
    "INFRA - Conduit": "Misc/Conduit.png",
    "INFRA - Conduit Well": "Misc/Conduit Well.png",
    "MISC - Bike Rack": "Misc/Bike Rack.png",
```

**VALIDATE**: `cd backend && uv run python -c "from app.services.icon_config import ICON_IMAGE_PATHS; print(len(ICON_IMAGE_PATHS))"`

---

### Task 12: UPDATE `icon_config.py` - Add ICON_OVERRIDES for Brand Text

**IMPLEMENT**: Add brand text overrides for new icons that need them.

**LOCATION**: After line 281 (after existing overrides)

```python
    # === Additional Switches with brand text ===
    "DIST - Cisco MX": {
        "brand_text": "CISCO",
    },
    "DIST - Fortinet FortiGate": {
        "brand_text": "FORTINET",
    },
    "SW - Cisco 9300 12X36M": {
        "brand_text": "CISCO",
    },
    "SW - Cisco 9300X 24X": {
        "brand_text": "CISCO",
    },
    "SW - Cisco 9300X 24Y": {
        "brand_text": "CISCO",
    },
    "SW - Cisco 9500 48Y4C": {
        "brand_text": "CISCO",
    },
    "SW - Fortinet 108F 8P": {
        "brand_text": "FORTINET",
    },
    "SW - IDF Cisco 9300 12X36M": {
        "brand_text": "CISCO",
    },
    "SW - IDF Cisco 9300X 24X": {
        "brand_text": "CISCO",
    },
    "SW - IDF Cisco 9300X 24Y": {
        "brand_text": "CISCO",
    },
    "SW - IDF Cisco 9500 48Y4C": {
        "brand_text": "CISCO",
    },
    # === Additional IoT with brand text ===
    "CCTV - AXIS M5526-E": {
        "brand_text": "AXIS",
    },
    "CCTV - Cisco MV93X": {
        "brand_text": "CISCO",
    },
    "SEN - Meraki MT15": {
        "brand_text": "MERAKI",
    },
    "SEN - Meraki MT40": {
        "brand_text": "MERAKI",
    },
    # === Power with brand text ===
    "PWR - EcoFlow Battery": {
        "brand_text": "ECOFLOW",
    },
    "PWR - EcoFlow Solar Panel": {
        "brand_text": "ECOFLOW",
    },
    "PWR - Liebert UPS": {
        "brand_text": "LIEBERT",
    },
```

**VALIDATE**: `cd backend && uv run python -c "from app.services.icon_config import ICON_OVERRIDES; print(len(ICON_OVERRIDES))"`

---

### Task 13: UPDATE `icon_config.py` - Expand get_model_text() Brands

**IMPLEMENT**: Add new brand prefixes to the brand stripping list.

**LOCATION**: Line 401 (modify existing for loop)

**CHANGE FROM:**
```python
            for brand in ["Cisco ", "Ubiquiti ", "Axis ", "Yealink ", "BrightSign "]:
```

**CHANGE TO:**
```python
            for brand in [
                "Cisco ", "Ubiquiti ", "Axis ", "Yealink ", "BrightSign ",
                "Fortinet ", "Meraki ", "EcoFlow ", "Liebert ", "Netgear ", "Netonix ",
            ]:
```

**VALIDATE**: `cd backend && uv run python -c "from app.services.icon_config import get_model_text; print(get_model_text('SW - Fortinet 108F 8P'), get_model_text('SEN - Meraki MT15'))"`

---

### Task 14: UPDATE `icon_config.py` - Add GEAR_ICON_CATEGORIES paths

**IMPLEMENT**: Ensure GEAR_ICON_CATEGORIES includes any needed category paths.

**LOCATION**: After line 31 (in GEAR_ICON_CATEGORIES dict)

No changes needed - existing categories cover all image paths. The images for Power, Boxes, Fiber all reside in existing category folders (Misc, Hardlines).

**VALIDATE**: `cd backend && uv run python -c "from app.services.icon_config import GEAR_ICON_CATEGORIES; print(list(GEAR_ICON_CATEGORIES.keys()))"`

---

### Task 15: ADD Unit Tests for New Categories

**IMPLEMENT**: Add tests for new category defaults.

**LOCATION**: `backend/tests/test_icon_renderer.py`, after line 89

```python
    def test_new_category_defaults_exist(self):
        """Test that new categories have defaults."""
        new_categories = ["Power", "Fiber", "Boxes"]
        for cat in new_categories:
            assert cat in CATEGORY_DEFAULTS, f"Missing defaults for {cat}"

    def test_power_category_has_brown_color(self):
        """Test Power category has brown color."""
        power = CATEGORY_DEFAULTS["Power"]
        assert power["circle_color"][0] > 0.3  # Brown has higher red
        assert power["circle_color"][1] < 0.4  # Lower green

    def test_fiber_category_has_orange_color(self):
        """Test Fiber category has orange color."""
        fiber = CATEGORY_DEFAULTS["Fiber"]
        assert fiber["circle_color"][0] > 0.8  # Orange has high red
        assert fiber["brand_text"] == "FIBER"
```

**VALIDATE**: `cd backend && uv run pytest tests/test_icon_renderer.py::TestIconConfig::test_new_category_defaults_exist -v`

---

### Task 16: ADD Unit Tests for New Icons

**IMPLEMENT**: Add tests for new icon configurations.

**LOCATION**: `backend/tests/test_icon_renderer.py`, after new category tests

```python
    def test_new_switch_icons_configured(self):
        """Test new switch icons return valid config."""
        new_switches = [
            "DIST - Cisco MX",
            "SW - Fortinet 108F 8P",
            "SW - Raspberry Pi",
        ]
        for subject in new_switches:
            config = get_icon_config(subject)
            assert config != {}, f"{subject} not configured"
            assert config["category"] == "Switches"

    def test_new_p2p_icons_configured(self):
        """Test new P2P icons return valid config."""
        new_p2ps = [
            "P2P - Ubiquiti Wave AP Micro",
            "P2P - Ubiquiti Wave Nano",
            "P2P - Ubiquiti Wave Pico",
        ]
        for subject in new_p2ps:
            config = get_icon_config(subject)
            assert config != {}, f"{subject} not configured"
            assert config["category"] == "P2Ps"

    def test_fiber_hardlines_use_fiber_category(self):
        """Test fiber connector hardlines use Fiber category."""
        fiber_types = ["HL - LC SM", "HL - SC SM", "HL - ST SM"]
        for subject in fiber_types:
            config = get_icon_config(subject)
            assert config["category"] == "Fiber", f"{subject} should be Fiber"

    def test_power_icons_configured(self):
        """Test power equipment icons return valid config."""
        power_icons = [
            "PWR - EcoFlow Battery",
            "PWR - Liebert UPS",
        ]
        for subject in power_icons:
            config = get_icon_config(subject)
            assert config != {}, f"{subject} not configured"
            assert config["category"] == "Power"

    def test_box_icons_configured(self):
        """Test box icons return valid config."""
        box_icons = [
            "BOX - Dri Box",
            "BOX - Zarges Box",
        ]
        for subject in box_icons:
            config = get_icon_config(subject)
            assert config != {}, f"{subject} not configured"
            assert config["category"] == "Boxes"

    def test_get_model_text_fortinet(self):
        """Test model text extraction for Fortinet device."""
        assert get_model_text("SW - Fortinet 108F 8P") == "108F 8P"

    def test_get_model_text_meraki(self):
        """Test model text extraction for Meraki device."""
        assert get_model_text("SEN - Meraki MT15") == "MT15"
```

**VALIDATE**: `cd backend && uv run pytest tests/test_icon_renderer.py -v -k "new_"`

---

### Task 17: Run Full Test Suite

**IMPLEMENT**: Verify all tests pass after changes.

**VALIDATE**: `cd backend && uv run pytest tests/test_icon_renderer.py -v`

---

### Task 18: Verify Icon Count

**IMPLEMENT**: Verify total icon count increased appropriately.

**VALIDATE**: `cd backend && uv run python -c "from app.services.icon_config import ICON_CATEGORIES, ICON_IMAGE_PATHS; print(f'ICON_CATEGORIES: {len(ICON_CATEGORIES)}', f'ICON_IMAGE_PATHS: {len(ICON_IMAGE_PATHS)}')"`

Expected: ~90 icons in ICON_CATEGORIES (was 39), ~88 in ICON_IMAGE_PATHS (was 37)

---

## TESTING STRATEGY

### Unit Tests

All new configurations tested via:
- `test_new_category_defaults_exist` - Verify Power, Fiber, Boxes categories
- `test_new_switch_icons_configured` - Verify switch icon configs
- `test_new_p2p_icons_configured` - Verify P2P icon configs
- `test_fiber_hardlines_use_fiber_category` - Verify fiber hardlines
- `test_power_icons_configured` - Verify power equipment configs
- `test_box_icons_configured` - Verify box icon configs
- `test_get_model_text_*` - Verify brand text extraction

### Integration Tests

Run full conversion test to verify icons render:
```bash
cd backend && uv run python scripts/test_conversion.py
```

### Edge Cases

- Empty hardline suffix (`HL -`)
- Icons with special characters (Wave° symbols in filenames)
- Icons sharing images (9300 variants)
- Icons with `None` image path (infrastructure markers)

### Known Issues

- **5 pre-existing failures** in `test_annotation_replacer.py` - PyMuPDF/PyPDF2 fixture incompatibility (unrelated to this feature)
- **11 skipped tests** - Features not implemented or require specific files

---

## VALIDATION COMMANDS

Execute every command to ensure zero regressions and 100% feature correctness.

### Level 1: Syntax & Style

```bash
cd backend && uv run ruff check app/services/icon_config.py
```

### Level 2: Unit Tests

```bash
cd backend && uv run pytest tests/test_icon_renderer.py -v
```

### Level 3: Full Test Suite

```bash
cd backend && uv run pytest -x --tb=short
```

Expected: ~122+ passed, 5 failed (known), 11 skipped

### Level 4: Manual Validation

Test a specific new icon renders correctly:
```bash
cd backend && uv run python scripts/test_icon_render.py "SW - Fortinet 108F 8P"
```

Verify output PDF shows green circle with gear image and "FORTINET" brand text.

### Level 5: E2E Conversion Test

```bash
cd backend && uv run python scripts/test_conversion.py
```

Verify conversion rate remains at or above 93.5% (376/402).

---

## ACCEPTANCE CRITERIA

- [ ] 3 new categories added to CATEGORY_DEFAULTS (Power, Fiber, Boxes)
- [ ] 51+ new icons added to ICON_CATEGORIES (total ~90)
- [ ] 51+ new icons added to ICON_IMAGE_PATHS (total ~88)
- [ ] Brand text overrides added for ~20 new icons
- [ ] `get_model_text()` handles new brand prefixes
- [ ] All validation commands pass
- [ ] Unit tests cover new configurations
- [ ] Full test suite passes (same 5 known failures)
- [ ] Manual icon render test shows correct visual

---

## COMPLETION CHECKLIST

- [ ] All tasks completed in order
- [ ] Each task validation passed immediately
- [ ] All validation commands executed successfully
- [ ] Full test suite passes (unit + integration)
- [ ] No linting or type checking errors
- [ ] Manual testing confirms icons render correctly
- [ ] Acceptance criteria all met
- [ ] Code reviewed for quality and maintainability

---

## NOTES

### Design Decisions

1. **New Categories vs Reusing Existing**: Created Power, Fiber, Boxes categories for visual distinction. Power equipment gets brown, fiber gets orange, boxes get dark gray.

2. **Image Reuse**: Many switch variants share images (9300 series all use same PNG). This is intentional - the physical appearance is similar.

3. **Hardware Icons Deferred**: The 25 hardware icons (mounting poles, clamps) are not network equipment and serve a different purpose. They can be added later if needed.

4. **Fiber Hardlines**: `HL - LC SM`, `HL - SC SM`, `HL - ST SM` use the Fiber category instead of Hardlines since they're fiber connectors, not copper.

5. **Brand Text Strategy**: Added overrides for icons where brand visibility is important (Cisco, Fortinet, Meraki, etc.). Generic equipment (PoE extenders) uses no brand text.

### Trade-offs

- **Image path variations**: Some filenames don't match subject names exactly (e.g., "4P" vs "4-P"). Documented in comments.
- **Shared images**: Some icons share the same gear image (9300 variants). This is acceptable for similar-looking equipment.

### Confidence Score: 9/10

High confidence because:
- This is primarily configuration additions (low risk)
- Clear patterns established by existing icons
- All gear images already exist
- Comprehensive test coverage planned
- No changes to core rendering logic
