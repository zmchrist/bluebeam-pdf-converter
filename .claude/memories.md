# Bluebeam Conversion Project Memory

**Last Updated:** January 30, 2026

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

**mapping.md Rebuilt:**
- Replaced placeholder subjects with real subjects from BTX files
- 68 bid→deployment mappings created (97.1% coverage)
- 2 unmapped bid icons (special items without deployment equivalents):
  - `CLAIR GEAR LIST` (title/header)
  - `MISC - 5G Cellular Hotspot (MiFi)` (portable device)

**Tests Added:**
- `backend/tests/test_btx_loader.py` - 24 unit tests, all passing

**User is manually reviewing mapping.md for accuracy.**

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
4. Reference toolchest BTX files to get deployment icon visual data
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

### Annotation Format:
- PDF annotations contain subject field that matches BTX subject names
- Subject names may be hex-encoded in PDF (use SubjectExtractor)
- Coordinates and size preserved during replacement

### Icon Matching Logic:
```
Find bid icon subject in PDF annotation →
Parse mapping.md markdown table →
Find bid subject row in mapping →
Get corresponding deployment subject →
Look up deployment icon in toolchest BTX →
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
    └── DeploymentMap.pdf (8.1MB) - Sample deployment map with markups
```

### mapping.md File:
- **Location:** `backend/data/mapping.md`
- **Format:** Markdown table
- **Structure:**
  ```markdown
  | Bid Icon Subject | Deployment Icon Subject | Category |
  |------------------|------------------------|----------|
  | Access Control - Wi-Fi Access Point | AP - Cisco 9120 | Access Points |
  | INFRAS - Edge Switch | SW - Cisco 9200 12P | Switches |
  | INFRAS - Point-to-Point Transeiver | P2P - Ubiquiti NanoBeam | Point-to-Points |
  ```
- **Current Stats:** 68 mappings covering 97.1% of bid icons
- **Subject Name Patterns:**
  - Bid icons: `Category - Description` (e.g., "Access Control - Wi-Fi Access Point")
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
- PDF library: PyPDF2, pypdf, or pdfplumber (need to test which works best)
- BTX XML parsing (for toolchest icon reference)
- Markdown parsing (for mapping.md)

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

## PRD Updates Completed (2026-01-29):

1. ✅ **Executive Summary** - Updated to describe PDF conversion workflow
2. ✅ **Mission & Core Principles** - Changed to 3-step workflow, accuracy focus
3. ✅ **MVP Scope** - Removed BTX upload, mapping UI; added PDF processing
4. ✅ **User Stories** - Completely rewritten for PDF upload/download workflow (6 stories)

## PRD Updates Still Needed:

5. ⏳ **Architecture Diagram** - Update for PDF processing (remove mapping UI layer)
6. ⏳ **Directory Structure** - Add mapping.md, PDF processing services
7. ⏳ **Features Section** - Remove mapping editor, add PDF annotation processing
8. ⏳ **Technology Stack** - Add PDF libraries, remove mapping CRUD
9. ⏳ **API Specification** - Simplify to 4 endpoints (upload, convert, download, health)
10. ⏳ **Implementation Phases** - Revise for simpler architecture (4 phases instead of 6)

---

## Key User Answers from Conversation:

**Q: How do we parse PDF annotations?**
A: Parse PDF directly to find markup annotation coordinates. Map underneath is flat, so only icon markups exist.

**Q: What format is mapping.md?**
A: Markdown table with columns: Bid Icon Subject, Deployment Icon Subject, Category

**Q: Multiple mapping files?**
A: NO - One mapping.md file that applies universally to all conversions

**Q: Where does mapping.md live?**
A: `backend/data/mapping.md`

**Q: Subject name matching?**
A: Extract subject from PDF annotation (may need hex→string translation), look up in mapping.md, find corresponding deployment subject

**Q: Multi-page PDFs?**
A: Single-page for MVP. Multi-page is future enhancement.

**Q: How to replace annotations?**
A: Find coords → translate subject via mapping.md → delete bid annotation entirely → insert deployment annotation at same coords/size

**Q: What needs to change in annotation?**
A: Both subject field AND visual appearance. Delete bid icon completely, replace with deployment icon.

---

## Next Steps (In Order):

### Immediate (User Action Required):
1. **User to review mapping.md** - Verify bid→deployment mappings are correct

### After Mapping Verification:
2. Implement `annotation_replacer.py` - Core annotation replacement logic
3. Implement `pdf_reconstructor.py` - Write modified PDFs with new annotations
4. Test with sample BidMap.pdf to verify conversion works
5. Build FastAPI endpoints (upload, convert, download)
6. Create React frontend UI

### Documentation (Lower Priority):
7. Update Architecture diagram (remove mapping UI, add PDF processing layer)
8. Update Directory Structure in PRD
9. Update README.md with corrected workflow

---

## Questions Still Needing Verification:

1. ~~Are annotations actually .btx format or standard PDF annotations?~~ - **ANSWERED:** BTX files are XML with zlib-compressed hex fields
2. ~~Is BTX information in hexadecimal?~~ - **ANSWERED:** Yes, fields starting with `789c` are hex-encoded zlib-compressed
3. ~~Do subject names need hex→string translation?~~ - **ANSWERED:** Subject is in decoded `<Raw>` field as `/Subj(Name)`
4. Which PDF library works best with Bluebeam PDFs (PyPDF2, pypdf, pdfplumber)? - Still needs testing

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
- [x] mapping.md rebuilt with real subjects (68 mappings)
- [x] Comprehensive unit tests (24 tests passing)
- [ ] User reviewing mapping.md for accuracy

### Phase 3: Annotation Replacement (NEXT)
- [ ] `annotation_replacer.py` - Replace bid annotations with deployment
- [ ] `pdf_reconstructor.py` - Write modified PDF

### Phase 4: API & Frontend
- [ ] FastAPI endpoints (upload, convert, download)
- [ ] React frontend with upload/download UI
- [ ] Integration testing

---

**Status:** Phase 2 complete, awaiting user verification of mapping.md
**Next Task:** User to review mapping.md, then proceed to Phase 3 (Annotation Replacement)
