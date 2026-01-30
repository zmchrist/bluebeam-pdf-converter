# Feature: PDF Annotation Parsing Implementation

The following plan should be complete, but it's important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils, types, and models. Import from the right files, etc.

## Feature Description

Implement the PDF annotation parsing foundation for the Bluebeam PDF Map Converter. This feature enables extracting markup annotations (icon stamps) from Bluebeam-generated PDF venue maps, including their coordinates, sizes, and subject names. This is the critical foundation for the bid→deployment icon conversion workflow.

## User Story

As a project estimator
I want to upload a bid map PDF and have the system automatically identify all icon markup annotations
So that the system can convert them to deployment icons without manual re-marking of 75+ equipment locations

## Problem Statement

Users currently spend 2-4 hours manually replacing bid icons with deployment icons on PDF venue maps after winning a bid. To automate this process, the system must first be able to:
1. Parse Bluebeam PDF files and extract annotation data
2. Extract subject names from annotations (handling hex encoding if present)
3. Validate PDF files meet MVP requirements (single page, has annotations)

## Solution Statement

Implement three core services:
1. **PDFAnnotationParser** - Extract annotations from PDF files using PyPDF2/pypdf
2. **SubjectExtractor** - Handle subject name extraction and hex decoding
3. **MappingParser** - Parse the mapping.md configuration file

Create the mapping.md file and temp directory, then implement unit tests to validate the parsing works with the sample BidMap.pdf.

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: Medium
**Primary Systems Affected**: backend/app/services/, backend/app/utils/, backend/data/
**Dependencies**: PyPDF2 (already in pyproject.toml), pypdf (to be evaluated)

---

## CONTEXT REFERENCES

### Relevant Codebase Files - IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

- `backend/app/services/pdf_parser.py` - Service stub to implement (lines 1-73)
- `backend/app/services/subject_extractor.py` - Service stub to implement (lines 1-42)
- `backend/app/services/mapping_parser.py` - Service stub to implement (lines 1-69)
- `backend/app/models/annotation.py` - Data models for annotations (lines 1-33)
- `backend/app/models/mapping.py` - Data models for mappings (lines 1-29)
- `backend/app/utils/errors.py` - Custom exception classes (lines 1-85)
- `backend/app/utils/validation.py` - Validation utilities (stub)
- `backend/app/config.py` - Settings including file paths (lines 1-42)
- `.claude/reference/pdf-processing-best-practices.md` - PDF parsing patterns and examples
- `.claude/reference/testing-and-logging.md` - Testing patterns for pytest

### New Files to Create

- `backend/data/mapping.md` - Icon mapping configuration (markdown table)
- `backend/data/temp/.gitkeep` - Ensure temp directory exists in git

### Relevant Documentation - YOU SHOULD READ THESE BEFORE IMPLEMENTING!

- [PyPDF2 Reading Annotations](https://pypdf2.readthedocs.io/en/3.0.0/user/reading-pdf-annotations.html)
  - Section: Extracting annotations from PDF pages
  - Why: Core API for annotation extraction
- [pypdf Documentation](https://pypdf.readthedocs.io/)
  - Section: Annotations
  - Why: Modern fork with better annotation support (evaluate as alternative)
- [PDF Reference - Annotation Types](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf)
  - Section: 12.5 Annotations
  - Why: Understanding /Rect, /Subj, /Subtype fields

### Patterns to Follow

**Service Layer Pattern** (from existing codebase):
```python
class PDFAnnotationParser:
    """Service for parsing PDF files and extracting annotation data."""

    def __init__(self):
        """Initialize PDF parser."""
        pass

    def parse_pdf(self, pdf_path: Path) -> list[Annotation]:
        """Extract all annotations from PDF."""
        ...
```

**Error Handling Pattern** (from `utils/errors.py`):
```python
from app.utils.errors import InvalidFileTypeError, NoAnnotationsFoundError, MultiPagePDFError

# Raise appropriate custom exceptions
if not is_valid_pdf:
    raise InvalidFileTypeError("File is not a valid PDF")
```

**Model Usage Pattern** (from `models/annotation.py`):
```python
from app.models.annotation import Annotation, AnnotationCoordinates

# Create annotation objects
coords = AnnotationCoordinates(x=100.0, y=200.0, width=50.0, height=50.0, page=1)
annotation = Annotation(subject="AP_Bid", coordinates=coords, annotation_type="/Stamp")
```

**Configuration Access Pattern** (from `config.py`):
```python
from app.config import settings

mapping_file = settings.mapping_file  # Path to mapping.md
temp_dir = settings.temp_dir          # Path to temp directory
```

---

## IMPLEMENTATION PLAN

### Phase 1: Infrastructure Setup

Create the mapping.md configuration file and temp directory structure. These are prerequisites for the parsing services.

**Tasks:**
- Create `backend/data/mapping.md` with icon mapping table
- Create `backend/data/temp/` directory with `.gitkeep`
- Update `.gitignore` to exclude temp files but keep `.gitkeep`

### Phase 2: SubjectExtractor Service

Implement the subject extraction and hex decoding service. This is a dependency for the PDF parser.

**Tasks:**
- Implement `extract_subject()` method
- Implement `translate_hex_subject()` method
- Implement `is_hex_encoded()` helper method
- Add unit tests for subject extraction

### Phase 3: MappingParser Service

Implement the mapping.md parser to load bid→deployment icon mappings.

**Tasks:**
- Implement `load_mappings()` method to parse markdown table
- Implement `get_deployment_subject()` lookup method
- Implement `validate_mappings()` method
- Add unit tests for mapping parsing

### Phase 4: PDFAnnotationParser Service

Implement the core PDF parsing service using PyPDF2/pypdf.

**Tasks:**
- Implement `validate_pdf()` method (magic number check)
- Implement `get_page_count()` method
- Implement `parse_pdf()` method to extract annotations
- Handle coordinate extraction from /Rect field
- Handle subject extraction (integrate SubjectExtractor)
- Add unit tests with sample BidMap.pdf

### Phase 5: Validation Utilities

Implement validation utilities for PDF files.

**Tasks:**
- Implement `validate_pdf_file()` function
- Implement `validate_file_size()` function
- Implement `validate_conversion_direction()` function

---

## STEP-BY-STEP TASKS

IMPORTANT: Execute every task in order, top to bottom. Each task is atomic and independently testable.

### Task 1: CREATE backend/data/mapping.md

Create the icon mapping configuration file with initial bid→deployment mappings.

- **IMPLEMENT**: Markdown table with columns: Bid Icon Subject | Deployment Icon Subject | Category
- **FORMAT**: Standard markdown table with header row and separator
- **CONTENT**: Add sample mappings based on toolchest BTX file subjects (examine BTX files for actual subject names)
- **GOTCHA**: Must skip header row and separator when parsing (rows 0 and 1)
- **VALIDATE**: `cat backend/data/mapping.md` (file exists and has valid format)

**Sample Content:**
```markdown
| Bid Icon Subject | Deployment Icon Subject | Category |
|------------------|------------------------|----------|
| AP_Bid | AP_Deployment | Access Points |
| Switch_Bid | Switch_Deployment | Switches |
```

### Task 2: CREATE backend/data/temp/.gitkeep

Create the temp directory for file storage.

- **IMPLEMENT**: Create empty `.gitkeep` file in temp directory
- **PURPOSE**: Ensure temp directory exists in git but files are ignored
- **VALIDATE**: `ls backend/data/temp/.gitkeep` (file exists)

### Task 3: UPDATE .gitignore

Ensure temp files are ignored but directory structure is preserved.

- **IMPLEMENT**: Add `backend/data/temp/*` and `!backend/data/temp/.gitkeep`
- **PATTERN**: Follow existing gitignore patterns in file
- **GOTCHA**: Don't duplicate existing entries
- **VALIDATE**: `cat .gitignore | grep temp` (patterns exist)

### Task 4: UPDATE backend/app/services/subject_extractor.py

Implement the SubjectExtractor service for extracting and decoding subject names.

- **IMPLEMENT**: Full implementation of `extract_subject()`, `translate_hex_subject()`, `is_hex_encoded()`
- **PATTERN**: Use static methods for utility functions
- **IMPORTS**: No external imports needed (pure Python)
- **GOTCHA**: UTF-16-BE decoding may include null bytes - remove them
- **GOTCHA**: Not all hex-looking strings are actually hex-encoded - validate properly
- **VALIDATE**: `cd backend && uv run python -c "from app.services.subject_extractor import SubjectExtractor; print(SubjectExtractor().translate_hex_subject('4150'))"`

**Implementation Details:**
```python
@staticmethod
def is_hex_encoded(subject: str) -> bool:
    """Check if subject string is hex-encoded."""
    if len(subject) % 2 != 0:
        return False
    try:
        int(subject, 16)
        return len(subject) >= 4  # Reasonable minimum for hex subject
    except ValueError:
        return False

def translate_hex_subject(self, hex_subject: str) -> str:
    """Decode hex to string, trying UTF-16-BE then UTF-8."""
    try:
        bytes_data = bytes.fromhex(hex_subject)
        # Try UTF-16-BE (common in PDF)
        try:
            decoded = bytes_data.decode('utf-16-be')
            return decoded.replace('\x00', '')
        except UnicodeDecodeError:
            pass
        # Try UTF-8 fallback
        try:
            return bytes_data.decode('utf-8')
        except UnicodeDecodeError:
            pass
        return hex_subject
    except Exception:
        return hex_subject
```

### Task 5: UPDATE backend/tests/test_subject_extractor.py

Add comprehensive unit tests for SubjectExtractor.

- **IMPLEMENT**: Tests for plain text, hex-encoded, empty, and edge cases
- **PATTERN**: Mirror existing test structure in `tests/test_pdf_parser.py`
- **IMPORTS**: `from app.services.subject_extractor import SubjectExtractor`
- **GOTCHA**: Remove `pytest.skip()` from existing stub tests
- **VALIDATE**: `cd backend && uv run pytest tests/test_subject_extractor.py -v`

**Test Cases:**
```python
def test_extract_plain_text_subject(self):
    result = self.extractor.extract_subject({"subject": "AP_Bid"})
    assert result == "AP_Bid"

def test_extract_hex_encoded_subject(self):
    # "AP" in hex (ASCII)
    result = self.extractor.translate_hex_subject("4150")
    assert result == "AP"

def test_extract_empty_subject(self):
    result = self.extractor.extract_subject({"subject": ""})
    assert result == ""

def test_extract_subject_from_subj_key(self):
    # PDF annotations may use /Subj instead of /Subject
    result = self.extractor.extract_subject({"Subj": "AP_Bid"})
    assert result == "AP_Bid"
```

### Task 6: UPDATE backend/app/services/mapping_parser.py

Implement the MappingParser service.

- **IMPLEMENT**: Full implementation of `load_mappings()`, `get_deployment_subject()`, `validate_mappings()`
- **PATTERN**: Read file with UTF-8 encoding, parse markdown table
- **IMPORTS**: `from app.models.mapping import IconMapping, MappingEntry`
- **GOTCHA**: Skip header row (index 0) and separator row (index 1)
- **GOTCHA**: Handle rows with extra/trailing whitespace
- **VALIDATE**: `cd backend && uv run python -c "from app.services.mapping_parser import MappingParser; from pathlib import Path; p = MappingParser(Path('backend/data/mapping.md')); print(p.load_mappings())"`

**Implementation Pattern:**
```python
def load_mappings(self) -> IconMapping:
    if not self.mapping_file.exists():
        raise FileNotFoundError(f"Mapping file not found: {self.mapping_file}")

    with self.mapping_file.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    # Skip header (line 0) and separator (line 1)
    data_lines = [line.strip() for line in lines[2:] if line.strip()]

    for line in data_lines:
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 4:  # |bid|deploy|cat| = 4+ parts
            bid_subject = parts[1]
            deployment_subject = parts[2]
            category = parts[3]
            if bid_subject and deployment_subject:
                self.mappings[bid_subject] = deployment_subject
                self.categories[bid_subject] = category

    return IconMapping(
        mappings=self.mappings,
        categories=self.categories,
        total_mappings=len(self.mappings)
    )
```

### Task 7: UPDATE backend/tests/test_mapping_parser.py

Add unit tests for MappingParser.

- **IMPLEMENT**: Tests for valid parsing, missing file, invalid format
- **PATTERN**: Use pytest fixtures for temp mapping files
- **IMPORTS**: `from app.services.mapping_parser import MappingParser`
- **GOTCHA**: Create temporary mapping files for tests, don't rely on real mapping.md
- **VALIDATE**: `cd backend && uv run pytest tests/test_mapping_parser.py -v`

### Task 8: UPDATE backend/app/utils/validation.py

Implement validation utility functions.

- **IMPLEMENT**: `validate_pdf_file()`, `validate_file_size()`, `validate_conversion_direction()`
- **PATTERN**: Return tuple (bool, str) for validation result and error message
- **IMPORTS**: `from pathlib import Path`
- **GOTCHA**: Check PDF magic bytes (%PDF) not just extension
- **VALIDATE**: `cd backend && uv run python -c "from app.utils.validation import validate_pdf_file; from pathlib import Path; print(validate_pdf_file(Path('samples/maps/BidMap.pdf')))"`

**Implementation:**
```python
def validate_pdf_file(file_path: Path) -> tuple[bool, str]:
    """Validate that file is a valid PDF."""
    if not file_path.exists():
        return False, "File not found"

    with file_path.open("rb") as f:
        header = f.read(4)
        if header != b"%PDF":
            return False, "File is not a valid PDF"

    return True, "Valid"

def validate_file_size(file_size: int, max_size_mb: int = 50) -> tuple[bool, str]:
    """Validate file size is within limits."""
    max_bytes = max_size_mb * 1024 * 1024
    if file_size > max_bytes:
        return False, f"File too large (max {max_size_mb}MB)"
    return True, "Valid"

def validate_conversion_direction(direction: str) -> tuple[bool, str]:
    """Validate conversion direction (MVP: bid_to_deployment only)."""
    if direction == "bid_to_deployment":
        return True, "Valid"
    if direction == "deployment_to_bid":
        return False, "Deployment to bid conversion not yet supported"
    return False, f"Invalid direction: {direction}"
```

### Task 9: UPDATE backend/app/services/pdf_parser.py

Implement the PDFAnnotationParser service.

- **IMPLEMENT**: Full implementation of `parse_pdf()`, `get_page_count()`, `validate_pdf()`
- **PATTERN**: Use pypdf (or PyPDF2) for PDF parsing
- **IMPORTS**: `from pypdf import PdfReader` (or `from PyPDF2 import PdfReader`)
- **IMPORTS**: `from app.models.annotation import Annotation, AnnotationCoordinates`
- **IMPORTS**: `from app.services.subject_extractor import SubjectExtractor`
- **IMPORTS**: `from app.utils.errors import InvalidFileTypeError, NoAnnotationsFoundError, MultiPagePDFError`
- **GOTCHA**: Must call `.get_object()` on annotation references in the /Annots array
- **GOTCHA**: Coordinates are in /Rect as [x1, y1, x2, y2] (lower-left, upper-right)
- **GOTCHA**: Subject may be in /Subject or /Subj field
- **VALIDATE**: `cd backend && uv run python -c "from app.services.pdf_parser import PDFAnnotationParser; from pathlib import Path; p = PDFAnnotationParser(); print(len(p.parse_pdf(Path('samples/maps/BidMap.pdf'))))"`

**Implementation Pattern:**
```python
from pypdf import PdfReader
from pathlib import Path
from app.models.annotation import Annotation, AnnotationCoordinates
from app.services.subject_extractor import SubjectExtractor

class PDFAnnotationParser:
    def __init__(self):
        self.subject_extractor = SubjectExtractor()

    def validate_pdf(self, pdf_path: Path) -> bool:
        """Check PDF magic number."""
        try:
            with pdf_path.open("rb") as f:
                header = f.read(4)
                return header == b"%PDF"
        except Exception:
            return False

    def get_page_count(self, pdf_path: Path) -> int:
        reader = PdfReader(pdf_path)
        return len(reader.pages)

    def parse_pdf(self, pdf_path: Path) -> list[Annotation]:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not self.validate_pdf(pdf_path):
            raise InvalidFileTypeError("File is not a valid PDF")

        reader = PdfReader(pdf_path)
        page_count = len(reader.pages)

        # MVP: Single page only
        if page_count > 1:
            raise MultiPagePDFError(f"Multi-page PDFs not supported (found {page_count} pages)")

        annotations = []
        page = reader.pages[0]

        if "/Annots" not in page:
            raise NoAnnotationsFoundError("No annotations found in PDF")

        for annot_ref in page["/Annots"]:
            annot = annot_ref.get_object()

            # Extract subject (try both /Subject and /Subj)
            subject_raw = annot.get("/Subject", annot.get("/Subj", ""))
            subject = self.subject_extractor.extract_subject({"subject": str(subject_raw)})

            # Extract coordinates
            rect = annot.get("/Rect", [])
            if len(rect) >= 4:
                x1, y1, x2, y2 = float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3])
                coords = AnnotationCoordinates(
                    x=x1,
                    y=y1,
                    width=x2 - x1,
                    height=y2 - y1,
                    page=1
                )
            else:
                continue  # Skip annotations without valid rect

            # Extract annotation type
            annot_type = str(annot.get("/Subtype", "/Unknown"))

            annotation = Annotation(
                subject=subject,
                coordinates=coords,
                annotation_type=annot_type,
                raw_data=dict(annot) if hasattr(annot, 'items') else None
            )
            annotations.append(annotation)

        if not annotations:
            raise NoAnnotationsFoundError("No valid annotations found in PDF")

        return annotations
```

### Task 10: UPDATE backend/tests/test_pdf_parser.py

Add comprehensive unit tests for PDFAnnotationParser.

- **IMPLEMENT**: Tests using sample BidMap.pdf
- **PATTERN**: Use `samples/maps/BidMap.pdf` as test fixture
- **IMPORTS**: `from app.services.pdf_parser import PDFAnnotationParser`
- **GOTCHA**: Tests will fail if sample PDF doesn't have expected annotations
- **VALIDATE**: `cd backend && uv run pytest tests/test_pdf_parser.py -v`

**Test Cases:**
```python
from pathlib import Path
import pytest
from app.services.pdf_parser import PDFAnnotationParser
from app.utils.errors import InvalidFileTypeError, NoAnnotationsFoundError

class TestPDFAnnotationParser:
    def setup_method(self):
        self.parser = PDFAnnotationParser()
        self.sample_pdf = Path("samples/maps/BidMap.pdf")

    def test_validate_pdf_with_valid_pdf(self):
        assert self.parser.validate_pdf(self.sample_pdf) is True

    def test_get_page_count(self):
        count = self.parser.get_page_count(self.sample_pdf)
        assert count >= 1

    def test_parse_pdf_extracts_annotations(self):
        annotations = self.parser.parse_pdf(self.sample_pdf)
        assert len(annotations) > 0

    def test_parse_pdf_annotations_have_coordinates(self):
        annotations = self.parser.parse_pdf(self.sample_pdf)
        for annot in annotations:
            assert annot.coordinates is not None
            assert annot.coordinates.width > 0
            assert annot.coordinates.height > 0

    def test_parse_pdf_invalid_file_raises_error(self):
        with pytest.raises(FileNotFoundError):
            self.parser.parse_pdf(Path("nonexistent.pdf"))
```

### Task 11: RUN Full Test Suite

Run all tests to verify the implementation.

- **VALIDATE**: `cd backend && uv run pytest tests/ -v`
- **VALIDATE**: `cd backend && uv run pytest tests/ --cov=app --cov-report=term-missing`

---

## TESTING STRATEGY

### Unit Tests

Based on project patterns in `backend/tests/`:

1. **test_subject_extractor.py**
   - Test plain text extraction
   - Test hex-encoded subject decoding
   - Test empty/null subjects
   - Test both /Subject and /Subj keys

2. **test_mapping_parser.py**
   - Test loading valid mapping.md
   - Test missing file handling
   - Test invalid format handling
   - Test lookup functionality

3. **test_pdf_parser.py**
   - Test PDF validation (magic bytes)
   - Test page count extraction
   - Test annotation extraction from BidMap.pdf
   - Test coordinate parsing
   - Test error handling for invalid PDFs

### Integration Tests

Deferred to Phase 3 (API Layer) - will test full upload→parse→convert workflow.

### Edge Cases

- PDF with no annotations → `NoAnnotationsFoundError`
- Multi-page PDF → `MultiPagePDFError`
- Invalid PDF file → `InvalidFileTypeError`
- Hex-encoded subjects with invalid bytes → Fallback to original string
- Missing /Rect field → Skip annotation
- Empty subject → Empty string (not error)

---

## VALIDATION COMMANDS

Execute every command to ensure zero regressions and 100% feature correctness.

### Level 1: Syntax & Style

```bash
# Check Python syntax
cd backend && uv run python -m py_compile app/services/pdf_parser.py
cd backend && uv run python -m py_compile app/services/subject_extractor.py
cd backend && uv run python -m py_compile app/services/mapping_parser.py
cd backend && uv run python -m py_compile app/utils/validation.py
```

### Level 2: Unit Tests

```bash
# Run all unit tests
cd backend && uv run pytest tests/test_subject_extractor.py -v
cd backend && uv run pytest tests/test_mapping_parser.py -v
cd backend && uv run pytest tests/test_pdf_parser.py -v

# Run with coverage
cd backend && uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

### Level 3: Integration Tests

```bash
# Quick integration check - parse sample PDF
cd backend && uv run python -c "
from app.services.pdf_parser import PDFAnnotationParser
from pathlib import Path
parser = PDFAnnotationParser()
annotations = parser.parse_pdf(Path('samples/maps/BidMap.pdf'))
print(f'Found {len(annotations)} annotations')
for a in annotations[:5]:
    print(f'  - {a.subject}: ({a.coordinates.x}, {a.coordinates.y})')
"
```

### Level 4: Manual Validation

```bash
# Verify mapping.md exists and is valid
cat backend/data/mapping.md

# Verify temp directory exists
ls -la backend/data/temp/

# Check imports work
cd backend && uv run python -c "from app.services.pdf_parser import PDFAnnotationParser; print('OK')"
cd backend && uv run python -c "from app.services.subject_extractor import SubjectExtractor; print('OK')"
cd backend && uv run python -c "from app.services.mapping_parser import MappingParser; print('OK')"
```

---

## ACCEPTANCE CRITERIA

- [x] `backend/data/mapping.md` exists with valid markdown table format
- [x] `backend/data/temp/` directory exists with `.gitkeep`
- [ ] SubjectExtractor correctly extracts plain text subjects
- [ ] SubjectExtractor correctly decodes hex-encoded subjects
- [ ] MappingParser loads mapping.md and returns IconMapping object
- [ ] MappingParser.get_deployment_subject() returns correct mappings
- [ ] PDFAnnotationParser.validate_pdf() correctly identifies PDFs
- [ ] PDFAnnotationParser.parse_pdf() extracts annotations from BidMap.pdf
- [ ] All annotations have valid coordinates (x, y, width, height)
- [ ] All unit tests pass with 80%+ coverage
- [ ] No regressions in existing functionality
- [ ] Custom exceptions raised for error conditions

---

## COMPLETION CHECKLIST

- [ ] All tasks completed in order
- [ ] Each task validation passed immediately
- [ ] All validation commands executed successfully
- [ ] Full test suite passes (unit + integration)
- [ ] No syntax or import errors
- [ ] Manual testing confirms PDF parsing works with BidMap.pdf
- [ ] Acceptance criteria all met
- [ ] Code reviewed for quality and maintainability

---

## NOTES

### Library Choice: pypdf vs PyPDF2

The project currently has PyPDF2 in `pyproject.toml`. Both libraries have nearly identical APIs. The reference documentation recommends **pypdf** for better annotation support.

**Recommendation**: Try PyPDF2 first since it's already installed. If annotation extraction doesn't work well, add pypdf as alternative:
```bash
cd backend && uv add pypdf
```

Then change imports:
```python
# from PyPDF2 import PdfReader
from pypdf import PdfReader
```

### BTX File Subject Discovery

The BTX files in `toolchest/` contain zlib-compressed data. The `<Title>` and other text fields appear to be hex-encoded. When creating `mapping.md`, you'll need to:

1. Parse the BTX XML to extract tool definitions
2. Decode hex-encoded subject names
3. Map bid subjects (from bidTools) to deployment subjects (from deploymentTools)

This BTX parsing will be implemented in Phase 2 (BTXReferenceLoader). For now, create `mapping.md` with placeholder mappings and update later when BTX parsing is complete.

### Sample PDF Analysis

The `samples/maps/BidMap.pdf` file is the primary test fixture. If the PDF has unusual annotation formats, you may need to:

1. Open BidMap.pdf in a PDF viewer to see annotations
2. Use a hex editor or PDF debugging tool to inspect annotation structure
3. Adjust parsing logic based on actual annotation format

### Error Handling Strategy

All errors should be raised as custom exceptions from `utils/errors.py`:
- `InvalidFileTypeError` - Not a valid PDF
- `NoAnnotationsFoundError` - PDF has no markup annotations
- `MultiPagePDFError` - PDF has multiple pages (MVP constraint)
- `MappingNotFoundError` - Subject not in mapping.md (used later in conversion)

This allows the API layer to catch specific exceptions and return appropriate HTTP status codes.
