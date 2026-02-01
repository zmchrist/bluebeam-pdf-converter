# Bluebeam Conversion Project Memory

**Last Updated:** January 30, 2026

---

## Session Update: 2026-01-30 (Night) - Clone Approach NOT WORKING

### Issue Discovered
**Script reports success but NO ICONS VISIBLE in output PDF!**

The `test_batch_clone.py` script reports converting 376/376 icons, but when the user opens `test_batch_clone_output.pdf`, no icons are visible. The conversion is silently failing despite appearing to succeed.

### What Was Attempted
- Created `backend/scripts/test_clone_icon.py` - Single icon cloning from DeploymentMap.pdf
- Created `backend/scripts/test_batch_clone.py` - Batch conversion of all icons
- Implemented coordinate transformation for PDF appearance streams
- Fixed PyPDF2 stream handling (DecodedStreamObject, no Filter copy)

### Technical Analysis

**Original BidMap.pdf annotations HAVE appearance streams:**
```
Subject: Artist - Indoor Wi-Fi Access Point
Subtype: /Circle
Rect: [6351.083, 7463.711, 6373.975, 7486.62]
Has /AP: Yes
AP stream (279 bytes): 0 0 0 RG 0.5968134 w 0.6 0.4 1 rg 6362.529 7464.308 m...
```

**Output PDF annotations appear to have data but don't render:**
- Annotations exist with correct subjects
- /AP dictionary exists
- Stream data appears present (~380 bytes)
- BUT icons don't appear when PDF is opened

### Possible Root Causes
1. **PyPDF2 annotation handling** - May not be properly linking annotations to page
2. **Indirect object references** - New annotations may not be properly registered
3. **Page /Annots array modification** - Changes may not persist correctly
4. **Stream encoding issue** - Despite data being present, may not be valid PDF stream

### Files Created (but not working)
- `backend/scripts/test_clone_icon.py` - Single icon clone test
- `backend/scripts/test_batch_clone.py` - Batch clone conversion
- `samples/maps/test_clone_output.pdf` - Output (icons not visible)
- `samples/maps/test_batch_clone_output.pdf` - Output (icons not visible)

### Status
**BLOCKED - Clone approach produces output but icons don't render**

Need to investigate why PyPDF2-created annotations aren't visible. May need to:
1. Use a different PDF library (pypdf, reportlab, PyMuPDF)
2. Debug the exact PDF structure differences between working and broken annotations
3. Try a completely different approach

---

## Session Update: 2026-01-30 (Evening) - Visual Icon Rendering

### Completed
- Created `backend/scripts/test_single_icon.py` - Single icon conversion test with embedded XObject image
- Successfully rendered a deployment icon with appearance stream (proof of concept)
- Analyzed BTX deployment icon structure (GROUP with 6 child annotations)

### Key Discoveries

**Deployment Icons are Complex Groups:**
Each deployment icon in BTX is a GROUP containing 6 child annotations:
| Child | Type | Purpose |
|-------|------|---------|
| 0 | FreeText | Reference label "j100" (top, blue text) |
| 1 | Circle | Blue circle background (RGB: 0.22, 0.34, 0.65) |
| 2 | **BBImage** | Product photo (Bluebeam-proprietary image type) |
| 3 | FreeText | "CISCO" header (white text) |
| 4 | FreeText | Model number "MR36H" (white text) |
| 5 | FreeText | Coordinate placeholder "xx' xx°" (blue text) |

**Appearance Stream Approach Works:**
- Created PDF appearance stream with embedded XObject image
- Used Bezier curves to draw circle, embedded PNG image, added text
- **Result:** Icon renders but as SQUARE instead of circle (Bezier issue)
- "CISCO" text visible, product image shows as white square

**Bid vs Deployment Icon Visual Difference:**
- Bid icons: Simple colored circles with WiFi symbol (single annotation)
- Deployment icons: Blue circle + product photo + text labels (complex group)

### Files Created
- `backend/scripts/test_single_icon.py` - Converts one "Artist - Indoor Wi-Fi Access Point" → "AP - Cisco 9120" with embedded image appearance
- `samples/maps/test_single_icon_output.pdf` - Test output PDF
- `samples/maps/test_single_icon_cropped.pdf` - Cropped view around converted icon

### Current Issue
Circle rendering as SQUARE - Bezier curve approximation not working correctly in PDF appearance stream. Need to fix the path drawing commands.

### Status
**Phase 3 visual appearance work in progress.** Proof of concept working - appearance streams render. Next: fix circle drawing, refine text positioning, then scale to all icons.

---

## Session Update: 2026-01-30 (Afternoon)

### Completed
- Created `backend/scripts/test_conversion.py` - End-to-end conversion test script
- Created `backend/app/services/appearance_extractor.py` - Extracts icon appearances from reference PDFs
- Updated `annotation_replacer.py` to use appearance data from reference PDFs
- Fixed mapping.md with actual subjects from BidMap.pdf (was using BTX subjects which didn't match)
- **Test conversion successful: 376/402 annotations converted (93.5%)**

### Key Discoveries

**Subject Name Mismatch:**
- BidMap.pdf uses different subject names than BTX files
- Example: PDF has "Artist - Indoor Wi-Fi Access Point", BTX has "Artist - Wi-Fi Access Point"
- Example: PDF has "Distribution - Edge Switch", BTX has "INFRAS - Edge Switch"
- **Solution:** Updated mapping.md with actual subjects from PDF

**Appearance Stream Approach:**
- Icons need `/AP` (appearance stream) for visual graphics - not just subject/colors
- BTX resources contain XObject images but embedding them is complex
- **Better approach:** Extract appearances from DeploymentMap.pdf and clone them
- Loaded 27 unique appearance streams from DeploymentMap.pdf

**Appearance Coverage:**
- 12 deployment subjects have visual appearances from reference PDF
- 25 deployment subjects missing (not in DeploymentMap.pdf) - fall back to colored shapes
- DeploymentMap.pdf has different model names (e.g., "AP - Cisco MR36H" vs "AP - Cisco 9120")

### Files Created
- `backend/scripts/test_conversion.py` - Test script for full conversion pipeline
- `backend/scripts/diagnose_annotations.py` - Diagnostic tool for PDF annotation analysis
- `backend/app/services/appearance_extractor.py` - Appearance stream extraction service

### Files Modified
- `backend/app/services/annotation_replacer.py` - Added appearance data support, BTX property parsing
- `backend/tests/test_annotation_replacer.py` - Updated tests for new behavior (uses /Subj not /Subject, /Circle not /Stamp)
- `backend/data/mapping.md` - Expanded to 89 mappings with actual PDF subjects

### Status
**Phase 3 partially complete.** Annotation replacement working but visual appearance limited by reference PDF coverage.

**26 skipped annotations are expected:** Legend items, gear lists, measurements (not equipment icons)

**Visual appearance gap:** Many deployment icons don't exist in DeploymentMap.pdf, so they show as colored shapes instead of icon graphics.

---

## Recent Progress: BTX Loader Implementation (2026-01-30)

### Completed Phase 2: BTX File Parsing

**BTXReferenceLoader** fully implemented in `backend/app/services/btx_loader.py`:

- `decode_hex_zlib()` - Decodes hex-encoded zlib-compressed BTX fields (magic: `789c`)
- `is_hex_zlib()` - Checks if string is zlib-compressed hex data
- `_parse_btx_file()` - Parses BTX XML, extracts ToolChestItem elements
- `_extract_subject_from_raw()` - Extracts subject from `/Subj(...)` in decoded Raw field
- `_extract_category_from_filename()` - Extracts category from BTX filename pattern
- `load_toolchest()` - Loads all BTX files from bid/deployment directories
- `get_icon_data()` - Retrieves IconData by subject name
- Helper methods: `get_bid_icon_count()`, `get_deployment_icon_count()`, `get_all_subjects()`, etc.

**Key Discoveries:**
- BTX `<Name>` element is NOT the display subject - it's a random internal ID
- Real subject name is in decoded `<Raw>` field as `/Subj(Subject Name Here)`
- All hex fields starting with `789c` are zlib-compressed
- BTX files may have UTF-8 BOM (`\xef\xbb\xbf`) - must strip before parsing

**Icons Discovered:**
- **Bid icons**: 70 icons from 1 BTX file
- **Deployment icons**: 118 icons from 8 BTX files

**Tests Added:**
- `backend/tests/test_btx_loader.py` - 24 unit tests, all passing

---

## Critical Architecture Understanding

### What the Product Actually Is:
**PDF Map Converter** - NOT a BTX file converter!

**User Workflow:**
1. User uploads: **PDF bid map** (with bid icon markups on venue map)
2. User selects: Conversion direction (Bid→Deployment or Deployment→Bid)
3. System processes: Parses PDF annotations, extracts subjects, maps icons using mapping.md, replaces annotations
4. User downloads: **Converted PDF deployment map** with deployment icons

### What Changed From Original Understanding:

**BEFORE (Incorrect):**
- Upload BTX files → Convert BTX icon definitions → Download converted BTX → Load into Bluebeam
- Mapping editor UI for creating icon pairs
- Visual icon pairing with drag-and-drop
- Multiple mapping configurations (JSON files)
- Mapping CRUD endpoints

**AFTER (Correct):**
- Upload PDF bid map → Convert PDF annotations → Download PDF deployment map
- NO BTX file upload from users
- NO mapping editor UI
- Static mapping.md file in backend (markdown table format)
- BTX files stay in toolchest/ as reference only
- Simple 3-step workflow: upload → convert → download

---

## Technical Details

### PDF Annotation Conversion Process:
1. Parse PDF to find all markup annotation coordinates
2. Extract subject field from each annotation (may need hex→string translation)
3. Look up subject in mapping.md to find corresponding deployment icon subject
4. Reference toolchest BTX files OR DeploymentMap.pdf to get deployment icon visual data
5. Delete bid icon annotation completely (subject + visual data)
6. Insert deployment icon annotation at exact same coordinates and size
7. Change both subject field AND visual appearance

### BTX File Format (Discovered):
```xml
<?xml version="1.0" encoding="utf-8"?>
<BluebeamRevuToolSet Version="1">
  <Title>789c...</Title>  <!-- hex zlib compressed -->
  <ToolChestItem Version="1">
    <Resources>
      <ID>789c...</ID>    <!-- hex zlib compressed -->
      <Data>789c...</Data> <!-- hex zlib binary image data -->
    </Resources>
    <Name>RANDOMCHARS</Name>  <!-- Internal ID, NOT display name -->
    <Type>Bluebeam.PDF.Annotations.AnnotationCircle</Type>
    <Raw>789c...</Raw>  <!-- hex zlib, contains /Subj(Subject Name) -->
    <X>0.075</X>
    <Y>0.075</Y>
    <Child>...</Child>  <!-- Nested child annotations -->
  </ToolChestItem>
</BluebeamRevuToolSet>
```

**Key Points:**
- Fields starting with `789c` are hex-encoded zlib-compressed
- `<Name>` is NOT the subject - it's a random internal ID
- Subject is in decoded `<Raw>` field: `/Subj(Subject Name Here)`
- Files may have UTF-8 BOM that must be stripped before XML parsing
- Resources contain XObject images (158x160 RGB with alpha mask)

### PDF Annotation Structure (from BidMap.pdf):
```
/Type: /Annot
/Subtype: /Circle (or /Square)
/Rect: [x1, y1, x2, y2]
/Subj: "Subject Name"
/IC: [r, g, b]  # Interior color
/C: [r, g, b]   # Border color
/BS: {/W: width, /S: /S}  # Border style
/AP: {/N: stream}  # Appearance stream (the actual graphics)
```

### Icon Matching Logic:
```
Find bid icon subject in PDF annotation →
Parse mapping.md markdown table →
Find bid subject row in mapping →
Get corresponding deployment subject →
Look up deployment icon appearance in DeploymentMap.pdf OR BTX →
Replace annotation (coords preserved, size preserved, subject + appearance changed)
```

### File Structure (Current State):

**toolchest/ directory:**
```
toolchest/
├── bidTools/
│   └── CDS Bluebeam Bid Tools [01-21-2026].btx  (single consolidated file)
├── deploymentTools/
│   ├── CDS Bluebeam Access Points [01-01-2026].btx
│   ├── CDS Bluebeam Cables [08-22-2025].btx
│   ├── CDS Bluebeam Hardlines [01-01-2026].btx
│   ├── CDS Bluebeam Hardware [01-01-2026].btx
│   ├── CDS Bluebeam IoT [01-01-2026].btx
│   ├── CDS Bluebeam Miscellaneous [01-01-2026].btx
│   ├── CDS Bluebeam Point-to-Points [01-01-2026].btx
│   └── CDS Bluebeam Switches [01-01-2026].btx
└── gearIcons/
```

**samples/ directory:**
```
samples/
├── icons/
│   ├── bidIcons/
│   └── deploymentIcons/
└── maps/
    ├── BidMap.pdf (4.3MB) - Sample bid map with markups
    ├── BidMap_converted_*.pdf - Generated conversion outputs
    └── DeploymentMap.pdf (8.1MB) - Reference for appearance extraction
```

### mapping.md File:
- **Location:** `backend/data/mapping.md`
- **Format:** Markdown table
- **Structure:**
  ```markdown
  | Bid Icon Subject | Deployment Icon Subject | Category |
  |------------------|------------------------|----------|
  | Artist - Indoor Wi-Fi Access Point | AP - Cisco 9120 | Access Points |
  | Distribution - Edge Switch | SW - Cisco 9200 12P | Switches |
  ```
- **Current Stats:** 89 mappings covering actual subjects from BidMap.pdf
- **Subject Name Patterns:**
  - Bid icons in PDF: `Category - Indoor/Outdoor/Medium Density Wi-Fi Access Point` style
  - Deployment icons: `Type - Model` (e.g., "AP - Cisco 9120", "SW - Cisco 9200 12P")
- **Purpose:** Single source of truth for bid↔deployment icon mappings
- **Scope:** Universal mapping applies to ALL conversions (one north star file)
- **Management:** Static, version-controlled, NOT user-editable via UI

---

## MVP Scope (Corrected)

### ✅ In Scope:
- Upload single PDF (bid or deployment map)
- Conversion direction selector (Bid→Deployment)
- PDF annotation parsing and extraction
- Subject name extraction (hex→string if needed)
- mapping.md parsing
- Annotation replacement (preserve coords, size; change subject + appearance)
- Download converted PDF
- Single-page PDF support (multi-page is future)
- Simple 3-step workflow UI

### ❌ Out of Scope (MVP):
- BTX file upload from users
- Mapping editor UI
- Visual icon pairing interface
- Mapping CRUD endpoints
- Multiple mapping configurations
- Preview before conversion
- Deployment→Bid reverse conversion (Phase 2)
- Multi-page PDF support (Phase 2)
- Batch PDF conversion (Phase 2)

---

## Technology Stack

### Backend:
- Python 3.11+
- FastAPI
- PDF library: PyPDF2 (working, but deprecated - consider pypdf)
- BTX XML parsing with lxml
- Markdown parsing for mapping.md

### Frontend:
- React 18
- TypeScript
- Tailwind CSS
- Simple upload/download UI (no complex mapping editor)

---

## API Endpoints (Simplified)

**Endpoint 1: Upload PDF**
- POST `/api/upload`
- Upload bid or deployment map PDF
- Returns upload_id

**Endpoint 2: Convert PDF**
- POST `/api/convert/{upload_id}`
- Request body: `{ "direction": "bid_to_deployment" }`
- Processes PDF annotations using mapping.md
- Returns conversion status and file_id

**Endpoint 3: Download Converted PDF**
- GET `/api/download/{file_id}`
- Downloads converted PDF

**Endpoint 4: Health Check**
- GET `/health`

---

## Implementation Phases Status:

### Phase 1: Core Backend Services ✅ COMPLETE
- [x] PDF parsing implementation (`pdf_parser.py`)
- [x] Subject extractor with hex decoding (`subject_extractor.py`)
- [x] Mapping parser for mapping.md (`mapping_parser.py`)
- [x] Basic validation utilities (`validation.py`)

### Phase 2: BTX File Parsing ✅ COMPLETE (2026-01-30)
- [x] BTX loader with zlib decompression (`btx_loader.py`)
- [x] Subject extraction from Raw fields
- [x] Icon data loading (70 bid, 118 deployment)
- [x] Comprehensive unit tests (24 tests passing)

### Phase 3: Annotation Replacement ⚠️ BLOCKED (2026-01-30)
- [x] `annotation_replacer.py` - Replace bid annotations with deployment
- [x] `appearance_extractor.py` - Extract appearances from reference PDF
- [x] `scripts/test_clone_icon.py` - Clone-based single icon conversion
- [x] `scripts/test_batch_clone.py` - Batch clone conversion
- [x] Coordinate transformation for appearance streams
- [ ] **BLOCKED: Icons don't render in output PDF despite script reporting success**

### Phase 4: API & Frontend (BLOCKED)
- [ ] FastAPI endpoints (upload, convert, download)
- [ ] React frontend with upload/download UI
- [ ] Integration testing

---

## Known Issues / Gaps

### CRITICAL: Converted Icons Not Visible
**Script reports 376/376 converted but NO icons appear in output PDF**

Investigation needed:
1. PyPDF2 may not properly handle annotation creation
2. May need different PDF library (pypdf, PyMuPDF, reportlab)
3. Need to compare raw PDF bytes between working and broken files

### Questions Resolved
- PDF annotations use `/Subj` key, not `/Subject`
- Original annotation types are `/Circle` and `/Square`, not `/Stamp`
- Subject names in PDF differ from BTX subject names
- DecodedStreamObject must NOT have `/Filter` copied from template
- Stream coordinates are absolute and need transformation with delta

---

**Status:** Phase 3 BLOCKED. Clone approach creates output file but icons don't render.
**Next Task:** Debug why PyPDF2-created annotations are invisible, or try different PDF library
