# Bluebeam Conversion Project Memory

**Last Updated:** January 29, 2026

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

### Annotation Format:
- Annotations are likely .btx format (need to verify)
- Subject names stored in annotation subject field
- BTX information may be in hexadecimal
- Need hex→string translation for subject names

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
  | AP_Bid | AP_Deploy | Access Points |
  | Switch_48Port_Bid | Switch_48Port_Deploy | Switches |
  ```
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

1. Update Architecture diagram (remove mapping UI, add PDF processing layer)
2. Update Directory Structure (add mapping.md, PDF services)
3. Revise Features section (PDF processing, annotation replacement)
4. Update Technology Stack (add PDF libraries)
5. Revise API Specification (4 endpoints only)
6. Update Implementation Phases (4 phases for simpler architecture)
7. Create mapping.md template file
8. Update README.md with corrected workflow
9. Examine sample PDFs to verify annotation format
10. Test PDF parsing libraries (PyPDF2 vs pypdf vs pdfplumber)

---

## Questions Still Needing Verification:

1. Are annotations actually .btx format or standard PDF annotations?
2. Is BTX information in hexadecimal? Need to verify with sample PDF.
3. Do subject names need hex→string translation? Check sample PDF.
4. Which PDF library works best with Bluebeam PDFs (PyPDF2, pypdf, pdfplumber)?

---

**Status:** In progress, ~40% complete on PRD updates
**Next Task:** Update Architecture diagram for PDF processing workflow
