# Bluebeam PDF Map Converter

A web-based tool that automates the conversion of PDF venue maps from "bid phase" to "deployment phase" by replacing icon annotations.

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, PyMuPDF (fitz), lxml, Pydantic
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, TanStack Query (planned)
- **Testing**: pytest, pytest-asyncio
- **No authentication** - internal single-user tool

## Project Structure

```
bluebeam-pdf-converter/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI entry point
│   │   ├── config.py             # Pydantic settings (paths, limits)
│   │   ├── models/
│   │   │   ├── annotation.py     # Annotation, AnnotationCoordinates
│   │   │   ├── pdf_file.py       # PDFFile, ConversionRequest/Response
│   │   │   └── mapping.py        # MappingEntry, IconMapping, IconData
│   │   ├── services/
│   │   │   ├── pdf_parser.py     # Extract annotations from PDFs
│   │   │   ├── subject_extractor.py  # Decode subject names (hex/UTF)
│   │   │   ├── mapping_parser.py # Parse mapping.md configuration
│   │   │   ├── btx_loader.py     # Load BTX toolchest icon data
│   │   │   ├── annotation_replacer.py # Replace bid→deployment icons
│   │   │   ├── appearance_extractor.py # Extract colors from reference PDFs
│   │   │   ├── icon_config.py    # Config for 39 deployment icons
│   │   │   ├── icon_renderer.py  # Create PDF appearance streams
│   │   │   └── file_manager.py   # Manage uploaded/converted file storage
│   │   ├── routers/
│   │   │   ├── upload.py         # POST /api/upload
│   │   │   ├── convert.py        # POST /api/convert/{upload_id}
│   │   │   └── download.py       # GET /api/download/{file_id}
│   │   └── utils/
│   │       ├── validation.py     # PDF and file validators
│   │       └── errors.py         # Custom exception classes
│   ├── tests/                    # pytest unit/integration tests
│   ├── scripts/                  # Test and utility scripts
│   ├── data/
│   │   └── mapping.md            # Icon mapping configuration (112+ mappings)
│   ├── pyproject.toml            # uv project config
│   └── requirements.txt
├── frontend/                     # React app (not yet implemented)
├── toolchest/
│   ├── bidTools/                 # Bid icon BTX definitions
│   └── deploymentTools/          # Deployment icon BTX files (8 categories)
├── samples/
│   ├── icons/
│   │   ├── bidIcons/
│   │   ├── deploymentIcons/
│   │   └── gearIcons/            # PNG images for icon rendering
│   └── maps/                     # Sample PDFs for testing
├── .claude/
│   ├── PRD.md                    # Product requirements document
│   ├── memories.md               # Session history and notes
│   └── commands/                 # Claude Code command definitions
└── .agents/plans/                # Implementation plans
```

## Commands

```bash
# Backend Setup
cd backend && uv sync

# Run Development Server
uv run uvicorn app.main:app --reload --port 8000

# Run All Tests
cd backend && uv run pytest

# Run Specific Test File
uv run pytest tests/test_icon_renderer.py -v

# Run Tests with Coverage
uv run pytest --cov=app

# Test Icon Rendering (CLI tool)
uv run python scripts/test_icon_render.py "SW - Cisco Micro 4P"

# End-to-End Conversion Test
uv run python scripts/test_conversion.py

# Frontend (when implemented)
cd frontend && npm install && npm run dev
```

## Reference Documentation

Read these documents when working on specific areas:

| Document | When to Read |
|----------|--------------|
| `.claude/PRD.md` | Understanding requirements, features, API spec, architecture |
| `backend/data/mapping.md` | Icon mapping configuration, bid→deployment subject mappings |
| `backend/app/services/icon_config.py` | Icon rendering configuration, categories, overrides |
| `.claude/memories.md` | Recent implementation decisions, technical discoveries |

## Code Conventions

### Backend (Python)
- Use Pydantic models for all data structures
- Separate services for each responsibility (parsing, extraction, replacement)
- Custom exceptions in `utils/errors.py` for error handling
- Type hints throughout with `TYPE_CHECKING` for circular imports
- Path objects (`pathlib.Path`) for file handling
- Configuration via `pydantic_settings.BaseSettings`

### Services Pattern
```python
# Services are initialized with dependencies
replacer = AnnotationReplacer(
    mapping_parser=mapping_parser,
    btx_loader=btx_loader,
    appearance_extractor=appearance_extractor
)
```

### Error Handling
- Custom exception hierarchy with `PDFConverterError` base
- Descriptive error messages for user feedback
- Graceful degradation (skip unmapped icons, continue processing)

```python
from app.utils.errors import InvalidFileTypeError, NoAnnotationsFoundError

try:
    result = parser.parse(pdf_path)
except NoAnnotationsFoundError as e:
    logger.warning("No annotations", error=str(e))
```

### API Design
- RESTful endpoints under `/api/`
- Return 201 for POST, 204 for DELETE
- Use HTTPException with descriptive error codes
- Interactive docs at `/docs` (Swagger) and `/redoc`

### Frontend (React - Planned)
- Feature-based folder structure under `src/features/`
- Use TanStack Query for API calls
- Tailwind CSS for styling
- TypeScript for type safety

## Configuration

Settings are managed via `backend/app/config.py`:

```python
from app.config import settings

# Access settings
settings.max_file_size_mb  # 50 MB default
settings.temp_dir          # Path to temp storage
settings.mapping_file      # Path to mapping.md
settings.toolchest_dir     # Path to BTX files
```

Override with environment variables or `.env` file.

## Data Files

### mapping.md
Icon mapping configuration in markdown table format:
```markdown
| Bid Icon Subject | Deployment Icon Subject | Category |
|------------------|------------------------|----------|
| accessPoints     | AP - Cisco MR36H       | APs      |
```

### BTX Files
Bluebeam toolchest XML files with hex-encoded zlib-compressed icon data:
- `toolchest/bidTools/` - Consolidated bid icons (70 icons)
- `toolchest/deploymentTools/` - Category files (118 deployment icons)

### Gear Icons
PNG images for icon rendering in `samples/icons/gearIcons/`:
- APs/, Switches/, P2Ps/, Hardlines/, Hardware/, Misc/

## Testing Strategy

### Testing Pyramid
- **80% Unit tests**: Service logic, parsing, validation
- **15% Integration tests**: API endpoints with real data
- **5% E2E tests**: Full conversion pipeline

### Test Organization
```
backend/tests/
├── test_pdf_parser.py          # PDF validation, extraction
├── test_subject_extractor.py   # Hex decoding, subject parsing
├── test_mapping_parser.py      # Mapping config loading
├── test_btx_loader.py          # BTX parsing (24 tests)
├── test_annotation_replacer.py # Annotation replacement
├── test_icon_renderer.py       # Appearance streams (24 tests)
├── test_file_manager.py        # File storage (8 tests)
└── test_api.py                 # API endpoint tests (9 tests)
```

### Running Tests
```bash
# All tests
uv run pytest

# Specific file with verbose output
uv run pytest tests/test_icon_renderer.py -v

# With coverage report
uv run pytest --cov=app --cov-report=html
```

## Key Services

### PDFAnnotationParser
Extracts annotations from PDF files using PyPDF2 for initial parsing.

### SubjectExtractor
Decodes subject names handling hex-encoded UTF-8/UTF-16-BE/latin-1 values.

### MappingParser
Parses `mapping.md` for bid→deployment subject mappings (112+ entries).

### BTXReferenceLoader
Loads BTX XML files, decodes zlib-compressed hex data, extracts icon subjects.

### AnnotationReplacer
Replaces bid annotations with deployment annotations using PyMuPDF:
- Preserves exact coordinates and sizing
- Creates visual appearance streams with icon renderer
- Falls back to simple shapes if rendering fails

### IconRenderer
Creates PDF appearance streams for deployment icons:
- Bezier curves for circles
- Embedded PNG gear images
- ID boxes, brand text, model text

### IconConfig
Central configuration for 39 deployment icons:
- `ICON_CATEGORIES`: Subject→category mapping
- `CATEGORY_DEFAULTS`: Rendering parameters per category
- `ICON_OVERRIDES`: Per-icon tuning (offsets, colors)
- `ICON_IMAGE_PATHS`: Subject→PNG file mapping

### FileManager
Manages temporary file storage for uploads and conversions:
- UUID-based file naming
- Expiration tracking (1 hour default)
- Cleanup of expired files

## Implementation Status

**Phase 1-3: ✅ Complete**
- PDF parsing and annotation extraction
- Subject extraction with hex decoding
- Mapping configuration
- BTX file processing
- Annotation replacement with PyMuPDF
- Config-driven icon rendering

**Phase 4 Backend: ✅ Complete**
- FileManager service for upload/download storage
- FastAPI endpoints (upload, convert, download) - all implemented
- Health check with mapping/toolchest validation
- End-to-end conversion via API working (376/402 annotations, ~1 second)

**Phase 4 Frontend: ⏳ Not Started**
- React frontend UI
- Upload/download workflow
