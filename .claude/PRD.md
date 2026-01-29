# Product Requirements Document: Bluebeam BTX Icon Converter

**Version:** 1.0
**Last Updated:** January 29, 2026
**Status:** Draft

---

## 1. Executive Summary

The Bluebeam PDF Map Converter is a web-based tool designed to streamline the conversion of venue maps from "bid maps" to "deployment maps" within Bluebeam Revu PDF markup workflows. During the bid phase, estimators mark equipment locations on PDF venue maps (sports arenas, concert halls, outdoor festivals) by dragging bid icons onto plans to show WiFi access points, switches, and other equipment. After winning the bid, these same PDF maps need to display deployment icons instead—icons that differ in color, shape, and labeling to reflect the deployment phase. Currently, converting these maps requires manually replacing each icon markup on the PDF, a time-consuming and error-prone process that can take 2-4 hours for projects with dozens or hundreds of marked locations.

This tool automates the conversion by directly transforming the PDF markup annotations themselves. Users upload a bid map PDF, select the conversion direction (bid→deployment or deployment→bid), and the system parses all icon markup annotations in the PDF, identifies their subject names, uses a predefined mapping configuration to determine the corresponding icon type, and replaces each annotation with the mapped icon while preserving exact coordinates and sizing. The result is a converted PDF that users can immediately download and use in their deployment workflows.

The MVP goal is to deliver a production-ready web application within 1-2 months that eliminates manual icon replacement, uses a backend mapping configuration (mapping.md) to define bid↔deployment icon pairs, ensures consistent conversions by referencing BTX toolsets in the toolchest directory, and reduces conversion time from 2-4 hours to under 1 minute.

## 2. Mission

**Mission Statement:**
Empower internal estimators and project managers to efficiently convert venue map PDFs from bid phase to deployment phase by transforming markup annotations directly within PDF files, eliminating hours of manual icon replacement and ensuring consistent, accurate conversions across all project drawings.

**Core Principles:**
1. **Simplicity First** — Three-step workflow (upload PDF → select conversion direction → download converted PDF) with minimal learning curve
2. **Accuracy** — Preserve exact markup coordinates and sizing while replacing icon appearances and subjects
3. **Reliability** — Deterministic, reproducible conversions using predefined mapping.md configuration
4. **Speed** — Reduce conversion time from 2-4 hours to under 1 minute
5. **Safety** — Never modify original files; always provide new converted PDF files for download

## 3. Target Users

### Primary User Personas

**Persona 1: Project Estimator**
- **Role:** Creates bid estimates by marking equipment locations on PDF drawings using bid icons in Bluebeam Revu
- **Technical Level:** Moderate (comfortable with PDF markup tools, basic file management)
- **Current Workflow:** During bidding, drags bid icons onto PDF floor plans to show where equipment will be installed. After winning bid, needs to convert those markups to deployment icons.
- **Pain Points:**
  - Manually replacing bid icons with deployment icons on marked PDFs takes 2-4 hours per project
  - Risk of missing locations or creating inconsistencies when manually re-marking
  - Must remember which bid icon corresponds to which deployment icon
  - Repetitive process across multiple projects and drawing sets
- **Goals:** Convert all bid icon markups to deployment icons quickly and accurately without re-marking locations

**Persona 2: Project Manager**
- **Role:** Manages PDF workflows and documentation for construction/engineering projects
- **Technical Level:** Basic to moderate (familiar with PDFs, less comfortable with technical file formats)
- **Current Workflow:** Receives marked-up bid drawings from estimators, needs to prepare deployment drawings with appropriate deployment icons for field teams.
- **Pain Points:**
  - Needs to ensure consistency across team's icon usage and conversions
  - No standardized way to handle bid-to-deployment transitions
  - Time pressure to deliver deployment drawings quickly after bid award
  - Difficulty tracking which icons have been converted
- **Goals:** Streamline the bid-to-deployment transition with consistent, reliable icon conversions

### Key User Needs
- Define custom mappings between bid and deployment icons
- Upload multiple BTX files at once for batch conversion
- See visual preview showing exactly how bid icons will become deployment icons
- Download converted BTX files to use in Bluebeam (markups auto-update to deployment icons)
- Save and reuse mapping configurations across projects
- Confidence that all markup locations are preserved with correct deployment icons

## 4. MVP Scope

### ✅ In Scope: Core Functionality

**PDF File Processing:**
- ✅ Upload single PDF venue map (bid map or deployment map)
- ✅ Drag-and-drop PDF file upload interface
- ✅ PDF file validation and error handling
- ✅ Single-page PDF processing (multi-page is future enhancement)
- ✅ Download converted PDF file

**Conversion Features:**
- ✅ Bid→Deployment icon conversion (primary focus)
- ✅ PDF annotation parsing and extraction
- ✅ Icon subject name extraction (hex→string translation if needed)
- ✅ mapping.md parsing for bid↔deployment icon pairs
- ✅ Annotation coordinate preservation
- ✅ Icon size preservation (deployment icon matches bid icon size exactly)
- ✅ Subject field and visual appearance replacement
- ✅ Complete bid annotation deletion and deployment annotation insertion

**Mapping Configuration:**
- ✅ Backend mapping.md file in markdown table format
- ✅ Static mapping configuration (version-controlled, not user-editable via UI)
- ✅ Toolchest BTX file references for icon visual data
- ✅ Mapping validation on application startup

**User Interface:**
- ✅ Simple PDF upload component
- ✅ Conversion direction selector (Bid→Deployment)
- ✅ Progress indicators during conversion
- ✅ Success/error notifications
- ✅ Download button for converted PDF
- ✅ Responsive design for desktop use

**Technical Requirements:**
- ✅ Python backend with FastAPI
- ✅ React frontend with TypeScript
- ✅ PDF parsing library (PyPDF2, pypdf, or pdfplumber)
- ✅ BTX XML parsing for toolchest icon reference
- ✅ Local file processing (no external dependencies)
- ✅ Comprehensive error handling and logging

### ❌ Out of Scope: Future Enhancements

**Phase 2 Features (Post-MVP):**
- ❌ Deployment→Bid reverse conversion (after bid→deployment is stable)
- ❌ Multi-page PDF support
- ❌ Batch PDF conversion (multiple PDFs at once)
- ❌ User-editable mapping configurations via UI
- ❌ Preview before conversion
- ❌ Selective icon conversion (choose specific icons to convert)

**Advanced Features:**
- ❌ User authentication and accounts
- ❌ Cloud storage integration
- ❌ Auto-detection of icon mapping patterns from PDF annotations
- ❌ Mapping confidence scoring and suggestions
- ❌ Advanced mapping rules (regex, wildcards, conditional mappings)
- ❌ Icon library management and browsing
- ❌ Collaborative features or sharing

**Integration:**
- ❌ Bluebeam Revu plugin/extension
- ❌ API for third-party integrations
- ❌ Mobile app version
- ❌ Integration with cloud PDF services

**Deployment:**
- ❌ Multi-tenancy support
- ❌ Database persistence of conversions
- ❌ User analytics and usage tracking
- ❌ Enterprise SSO integration

## 5. User Stories

**Story 1: Converting a Bid Map to Deployment Map**
_As a project estimator, I want to upload a bid map PDF and receive a deployment map PDF with all icon markups automatically converted, so that I don't have to manually re-mark 75+ equipment locations after winning a bid._

**Example:** Bob is working on a new project for a large sports arena. He receives the production-supplied venue map showing all areas and connectivity requirements. He loads his bid icons toolset into Bluebeam and marks 75+ locations across the arena where WiFi access points, switches, and other equipment will be installed. After submitting the bid and winning the contract, Bob needs a deployment map. He opens the converter web app, drags his bid map PDF into the upload area, clicks "Convert: Bid→Deployment", waits 30 seconds while the system processes, and downloads the converted deployment map PDF. He opens it in Bluebeam and verifies that all 75+ markups now show deployment icons with correct colors, labels, and visual appearance—no manual re-marking needed.

**Story 2: Quick Turnaround After Bid Award**
_As a project manager, I want to convert venue bid maps to deployment maps in under 1 minute, so that I can deliver deployment documentation to field teams immediately after bid acceptance._

**Example:** Sarah just received notice that her company won a concert hall WiFi installation bid. The client needs deployment drawings by end of day. She opens the converter, uploads the concert hall bid map PDF (marked with 40 bid icon locations), selects "Bid→Deployment", and downloads the converted deployment map in 45 seconds. She emails it to the field team and client within 5 minutes of bid acceptance, meeting the tight deadline.

**Story 3: Consistent Conversions Across Projects**
_As a project estimator, I want all icon conversions to follow the same mapping rules automatically, so that I get consistent deployment maps without configuring anything._

**Example:** Tom handles 3-4 venue projects per month (sports arenas, concert halls, festivals). Every time he converts a bid map, the system uses the same mapping.md configuration: "AP_Bid" always becomes "AP_Deploy_Green", "Switch_48Port_Bid" always becomes "Switch_48Port_Deploy_Labeled", etc. He doesn't need to select mappings, create configurations, or remember icon pairs—the backend handles it automatically, ensuring consistency across all his projects.

**Story 4: Error Handling for Invalid PDFs**
_As a project estimator, I want clear error messages if my PDF can't be converted, so that I can fix issues and successfully complete my conversion._

**Example:** Lisa uploads a PDF that doesn't contain any Bluebeam icon markup annotations (it only has the venue map image, no equipment markups). The system displays: "No icon markup annotations found in PDF. Please verify you uploaded a bid map with equipment location markups." She realizes she uploaded the wrong file, selects the correct marked-up bid map, and the conversion proceeds successfully.

**Story 5: Preserving Markup Locations and Sizing**
_As a project manager, I want all deployment icons to appear at the exact same coordinates and sizes as the bid icons, so that equipment locations remain accurate on the converted deployment maps._

**Example:** Rachel converts an outdoor festival bid map with 120 marked equipment locations. After conversion, she overlays the bid map and deployment map PDFs in Bluebeam and verifies that every icon is in the exact same position—no shift in coordinates, no size changes, just the icon appearance and labeling updated. The deployment map is pixel-perfect accurate for field installation.

**Story 6: Deterministic and Reproducible Conversions**
_As a project estimator, I want to be able to reconvert the same bid map and get identical results, so that I can regenerate deployment maps if files are lost or clients request revisions._

**Example:** Mike needs to regenerate a deployment map he created 2 weeks ago because the client requested documentation changes (non-icon-related). He uploads the same bid map PDF he converted before, clicks "Bid→Deployment", and downloads the result. The converted deployment map is byte-for-byte identical to the one he created 2 weeks ago, confirming the conversion is deterministic and reliable. His documentation remains consistent across revisions.

## 6. Core Architecture & Patterns

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Web Browser                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │           React Frontend (Port 5173)               │  │
│  │  • PDF upload component (drag-drop)                │  │
│  │  • Conversion direction selector                   │  │
│  │  • Progress indicator                              │  │
│  │  • PDF download button                             │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────┬──────────────────────────────────────┘
                      │ HTTP/JSON (REST API)
                      ▼
┌──────────────────────────────────────────────────────────┐
│           FastAPI Backend (Port 8000)                    │
│  ┌────────────────────────────────────────────────────┐  │
│  │              API Layer                             │  │
│  │  • POST /api/upload - PDF upload                   │  │
│  │  • POST /api/convert - Annotation conversion       │  │
│  │  • GET /api/download/{id} - PDF download           │  │
│  │  • GET /health - Health check                      │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │           Processing Layer                         │  │
│  │  • PDFAnnotationParser - Extract annotations       │  │
│  │  • SubjectExtractor - Extract/translate subjects   │  │
│  │  • MappingParser - Parse mapping.md                │  │
│  │  • BTXReferenceLoader - Load toolchest icon data   │  │
│  │  • AnnotationReplacer - Replace bid→deployment     │  │
│  │  • PDFReconstructor - Rebuild PDF with new annots  │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │            Data Layer                              │  │
│  │  • Temporary PDF storage (uploads/conversions)     │  │
│  │  • mapping.md (backend/data/mapping.md)            │  │
│  │  • toolchest/ BTX reference files                  │  │
│  │    - bidTools/ (bid icon definitions)              │  │
│  │    - deploymentTools/ (deployment icon defs)       │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### Directory Structure

```
Bluebeam Conversion/
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── config.py                 # Configuration and settings
│   │   ├── models/
│   │   │   ├── pdf_file.py           # PDF file data models
│   │   │   ├── annotation.py         # Annotation data models
│   │   │   └── mapping.py            # Mapping data models
│   │   ├── services/
│   │   │   ├── pdf_parser.py         # PDF annotation parsing
│   │   │   ├── subject_extractor.py  # Extract/translate subjects (hex→string)
│   │   │   ├── mapping_parser.py     # Parse mapping.md file
│   │   │   ├── btx_loader.py         # Load toolchest BTX icon data
│   │   │   ├── annotation_replacer.py # Replace bid→deployment annotations
│   │   │   └── pdf_reconstructor.py  # Rebuild PDF with new annotations
│   │   ├── routers/
│   │   │   ├── upload.py             # PDF upload endpoint
│   │   │   ├── convert.py            # Conversion endpoint
│   │   │   └── download.py           # PDF download endpoint
│   │   └── utils/
│   │       ├── validation.py         # Input validation utilities
│   │       └── errors.py             # Custom exception classes
│   ├── tests/
│   │   ├── test_pdf_parser.py
│   │   ├── test_subject_extractor.py
│   │   ├── test_mapping_parser.py
│   │   ├── test_annotation_replacer.py
│   │   └── test_api.py
│   ├── data/
│   │   ├── mapping.md                # Icon mapping configuration (markdown)
│   │   └── temp/                     # Temporary PDF storage
│   ├── requirements.txt              # Python dependencies
│   └── pyproject.toml                # uv project configuration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PDFUpload/
│   │   │   │   └── DropZone.tsx      # Drag-drop PDF upload
│   │   │   ├── ConversionSelector/
│   │   │   │   └── DirectionPicker.tsx # Bid↔Deployment selector
│   │   │   ├── Progress/
│   │   │   │   └── ProgressBar.tsx   # Conversion progress
│   │   │   └── Download/
│   │   │       └── DownloadButton.tsx # PDF download button
│   │   ├── services/
│   │   │   └── api.ts                # API client
│   │   ├── hooks/
│   │   │   ├── usePDFUpload.ts
│   │   │   └── useConversion.ts
│   │   ├── types/
│   │   │   └── index.ts              # TypeScript type definitions
│   │   ├── App.tsx                   # Main application component
│   │   └── main.tsx                  # Application entry point
│   ├── package.json
│   └── vite.config.ts
├── toolchest/                        # Reference BTX files (not uploaded by users)
├── samples/                        # Sample icons and maps
│   ├── icons/
│   │   ├── bidIcons/
│   │   └── deploymentIcons/
│   └── maps/
│       ├── BidMap.pdf
│       └── DeploymentMap.pdf
├── .claude/                        # Claude Code commands
├── bluebeamPlan.md
├── PRD.md
└── README.md
```

### Key Design Patterns

**1. Service Layer Pattern**
Business logic separated into dedicated service classes (BTXParser, IconMapper, FileProcessor) for testability and maintainability.

**2. Repository Pattern**
File storage and retrieval abstracted through FileProcessor service, enabling easy swap of storage mechanisms (local → cloud).

**3. Request-Response Model**
All API endpoints follow consistent request/response schemas with Pydantic validation for type safety.

**4. Component Composition**
Frontend built with composable React components, each handling a single responsibility.

**5. Error Boundary Pattern**
Comprehensive error handling at API, service, and UI layers with user-friendly error messages.

## 7. Core Features

### Feature 1: PDF Upload System

**Purpose:** Enable users to upload a single PDF venue map (bid or deployment map) for conversion

**Components:**
- Drag-and-drop zone with visual feedback for PDF files
- File browser fallback for traditional upload
- File type validation (.pdf extension)
- PDF structure validation (verify it's a valid PDF)
- File size validation (max 50MB for venue maps)

**User Flow:**
1. User drags PDF bid map onto drop zone OR clicks to browse
2. System validates file type (PDF) and file size
3. System performs basic PDF structure check
4. PDF appears in upload area with filename and ready status
5. User proceeds to select conversion direction

**Technical Details:**
- Frontend: HTML5 File API with React drag-and-drop
- Backend: FastAPI file upload with UploadFile
- Validation: PDF magic number check (%PDF header), extension verification
- Storage: Temporary directory (backend/data/temp/) with UUID-based naming
- File retention: Temporary files cleaned up after 1 hour

### Feature 2: Conversion Direction Selector

**Purpose:** Allow users to choose between bid→deployment or deployment→bid conversion (MVP focuses on bid→deployment)

**Components:**
- Radio button selector for conversion direction
- Visual indicator showing selected direction
- Direction validation before processing
- (MVP: Only bid→deployment enabled; deployment→bid grayed out for Phase 2)

**User Flow:**
1. After PDF upload, user sees conversion direction selector
2. User selects "Bid → Deployment" (default selection)
3. "Deployment → Bid" option shown but disabled (Phase 2)
4. User clicks "Convert" button to start processing

**Technical Details:**
- Frontend: React controlled component with state management
- API parameter: `{ "direction": "bid_to_deployment" }` sent to convert endpoint
- Backend validation: Ensure direction parameter is valid
- MVP constraint: Only "bid_to_deployment" accepted; return 400 for other directions

### Feature 3: PDF Annotation Parsing

**Purpose:** Extract markup annotations from uploaded PDF to identify icon locations and subjects

**Components:**
- PDFAnnotationParser service
- Annotation coordinate extraction
- Subject field extraction (icon identifier)
- Hex→string translation for subject names (if needed)
- Annotation metadata collection (size, position, page number)

**Processing Flow:**
1. Parse PDF structure using PyPDF2/pypdf/pdfplumber
2. Iterate through PDF pages (MVP: single-page only)
3. Find all markup annotations (icon stamps/callouts)
4. For each annotation, extract:
   - X, Y coordinates (exact position on page)
   - Width and height (icon size)
   - Subject field (icon identifier, e.g., "AP_Bid", "Switch_48Port_Bid")
   - Page number (always 1 for MVP)
5. Translate subject from hexadecimal to string if needed
6. Build list of all annotations to convert

**Technical Details:**
- PDF Library: PyPDF2, pypdf, or pdfplumber (test which works best with Bluebeam PDFs)
- Subject extraction: Parse annotation dictionary `/Subj` field
- Hex translation: Check if subject is hex-encoded (e.g., "4150005f426964" → "AP_Bid")
- Error handling: Gracefully handle PDFs with no annotations, warn user
- Output: List of Annotation objects with coords, size, subject

### Feature 4: Mapping Configuration (Backend)

**Purpose:** Provide static mapping.md file that defines bid↔deployment icon pairs for all conversions

**Components:**
- mapping.md markdown table in backend/data/ directory
- MappingParser service to read and parse markdown table
- Mapping validation on application startup
- Mapping cache for fast lookups during conversion

**mapping.md Structure:**
```markdown
| Bid Icon Subject | Deployment Icon Subject | Category |
|------------------|------------------------|----------|
| AP_Bid | AP_Deploy | Access Points |
| Switch_48Port_Bid | Switch_48Port_Deploy | Switches |
| Switch_24Port_Bid | Switch_24Port_Deploy | Switches |
| Cable_Cat6_Bid | Cable_Cat6_Deploy | Cables |
| Hardware_Rack_Bid | Hardware_Rack_Deploy | Hardware |
```

**Technical Details:**
- File location: `backend/data/mapping.md`
- Format: Markdown table with 3 columns (Bid Icon Subject, Deployment Icon Subject, Category)
- Parsing: Python markdown library or simple regex parsing
- Validation: Ensure all rows have 3 columns, no duplicate bid subjects
- Cache: Load mapping into dictionary on startup for O(1) lookups
- Version control: mapping.md committed to git as single source of truth
- NO user editing via UI (static configuration file)

### Feature 5: BTX Reference Loader

**Purpose:** Load icon visual data from toolchest BTX files to apply during annotation replacement

**Components:**
- BTXReferenceLoader service
- XML parsing for BTX toolset files
- Icon data extraction (colors, shapes, labels)
- Zlib decompression for binary icon data
- Icon lookup by subject name

**Processing Flow:**
1. On application startup, scan toolchest/ directories:
   - `toolchest/bidTools/CDS Bluebeam Bid Tools [01-21-2026].btx`
   - `toolchest/deploymentTools/*.btx` (8 category files)
2. Parse each BTX XML structure
3. Extract all icon definitions (subject names, visual data, metadata)
4. Decompress zlib-compressed icon data (hex strings starting with "789c")
5. Build icon reference dictionary: `{subject_name: icon_visual_data}`
6. Cache in memory for fast annotation replacement

**Technical Details:**
- BTX format: UTF-8 XML files with zlib-compressed binary data
- XML parsing: lxml or xml.etree.ElementTree
- Decompression: Python zlib library for hex→binary→decompressed data
- Icon data: Colors, line weights, shapes, labels, embedded images
- Lookup: O(1) dictionary access by subject name
- Error handling: Log warnings for icons not found in BTX files

### Feature 6: Annotation Replacement Engine

**Purpose:** Replace bid icon annotations with deployment icon annotations while preserving coordinates and sizing

**Components:**
- AnnotationReplacer service
- Annotation deletion (remove bid annotation completely)
- Annotation insertion (add deployment annotation at same coords)
- Size preservation (deployment icon same size as bid icon)
- Subject and visual appearance replacement

**Replacement Flow:**
1. For each annotation extracted from PDF:
   - Extract bid icon subject (e.g., "AP_Bid")
   - Look up bid subject in mapping.md → find deployment subject (e.g., "AP_Deploy")
   - Look up deployment icon visual data in BTX reference
   - Delete bid annotation entirely (remove from PDF annotation array)
   - Create new deployment annotation with:
     - Same X, Y coordinates as bid annotation
     - Same width and height as bid annotation
     - Deployment icon subject name
     - Deployment icon visual appearance (color, shape, label)
   - Insert deployment annotation into PDF at original position
2. Repeat for all annotations in PDF

**Technical Details:**
- Coordinate preservation: Copy exact (x, y) position from bid annotation
- Size preservation: Copy exact width/height from bid annotation
- Subject replacement: Change `/Subj` field from bid subject to deployment subject
- Visual replacement: Update annotation appearance stream with deployment icon data
- Atomic operation: All annotations replaced in single pass
- Error handling: Skip annotations that don't have mapping; log warnings

### Feature 7: PDF Reconstruction

**Purpose:** Rebuild PDF file with all converted annotations and prepare for download

**Components:**
- PDFReconstructor service
- PDF writer to save modified PDF
- File validation (ensure output PDF is valid)
- Naming convention for converted files
- Temporary storage for download

**Reconstruction Flow:**
1. Take modified PDF object with replaced annotations
2. Write PDF to temporary file in backend/data/temp/
3. Name file: `{original_filename}_deployment.pdf`
4. Validate output PDF (can be opened, all pages intact)
5. Return file_id for download endpoint
6. Schedule cleanup after 1 hour

**Technical Details:**
- PDF writing: Use same library as parsing (PyPDF2/pypdf/pdfplumber)
- File naming: Preserve original filename, append `_deployment` suffix
- Storage: backend/data/temp/{uuid}_deployment.pdf
- Validation: Attempt to reopen PDF, check page count matches input
- Cleanup: Background task removes temp files after 1 hour
- File streaming: FastAPI FileResponse for download

### Feature 8: Progress Tracking & User Feedback

**Purpose:** Provide real-time feedback during PDF processing

**Components:**
- Progress indicator showing current processing step
- Status messages for each phase (uploading, parsing, converting, downloading)
- Success notification with download button
- Error messages with actionable guidance

**Processing Steps Displayed:**
1. "Uploading PDF..." (file upload in progress)
2. "Parsing annotations..." (extracting icon markups from PDF)
3. "Converting icons..." (replacing bid → deployment annotations)
4. "Preparing download..." (reconstructing PDF)
5. "Conversion complete!" (show download button)

**Technical Details:**
- Frontend: React state updates with progress status
- Backend: Synchronous processing (FastAPI endpoint completes before returning)
- Progress: Frontend shows spinner with current step description
- Success state: Display download button + success message
- Error state: Display error message + retry button
- No WebSockets needed (MVP uses simple request-response)

### Feature 9: Download Management

**Purpose:** Enable easy retrieval of converted PDF files

**Components:**
- Download button (appears after successful conversion)
- Direct file download via browser
- File naming shows conversion applied
- Option to convert another PDF (reset workflow)

**User Flow:**
1. After conversion completes, "Download Converted PDF" button appears
2. User clicks download button
3. Browser downloads file: `{original_name}_deployment.pdf`
4. User can click "Convert Another PDF" to reset and start over
5. Converted files auto-cleanup after 1 hour

**Technical Details:**
- Download endpoint: GET /api/download/{file_id}
- File streaming: FastAPI FileResponse with appropriate headers
- Content-Disposition: `attachment; filename="{original}_deployment.pdf"`
- Naming: Original filename + `_deployment` suffix
- Cleanup: Background task removes temp files after 1 hour
- Multiple downloads: User can re-download same file within 1 hour window

### Feature 10: Validation & Error Handling

**Purpose:** Ensure robust handling of invalid inputs and edge cases

**Components:**
- PDF structure validation
- Annotation format verification
- Mapping validation (ensure bid subject exists in mapping.md)
- User-friendly error messages
- Detailed error logging for debugging

**Error Scenarios:**
- Invalid PDF → "File is not a valid PDF. Please upload a PDF venue map."
- No annotations found → "No icon markup annotations found in PDF. Please verify you uploaded a marked-up bid map."
- Unknown bid icon subject → "Unknown bid icon found: [subject]. Please verify mapping configuration."
- Multi-page PDF (MVP) → "Multi-page PDFs not yet supported. Please upload a single-page venue map."
- File too large → "PDF file too large (max 50MB). Please reduce file size."
- Corrupted PDF → "Unable to parse PDF structure. File may be corrupted."

**Technical Details:**
- Validation at multiple layers: Upload, Parse, Convert, Reconstruct
- Python exceptions mapped to HTTP status codes (400, 500)
- Frontend error display with clear, actionable messages
- Logging with full context for troubleshooting
- Graceful degradation: Log warnings for unmapped icons but continue processing others

## 8. Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Core programming language |
| FastAPI | 0.104+ | Web framework and API server |
| Pydantic | 2.5+ | Data validation and serialization |
| uvicorn | 0.24+ | ASGI server |
| python-multipart | 0.0.6+ | File upload handling |

### Backend Dependencies

```python
# Core Framework
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pydantic = "^2.5.0"
python-multipart = "^0.0.6"

# PDF Processing
PyPDF2 = "^3.0.0"            # PDF parsing and manipulation (option 1)
# OR pypdf = "^3.17.0"       # Alternative PDF library (option 2)
# OR pdfplumber = "^0.11.0"  # Alternative PDF library (option 3)
# Note: Test all three to determine which works best with Bluebeam PDFs

# BTX Reference File Processing (for toolchest icons)
lxml = "^5.0.0"              # XML parsing for BTX files
# zlib (built-in)            # Compression/decompression for BTX icon data

# Mapping Configuration
markdown = "^3.5.0"          # Parse mapping.md markdown tables
# OR use simple regex parsing (no dependency needed)

# Utilities
python-dotenv = "^1.0.0"     # Environment configuration
aiofiles = "^23.2.0"         # Async file operations
```

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18+ | UI framework |
| TypeScript | 5.0+ | Type-safe JavaScript |
| Vite | 5.0+ | Build tool and dev server |
| TanStack Query | 5.0+ | Server state management |
| Tailwind CSS | 3.4+ | Utility-first CSS framework |

### Frontend Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.0.0",
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.6.0",
    "react-dropzone": "^14.2.0",
    "lucide-react": "^0.300.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

### Development Tools

- **uv** - Fast Python package manager (replaces pip/virtualenv)
- **pytest** - Python testing framework
- **Vitest** - Frontend unit testing
- **ESLint** - JavaScript/TypeScript linting
- **Prettier** - Code formatting

### Optional Dependencies

- **python-magic** - Advanced file type detection (if basic PDF magic number check insufficient)
- **Pillow** - Image processing if icon visual data requires format conversion
- **reportlab** - Alternative PDF manipulation library if PyPDF2/pypdf/pdfplumber insufficient
- **PyMuPDF (fitz)** - High-performance PDF library for complex annotation manipulation

## 9. Security & Configuration

### Security Scope

**✅ In Scope for MVP:**
- File type validation to prevent malicious uploads (PDF magic number check)
- File size limits to prevent DoS (max 50MB for PDFs)
- Input sanitization for all API parameters
- Temporary file cleanup to prevent disk exhaustion (1-hour retention)
- Safe PDF parsing (disable JavaScript execution in PDFs)
- Safe XML parsing for BTX reference files (disable external entity resolution)
- CORS configuration for frontend/backend communication

**❌ Out of Scope:**
- User authentication and authorization
- Rate limiting and API throttling
- Audit logging of user actions
- Encryption at rest
- Network security (SSL/TLS) - handled at deployment

### Configuration Management

**Environment Variables:**

```bash
# Backend (.env)
APP_ENV=development                    # development | production
DEBUG=true                             # Enable debug logging
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173    # Frontend URL

# File Processing
MAX_FILE_SIZE_MB=10                   # Max BTX file size
MAX_FILES_PER_BATCH=5                 # Max files per upload
TEMP_FILE_RETENTION_HOURS=1           # Auto-cleanup time
UPLOAD_DIR=./tmp/uploads              # Temporary storage path
OUTPUT_DIR=./tmp/converted            # Converted files path

# Logging
LOG_LEVEL=INFO                        # DEBUG | INFO | WARNING | ERROR
LOG_FILE=./logs/app.log              # Log file path
```

**Frontend Configuration:**

```typescript
// src/config.ts
export const config = {
  apiBaseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  maxFileSize: 10 * 1024 * 1024,      // 10MB
  maxFilesPerBatch: 5,
  supportedExtensions: ['.btx'],
  pollingInterval: 1000,               // Progress polling (ms)
};
```

### Deployment Considerations

**Local Development:**
- Both frontend and backend run on localhost
- No SSL required
- CORS configured for local ports

**Production Deployment (Future):**
- Reverse proxy (nginx) for SSL termination
- Environment-specific configuration files
- Centralized logging
- Health check endpoints

## 10. API Specification

### Base URL

```
Development: http://localhost:8000/api
Production: https://pdf-converter.example.com/api
```

### Authentication

None required for MVP (internal tool, all endpoints publicly accessible on local network)

---

### Endpoint 1: Upload PDF

**POST** `/api/upload`

Upload a single PDF venue map (bid or deployment map) for conversion.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Form data with single PDF file

```http
POST /api/upload HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="ArenaBidMap.pdf"
Content-Type: application/pdf

[binary PDF file content]
------WebKitFormBoundary--
```

**Response (200 OK):**

```json
{
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_name": "ArenaBidMap.pdf",
  "file_size": 4325760,
  "status": "uploaded",
  "page_count": 1,
  "annotation_count": 75,
  "message": "PDF uploaded successfully"
}
```

**Error Responses:**

**400 Bad Request** (Invalid file type):
```json
{
  "detail": "File is not a valid PDF. Please upload a PDF venue map.",
  "error_code": "INVALID_FILE_TYPE"
}
```

**400 Bad Request** (File too large):
```json
{
  "detail": "PDF file too large (max 50MB). Please reduce file size.",
  "error_code": "FILE_TOO_LARGE"
}
```

**400 Bad Request** (Multi-page PDF):
```json
{
  "detail": "Multi-page PDFs not yet supported. Please upload a single-page venue map.",
  "error_code": "MULTI_PAGE_NOT_SUPPORTED"
}
```

**400 Bad Request** (No annotations):
```json
{
  "detail": "No icon markup annotations found in PDF. Please verify you uploaded a marked-up bid map.",
  "error_code": "NO_ANNOTATIONS_FOUND"
}
```

---

### Endpoint 2: Convert PDF

**POST** `/api/convert/{upload_id}`

Convert PDF annotations from bid icons to deployment icons (or reverse).

**Path Parameters:**
- `upload_id` (string, required): Upload session UUID from upload endpoint

**Request Body:**
```json
{
  "direction": "bid_to_deployment"
}
```

**Direction Parameter:**
- `"bid_to_deployment"` - Convert bid map to deployment map (MVP)
- `"deployment_to_bid"` - Convert deployment map to bid map (Phase 2, currently returns 400)

**Response (200 OK):**

```json
{
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_id": "660e8400-e29b-41d4-a716-446655440099",
  "status": "success",
  "original_file": "ArenaBidMap.pdf",
  "converted_file": "ArenaBidMap_deployment.pdf",
  "direction": "bid_to_deployment",
  "annotations_processed": 75,
  "annotations_converted": 73,
  "annotations_skipped": 2,
  "skipped_subjects": ["Unknown_Icon_1", "Test_Marker"],
  "processing_time_ms": 2340,
  "download_url": "/api/download/660e8400-e29b-41d4-a716-446655440099",
  "message": "Conversion completed successfully"
}
```

**Error Responses:**

**400 Bad Request** (Invalid direction):
```json
{
  "detail": "Invalid conversion direction. MVP supports 'bid_to_deployment' only.",
  "error_code": "INVALID_DIRECTION"
}
```

**404 Not Found** (Upload not found):
```json
{
  "detail": "Upload session not found or expired.",
  "error_code": "UPLOAD_NOT_FOUND"
}
```

**500 Internal Server Error** (Conversion failed):
```json
{
  "detail": "Conversion failed: Unable to parse PDF annotations.",
  "error_code": "CONVERSION_ERROR",
  "file_name": "ArenaBidMap.pdf"
}
```

**500 Internal Server Error** (Mapping error):
```json
{
  "detail": "Unknown bid icon subject: AP_Custom. Please verify mapping configuration.",
  "error_code": "MAPPING_ERROR",
  "unknown_subject": "AP_Custom"
}
```

---

### Endpoint 3: Download Converted PDF

**GET** `/api/download/{file_id}`

Download the converted PDF file.

**Path Parameters:**
- `file_id` (string, required): Converted file UUID from convert endpoint

**Response (200 OK):**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="ArenaBidMap_deployment.pdf"`
- Body: Binary PDF file content

**Error Response (404 Not Found):**

```json
{
  "detail": "Converted file not found or expired (files expire after 1 hour).",
  "error_code": "FILE_NOT_FOUND"
}
```

---

### Endpoint 4: Health Check

**GET** `/health`

Check API health status and verify mapping configuration is loaded.

**Response (200 OK):**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-29T10:30:00Z",
  "mapping_loaded": true,
  "mapping_count": 45,
  "toolchest_bid_icons": 45,
  "toolchest_deployment_icons": 45
}
```

**Response (503 Service Unavailable):**

```json
{
  "status": "unhealthy",
  "version": "1.0.0",
  "timestamp": "2026-01-29T10:30:00Z",
  "error": "mapping.md file not found or invalid",
  "mapping_loaded": false
}
```

---

### Common Response Fields

All endpoints include these fields in error responses:
- `detail` (string): Human-readable error message
- `error_code` (string): Machine-readable error code for programmatic handling

All successful responses include:
- `message` (string): Human-readable success message (optional)

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 OK | Request successful |
| 400 Bad Request | Invalid input (file type, size, parameters) |
| 404 Not Found | Resource not found (upload_id, file_id) |
| 500 Internal Server Error | Server-side processing error |
| 503 Service Unavailable | Service configuration invalid (mapping.md missing) |

### File Retention Policy

- Uploaded PDFs: Retained for 1 hour after upload
- Converted PDFs: Retained for 1 hour after conversion
- Automatic cleanup: Background task removes expired files every 15 minutes

### API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 11. Success Criteria

### MVP Success Definition

The MVP will be considered successful when internal estimators and project managers can convert BTX files in under 1 minute per batch with zero manual XML editing required, achieving 95%+ conversion accuracy across all standard icon sets.

### Functional Requirements

**Core Functionality:**
- ✅ Users can upload 1-5 BTX files via drag-and-drop or file browser
- ✅ System validates BTX file structure and displays clear errors for invalid files
- ✅ Users can preview all icon mappings before conversion with visual comparison
- ✅ Conversion completes in under 30 seconds for typical file (100-200 KB)
- ✅ Users can download individual converted files or batch ZIP
- ✅ Converted BTX files import successfully into Bluebeam Revu without errors
- ✅ All non-icon BTX metadata preserved exactly (tool properties, colors, settings)

**Quality Indicators:**
- ✅ 95%+ icon mapping accuracy (manual QA on sample files)
- ✅ Zero file corruption (all converted files pass Bluebeam validation)
- ✅ Consistent output (identical input produces identical output)
- ✅ Error rate < 5% for valid BTX files
- ✅ Processing speed: < 10 seconds per file for 90% of conversions

**User Experience Goals:**
- ✅ First-time users can complete a conversion without instructions
- ✅ Progress indicators provide clear feedback during all operations
- ✅ Error messages are actionable (explain what's wrong and what to do)
- ✅ UI is responsive and works on 1920x1080 and 1366x768 displays
- ✅ No training documentation required for basic usage

**Technical Requirements:**
- ✅ Backend API responds in < 200ms for non-conversion endpoints
- ✅ Frontend loads in < 3 seconds on typical network
- ✅ System handles concurrent uploads from 2-3 users
- ✅ Automated tests cover 80%+ of backend code
- ✅ Zero security vulnerabilities in dependencies

## 12. Implementation Phases

### Phase 1: Backend PDF Processing Foundation (Weeks 1-2)

**Goal:** Build PDF parsing, annotation extraction, and BTX reference loading

**Deliverables:**
- ✅ FastAPI project structure with proper configuration
- ✅ PDFAnnotationParser service (test PyPDF2, pypdf, pdfplumber)
- ✅ Annotation coordinate and subject extraction
- ✅ Hex→string translation for subject names (if needed)
- ✅ mapping.md parser (markdown table → dictionary)
- ✅ BTXReferenceLoader for toolchest BTX files (XML + zlib decompression)
- ✅ Unit tests for PDF parsing with sample BidMap.pdf
- ✅ Error handling for invalid PDFs, missing annotations

**Validation Criteria:**
- Successfully parses samples/maps/BidMap.pdf and extracts all 75+ annotations
- Extracts subject names correctly (handles hex encoding if present)
- Loads mapping.md and creates bid→deployment lookup dictionary
- Loads toolchest BTX files and extracts icon visual data
- All unit tests pass with 80%+ code coverage
- Handles edge cases (corrupted PDFs, missing subjects) gracefully

---

### Phase 2: Annotation Replacement & PDF Reconstruction (Week 3)

**Goal:** Implement bid→deployment annotation replacement and PDF writing

**Deliverables:**
- ✅ AnnotationReplacer service that replaces bid annotations with deployment annotations
- ✅ Coordinate preservation (exact x, y position)
- ✅ Size preservation (deployment icon matches bid icon dimensions)
- ✅ Subject and visual appearance replacement
- ✅ PDFReconstructor service to write modified PDF
- ✅ Integration tests for full conversion pipeline (upload → convert → download)
- ✅ Validation that converted PDFs open correctly in Bluebeam Revu

**Validation Criteria:**
- Successfully converts samples/maps/BidMap.pdf to deployment map
- Converted PDF opens in Bluebeam Revu without errors
- All annotation coordinates exactly match original positions
- Deployment icons are same size as bid icons
- Subject names and visual appearances correctly updated
- Conversion is deterministic (same input = same output every time)
- Integration tests verify end-to-end PDF conversion

---

### Phase 3: API Layer & File Management (Week 4)

**Goal:** Build REST API with upload, convert, download, and health check endpoints

**Deliverables:**
- ✅ Upload endpoint (POST /api/upload) with PDF validation
- ✅ Convert endpoint (POST /api/convert/{upload_id}) with direction parameter
- ✅ Download endpoint (GET /api/download/{file_id}) for converted PDFs
- ✅ Health check endpoint (GET /health) with mapping validation
- ✅ Temporary file storage and cleanup (1-hour retention)
- ✅ Background task for expired file cleanup
- ✅ Comprehensive error handling and logging
- ✅ API documentation with FastAPI OpenAPI (Swagger/ReDoc)

**Validation Criteria:**
- All 4 API endpoints return appropriate status codes and error messages
- File upload validates PDF type, size, and annotation presence
- Convert endpoint processes bid→deployment correctly (deployment→bid returns 400)
- Download endpoint streams PDF files correctly
- Health check verifies mapping.md is loaded
- Temporary files cleaned up after 1 hour
- API documentation is complete and accurate
- Postman/curl tests pass for all endpoints

---

### Phase 4: Frontend & End-to-End Testing (Weeks 5-6)

**Goal:** Build simple React UI and complete end-to-end testing

**Deliverables:**
- ✅ React project structure with TypeScript and Tailwind
- ✅ PDF upload component with drag-and-drop (DropZone.tsx)
- ✅ Conversion direction selector (DirectionPicker.tsx, bid→deployment only)
- ✅ Progress indicator showing conversion steps (ProgressBar.tsx)
- ✅ Download button for converted PDF (DownloadButton.tsx)
- ✅ Error display and user notifications
- ✅ Responsive design for desktop use
- ✅ Full end-to-end testing with real user scenarios
- ✅ User acceptance testing with estimators and project managers
- ✅ Performance validation (conversions complete in < 1 minute)
- ✅ Documentation (README, API docs, troubleshooting guide)

**Validation Criteria:**
- UI is clean, simple, and intuitive (matches 3-step workflow)
- Drag-and-drop PDF upload works correctly
- Conversion direction selector displays correctly (deployment→bid grayed out)
- Progress indicator updates during conversion process
- Download button appears after successful conversion
- Error messages are clear and actionable
- Manual testing on Chrome, Firefox, Edge passes
- All 6 user stories pass acceptance testing
- Conversions complete in under 1 minute for typical venue maps (75+ annotations)
- Real users complete conversions without assistance
- No critical or high-priority bugs remain
- Documentation is clear and complete

## 13. Future Considerations

### Post-MVP Enhancements

**Custom Mapping Rules:**
- User-defined icon mappings for non-standard toolsets
- Mapping template library for different project types
- Import/export mapping configurations

**Advanced Conversion Options:**
- Reverse conversion (deployment → bid icons)
- Selective icon conversion (choose which icons to convert)
- Batch conversion with different mapping rules per file
- Preview mode with manual override for specific icons

**Icon Library Management:**
- Browse and search available bid/deployment icons
- Upload custom icon sets
- Icon versioning and history
- Visual icon editor for modifications

**Workflow Integration:**
- Bluebeam Revu plugin for direct in-app conversion
- Watch folder for automatic conversion of new BTX files
- Command-line interface for scripted workflows
- Integration with project management tools

**Collaboration Features:**
- User accounts and authentication
- Share converted files with team members
- Conversion history and audit trail
- Team icon library with shared custom mappings

### Scalability Enhancements

**Performance:**
- Parallel processing for batch conversions
- Caching of frequently converted files
- Optimized icon data extraction and compression
- WebSocket for real-time progress (replace polling)

**Storage:**
- Cloud storage integration (AWS S3, Azure Blob)
- Database persistence for conversion history
- Long-term retention of converted files
- Automatic backup and recovery

**Deployment:**
- Docker containerization for easy deployment
- Multi-user support with resource isolation
- Load balancing for high-traffic scenarios
- Monitoring and alerting (Prometheus, Grafana)

## 14. Risks & Mitigations

### Risk 1: BTX Format Changes

**Risk:** Bluebeam updates BTX file format in future versions, breaking parsing logic

**Impact:** High — System unable to process new BTX files
**Likelihood:** Medium — Bluebeam has updated formats historically

**Mitigation:**
- Build parser with version detection and format validation
- Maintain sample files from multiple Bluebeam versions for testing
- Log detailed parsing errors to identify format changes early
- Design parser with extensibility for future format variations
- Monitor Bluebeam release notes and community forums for format updates

---

### Risk 2: Icon Mapping Accuracy

**Risk:** Automated icon matching produces incorrect bid → deployment mappings

**Impact:** High — Incorrect conversions require manual fixing (defeats purpose)
**Likelihood:** Medium — Some icon names may not follow consistent patterns

**Mitigation:**
- Develop comprehensive mapping table based on all sample files
- Implement confidence scoring for matches with manual review for low confidence
- Provide preview functionality so users verify before conversion
- Build validation tests comparing converted files to known-good conversions
- Allow user feedback on incorrect mappings to improve algorithm

---

### Risk 3: File Corruption During Conversion

**Risk:** XML reconstruction or compression errors corrupt output BTX files

**Impact:** Critical — Users cannot use converted files, lose trust in tool
**Likelihood:** Low — Structured process with validation, but possible

**Mitigation:**
- Implement atomic file operations (write to temp, validate, then move)
- Add post-conversion validation (parse converted file, check structure)
- Never modify original uploaded files (always work on copies)
- Extensive automated testing with edge cases and malformed inputs
- Provide rollback mechanism (keep original files accessible)

---

### Risk 4: Performance Bottlenecks with Large Files

**Risk:** Large BTX files (5-10 MB) or complex icon sets cause slow conversions

**Impact:** Medium — User experience degrades, timeouts possible
**Likelihood:** Low — Most BTX files are < 1 MB, but some may be larger

**Mitigation:**
- Profile parsing and conversion code to identify bottlenecks
- Implement streaming for large file processing (avoid loading entire file)
- Set reasonable timeouts with clear progress indicators
- Optimize zlib decompression and XML parsing
- If needed, implement async processing with job queue for very large files

---

### Risk 5: Limited Testing Coverage

**Risk:** Edge cases or rare BTX variants not covered in testing

**Impact:** Medium — Some files fail conversion unexpectedly in production
**Likelihood:** Medium — Cannot test every possible BTX file variation

**Mitigation:**
- Collect diverse sample BTX files from multiple projects and time periods
- Implement comprehensive error handling with detailed logging
- Build validation testing with known-good conversions
- User acceptance testing with real production files
- Post-launch monitoring with user feedback loop for failed conversions
- Design for graceful degradation (partial conversion better than total failure)

## 15. Appendix

### Related Documents

- [Bluebeam Project Plan](bluebeamPlan.md) — Technical approach and research findings
- [README.md](README.md) — Setup instructions and project overview
- Sample Icon Maps:
  - [BidMap.pdf](samples/maps/BidMap.pdf) — Visual reference for bid icons
  - [DeploymentMap.pdf](samples/maps/DeploymentMap.pdf) — Visual reference for deployment icons

### Key Dependencies

- [FastAPI Documentation](https://fastapi.tiangolo.com/) — Web framework
- [React Documentation](https://react.dev/) — Frontend framework
- [Bluebeam Community Forums](https://community.bluebeam.com/) — BTX file format discussions
- [Python lxml](https://lxml.de/) — XML parsing library
- [Python zlib](https://docs.python.org/3/library/zlib.html) — Compression library

### Sample BTX Files

Located in `toolchest/` directory:
- CDS Bluebeam Access Points [01-01-2026].btx
- CDS Bluebeam Bid Tools [01-21-2026].btx
- CDS Bluebeam Cables [08-22-2025].btx
- CDS Bluebeam Hardlines [01-01-2026].btx
- CDS Bluebeam Hardware [01-01-2026].btx
- CDS Bluebeam IoT [01-01-2026].btx
- CDS Bluebeam Miscellaneous [01-01-2026].btx
- CDS Bluebeam Point-to-Points [01-01-2026].btx
- CDS Bluebeam Switches [01-01-2026].btx

### Repository Structure

```
c:\Users\zchrist\Documents\aiSync\PROJECTS\Bluebeam Conversion\
├── backend/           (To be created in Phase 1)
├── frontend/          (To be created in Phase 4)
├── toolchest/         (Existing BTX samples)
├── samples/           (Existing icon samples and maps)
├── .claude/           (Claude Code commands)
├── bluebeamPlan.md    (Project plan document)
├── PRD.md             (This document)
└── README.md          (Project README)
```

---

**Document Status:** Draft v1.0
**Next Steps:** Review PRD with stakeholders, gather feedback, refine MVP scope
**Approval Required From:** Project lead, primary users (estimators/project managers)

