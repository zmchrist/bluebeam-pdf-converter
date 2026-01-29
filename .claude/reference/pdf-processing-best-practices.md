# PDF Processing Best Practices Reference

A concise reference guide for PDF manipulation, Bluebeam annotation handling, and icon conversion workflows.

---

## Table of Contents

1. [PDF Library Comparison](#1-pdf-library-comparison)
2. [PDF Annotation Extraction](#2-pdf-annotation-extraction)
3. [BTX File Processing](#3-btx-file-processing)
4. [Subject Name Extraction & Hex Decoding](#4-subject-name-extraction--hex-decoding)
5. [Annotation Replacement](#5-annotation-replacement)
6. [PDF Reconstruction](#6-pdf-reconstruction)
7. [Mapping Configuration](#7-mapping-configuration)
8. [Error Handling](#8-error-handling)
9. [Performance Optimization](#9-performance-optimization)
10. [Testing Strategies](#10-testing-strategies)

---

## 1. PDF Library Comparison

### Three Options to Evaluate

| Library | Version | Pros | Cons | Best For |
|---------|---------|------|------|----------|
| **PyPDF2** | 3.0.0+ | Mature, widely used, good documentation | Annotation support can be complex | General PDF manipulation |
| **pypdf** | 3.17.0+ | Modern fork of PyPDF2, active development, better annotation API | Relatively newer | Bluebeam PDFs (recommended) |
| **pdfplumber** | 0.11.0+ | Excellent text/table extraction, high-level API | Limited low-level annotation access | Text extraction focus |

### Installation

```bash
# Option 1: PyPDF2
pip install PyPDF2>=3.0.0

# Option 2: pypdf (recommended)
pip install pypdf>=3.17.0

# Option 3: pdfplumber
pip install pdfplumber>=0.11.0
```

### Basic Usage Comparison

**PyPDF2:**
```python
from PyPDF2 import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
page = reader.pages[0]
annotations = page.get("/Annots")
```

**pypdf:**
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
page = reader.pages[0]
if "/Annots" in page:
    annotations = page["/Annots"]
```

**pdfplumber:**
```python
import pdfplumber

with pdfplumber.open("input.pdf") as pdf:
    page = pdf.pages[0]
    # Great for text, limited for annotations
    text = page.extract_text()
```

### Recommendation

Start with **pypdf** for Bluebeam PDFs due to:
- Better annotation handling
- Active maintenance
- Modern Python support
- Compatible with PyPDF2 (easy migration)

---

## 2. PDF Annotation Extraction

### Understanding PDF Annotations

PDF annotations are stored in the `/Annots` array of each page. Each annotation object contains:
- `/Type`: `/Annot`
- `/Subtype`: Type of annotation (`/Stamp`, `/FreeText`, `/Square`, etc.)
- `/Rect`: Coordinates `[x1, y1, x2, y2]`
- `/AP`: Appearance dictionary (contains visual representation)
- `/Contents`: Text content (may be empty for stamps)
- **Bluebeam specific**: `/Subject` or `/Subj` - Icon identifier

### Extract Annotations from PDF

```python
from pypdf import PdfReader
from pathlib import Path

class PDFAnnotationParser:
    def __init__(self, pdf_path: Path):
        self.reader = PdfReader(pdf_path)

    def extract_annotations(self, page_num: int = 0):
        """Extract all annotations from a page."""
        page = self.reader.pages[page_num]

        if "/Annots" not in page:
            return []

        annotations = []
        for annot_ref in page["/Annots"]:
            annot = annot_ref.get_object()

            annotation_data = {
                "type": str(annot.get("/Subtype", "")),
                "rect": annot.get("/Rect", []),
                "subject": annot.get("/Subject", annot.get("/Subj", "")),
                "contents": annot.get("/Contents", ""),
                "appearance": annot.get("/AP"),
                "raw": annot,
            }
            annotations.append(annotation_data)

        return annotations
```

### Parse Coordinates

```python
def parse_annotation_coordinates(rect: list) -> dict:
    """
    Parse PDF rectangle coordinates.
    PDF rect format: [x1, y1, x2, y2] (lower-left, upper-right)
    """
    if len(rect) != 4:
        raise ValueError(f"Invalid rect: {rect}")

    x1, y1, x2, y2 = rect
    return {
        "x": float(x1),
        "y": float(y1),
        "width": float(x2 - x1),
        "height": float(y2 - y1),
    }
```

### Filter by Annotation Type

```python
def filter_stamp_annotations(annotations: list) -> list:
    """Only return stamp/icon annotations."""
    return [
        a for a in annotations
        if a["type"] == "/Stamp" or "Stamp" in a["type"]
    ]
```

---

## 3. BTX File Processing

### BTX File Structure

BTX (Bluebeam Toolchest XML) format:
```xml
<Toolchest version="1.0">
  <Tool>
    <Subject>AP_Bid</Subject>
    <ToolType>Stamp</ToolType>
    <IconData encoding="zlib">[base64-encoded compressed data]</IconData>
    <Color>#FF0000</Color>
    <!-- Other properties -->
  </Tool>
</Toolchest>
```

### Parse BTX Files with lxml

```python
from lxml import etree
import zlib
import base64
from pathlib import Path

class BTXReferenceLoader:
    def __init__(self, toolchest_dir: Path):
        self.toolchest_dir = toolchest_dir
        self.icons = {}

    def load_all_btx_files(self):
        """Load all BTX files from toolchest directory."""
        for btx_file in self.toolchest_dir.rglob("*.btx"):
            self.load_btx_file(btx_file)

    def load_btx_file(self, btx_path: Path):
        """Parse a single BTX file and extract icon data."""
        tree = etree.parse(str(btx_path))
        root = tree.getroot()

        for tool in root.findall(".//Tool"):
            subject = tool.findtext("Subject")
            icon_data_elem = tool.find("IconData")

            if subject and icon_data_elem is not None:
                # Extract and decompress icon data
                encoding = icon_data_elem.get("encoding", "")
                icon_data_b64 = icon_data_elem.text

                if icon_data_b64:
                    icon_data = self.decode_icon_data(icon_data_b64, encoding)
                    self.icons[subject] = {
                        "subject": subject,
                        "icon_data": icon_data,
                        "source_file": btx_path.name,
                    }

    def decode_icon_data(self, data_b64: str, encoding: str) -> bytes:
        """Decode and decompress icon data."""
        # Decode base64
        compressed_data = base64.b64decode(data_b64)

        # Decompress if zlib encoded
        if encoding.lower() == "zlib":
            return zlib.decompress(compressed_data)

        return compressed_data

    def get_icon_data(self, subject: str) -> dict | None:
        """Get icon data by subject name."""
        return self.icons.get(subject)
```

### Load Toolchest on Startup

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

btx_loader = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global btx_loader
    btx_loader = BTXReferenceLoader(Path("toolchest"))
    btx_loader.load_all_btx_files()
    print(f"Loaded {len(btx_loader.icons)} icon definitions")
    yield
    # Shutdown
    btx_loader = None

app = FastAPI(lifespan=lifespan)
```

---

## 4. Subject Name Extraction & Hex Decoding

### Bluebeam Subject Name Formats

Bluebeam may encode subject names in different formats:

1. **Plain text**: `"AP_Bid"`
2. **Hex-encoded**: `"4150005f426964"` (UTF-16 with null bytes)
3. **UTF-8**: `"AP_Bid"` (standard)

### Hex Decoding Implementation

```python
class SubjectExtractor:
    @staticmethod
    def extract_subject(annotation: dict) -> str:
        """Extract and decode subject from annotation."""
        subject = annotation.get("subject", "")

        if not subject:
            return ""

        # Check if hex-encoded
        if SubjectExtractor.is_hex_encoded(subject):
            return SubjectExtractor.decode_hex_subject(subject)

        return subject

    @staticmethod
    def is_hex_encoded(subject: str) -> bool:
        """Check if subject string is hex-encoded."""
        # Hex strings are even length and only contain hex characters
        if len(subject) % 2 != 0:
            return False

        try:
            int(subject, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def decode_hex_subject(hex_string: str) -> str:
        """Decode hex-encoded subject name."""
        try:
            # Convert hex to bytes
            bytes_data = bytes.fromhex(hex_string)

            # Try UTF-16 (with null bytes)
            try:
                decoded = bytes_data.decode('utf-16-be')
                # Remove null bytes
                return decoded.replace('\x00', '')
            except UnicodeDecodeError:
                pass

            # Try UTF-8
            try:
                return bytes_data.decode('utf-8')
            except UnicodeDecodeError:
                pass

            # Fallback: return original
            return hex_string

        except Exception:
            return hex_string
```

### Testing Subject Extraction

```python
def test_subject_extraction():
    # Plain text
    assert SubjectExtractor.extract_subject({"subject": "AP_Bid"}) == "AP_Bid"

    # Hex-encoded UTF-16 (example)
    hex_encoded = "4150005f426964"  # "AP_Bid" in UTF-16
    assert SubjectExtractor.extract_subject({"subject": hex_encoded}) == "AP_Bid"

    # Empty subject
    assert SubjectExtractor.extract_subject({"subject": ""}) == ""
```

---

## 5. Annotation Replacement

### Replacement Strategy

1. **Extract** bid icon annotation (coordinates, subject)
2. **Look up** deployment subject in mapping
3. **Load** deployment icon visual data from BTX
4. **Delete** bid icon annotation from PDF
5. **Create** new deployment icon annotation with:
   - Same coordinates
   - Same size
   - New subject name
   - New appearance (from BTX)

### Create New Annotation

```python
from pypdf import PdfWriter, generic

class AnnotationReplacer:
    def __init__(self, btx_loader: BTXReferenceLoader, mapping: dict):
        self.btx_loader = btx_loader
        self.mapping = mapping

    def replace_annotation(self, page, old_annot, bid_subject: str):
        """Replace bid annotation with deployment annotation."""
        # Look up deployment subject
        deployment_subject = self.mapping.get(bid_subject)
        if not deployment_subject:
            raise ValueError(f"No mapping found for {bid_subject}")

        # Get deployment icon data
        icon_data = self.btx_loader.get_icon_data(deployment_subject)
        if not icon_data:
            raise ValueError(f"No icon data for {deployment_subject}")

        # Preserve coordinates and size
        rect = old_annot.get("/Rect")

        # Create new annotation object
        new_annot = generic.DictionaryObject()
        new_annot.update({
            generic.NameObject("/Type"): generic.NameObject("/Annot"),
            generic.NameObject("/Subtype"): generic.NameObject("/Stamp"),
            generic.NameObject("/Rect"): rect,
            generic.NameObject("/Subject"): generic.create_string_object(deployment_subject),
            # Add appearance dictionary from BTX icon data
            # (implementation depends on BTX icon format)
        })

        return new_annot

    def remove_annotation(self, page, annot_ref):
        """Remove annotation from page."""
        if "/Annots" in page:
            annots = page["/Annots"]
            if annot_ref in annots:
                annots.remove(annot_ref)
```

---

## 6. PDF Reconstruction

### Write Modified PDF

```python
from pypdf import PdfReader, PdfWriter
from pathlib import Path
import uuid

class PDFReconstructor:
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir

    def reconstruct_pdf(
        self,
        input_path: Path,
        original_filename: str,
        annotations_to_replace: list,
    ) -> tuple[str, Path]:
        """Create modified PDF with replaced annotations."""
        reader = PdfReader(input_path)
        writer = PdfWriter()

        # Process each page
        for page_num, page in enumerate(reader.pages):
            # Replace annotations on this page
            for annot_data in annotations_to_replace:
                if annot_data["page"] == page_num:
                    # Replace annotation
                    self.replace_annotation_on_page(page, annot_data)

            writer.add_page(page)

        # Write output PDF
        file_id = str(uuid.uuid4())
        output_filename = f"{Path(original_filename).stem}_deployment.pdf"
        output_path = self.temp_dir / f"{file_id}_{output_filename}"

        with output_path.open("wb") as output_file:
            writer.write(output_file)

        return file_id, output_path

    def validate_output_pdf(self, pdf_path: Path) -> bool:
        """Validate reconstructed PDF."""
        try:
            reader = PdfReader(pdf_path)
            # Check it can be opened and has pages
            return len(reader.pages) > 0
        except Exception:
            return False
```

---

## 7. Mapping Configuration

### Parse mapping.md

The `backend/data/mapping.md` file defines bid ↔ deployment mappings:

```markdown
| Bid Icon Subject | Deployment Icon Subject | Category |
|------------------|------------------------|----------|
| AP_Bid           | AP_Deployment          | Access Points |
| Switch_Bid       | Switch_Deployment      | Network Equipment |
```

### Mapping Parser

```python
from pathlib import Path

class MappingParser:
    def __init__(self, mapping_file: Path):
        self.mapping_file = mapping_file
        self.mappings = {}

    def load_mappings(self) -> dict:
        """Parse mapping.md markdown table."""
        with self.mapping_file.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        # Skip header and separator rows
        data_lines = [line.strip() for line in lines[2:] if line.strip()]

        for line in data_lines:
            # Parse markdown table row: | Bid | Deployment | Category |
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:  # Including empty first/last
                bid_subject = parts[1]
                deployment_subject = parts[2]
                category = parts[3]

                self.mappings[bid_subject] = deployment_subject

        return self.mappings

    def get_deployment_subject(self, bid_subject: str) -> str | None:
        """Look up deployment subject for a bid subject."""
        return self.mappings.get(bid_subject)

    def validate_all_subjects_exist(self, btx_loader: BTXReferenceLoader) -> list[str]:
        """Check that all mapped subjects exist in BTX files."""
        missing = []

        for bid_subj, deploy_subj in self.mappings.items():
            if not btx_loader.get_icon_data(bid_subj):
                missing.append(f"Bid icon: {bid_subj}")
            if not btx_loader.get_icon_data(deploy_subj):
                missing.append(f"Deployment icon: {deploy_subj}")

        return missing
```

### Load on Startup

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    global btx_loader, mapping_parser

    # Load BTX files
    btx_loader = BTXReferenceLoader(Path("toolchest"))
    btx_loader.load_all_btx_files()

    # Load mappings
    mapping_parser = MappingParser(Path("backend/data/mapping.md"))
    mapping_parser.load_mappings()

    # Validate
    missing = mapping_parser.validate_all_subjects_exist(btx_loader)
    if missing:
        print(f"Warning: Missing icon definitions: {missing}")

    yield

app = FastAPI(lifespan=lifespan)
```

---

## 8. Error Handling

### Custom PDF Exceptions

```python
class PDFConverterError(Exception):
    """Base exception for PDF converter."""
    pass

class InvalidPDFError(PDFConverterError):
    """Raised when file is not a valid PDF."""
    pass

class NoAnnotationsFoundError(PDFConverterError):
    """Raised when PDF contains no markup annotations."""
    pass

class MultiPagePDFError(PDFConverterError):
    """Raised when PDF has multiple pages (MVP limitation)."""
    def __init__(self, page_count: int):
        self.page_count = page_count
        super().__init__(f"Multi-page PDFs not supported (found {page_count} pages)")

class MappingNotFoundError(PDFConverterError):
    """Raised when bid icon subject not in mapping."""
    def __init__(self, subject: str):
        self.subject = subject
        super().__init__(f"Unknown bid icon subject: {subject}")

class BTXIconNotFoundError(PDFConverterError):
    """Raised when icon definition not found in BTX files."""
    def __init__(self, subject: str):
        self.subject = subject
        super().__init__(f"Icon definition not found: {subject}")
```

### Validate PDF Before Processing

```python
def validate_pdf(pdf_path: Path) -> tuple[bool, str]:
    """Validate PDF file."""
    # Check file exists
    if not pdf_path.exists():
        return False, "File not found"

    # Check magic bytes
    with pdf_path.open("rb") as f:
        header = f.read(4)
        if header != b"%PDF":
            return False, "File is not a valid PDF"

    # Check can be opened
    try:
        reader = PdfReader(pdf_path)
        page_count = len(reader.pages)

        # MVP: Single page only
        if page_count > 1:
            return False, f"Multi-page PDFs not supported (found {page_count} pages)"

        # Check has annotations
        page = reader.pages[0]
        if "/Annots" not in page or not page["/Annots"]:
            return False, "No markup annotations found in PDF"

        return True, "Valid"

    except Exception as e:
        return False, f"Failed to read PDF: {str(e)}"
```

---

## 9. Performance Optimization

### Caching Strategies

```python
from functools import lru_cache

# Cache BTX loader globally
_btx_loader = None

def get_btx_loader() -> BTXReferenceLoader:
    global _btx_loader
    if _btx_loader is None:
        _btx_loader = BTXReferenceLoader(Path("toolchest"))
        _btx_loader.load_all_btx_files()
    return _btx_loader

# Cache mapping parser
@lru_cache(maxsize=1)
def get_mapping_parser() -> MappingParser:
    parser = MappingParser(Path("backend/data/mapping.md"))
    parser.load_mappings()
    return parser
```

### Lazy Loading

```python
class LazyBTXLoader:
    def __init__(self, toolchest_dir: Path):
        self.toolchest_dir = toolchest_dir
        self._icons = None

    @property
    def icons(self) -> dict:
        if self._icons is None:
            self._icons = {}
            self.load_all_btx_files()
        return self._icons
```

### Async File Operations

```python
import aiofiles

async def save_pdf_async(pdf_path: Path, content: bytes):
    """Save PDF asynchronously."""
    async with aiofiles.open(pdf_path, "wb") as f:
        await f.write(content)

async def read_pdf_async(pdf_path: Path) -> bytes:
    """Read PDF asynchronously."""
    async with aiofiles.open(pdf_path, "rb") as f:
        return await f.read()
```

---

## 10. Testing Strategies

### Unit Tests for PDF Parsing

```python
import pytest
from pathlib import Path

class TestPDFAnnotationParser:
    def setup_method(self):
        self.parser = PDFAnnotationParser()
        self.sample_pdf = Path("samples/maps/BidMap.pdf")

    def test_extract_annotations_from_sample_pdf(self):
        annotations = self.parser.extract_annotations(self.sample_pdf)
        assert len(annotations) > 0
        assert all("subject" in a for a in annotations)

    def test_parse_coordinates(self):
        rect = [100, 200, 150, 250]
        coords = parse_annotation_coordinates(rect)
        assert coords["x"] == 100
        assert coords["y"] == 200
        assert coords["width"] == 50
        assert coords["height"] == 50
```

### Unit Tests for Hex Decoding

```python
class TestSubjectExtractor:
    def test_plain_text_subject(self):
        result = SubjectExtractor.extract_subject({"subject": "AP_Bid"})
        assert result == "AP_Bid"

    def test_hex_encoded_subject(self):
        # Example hex-encoded subject
        hex_subject = "4150005f426964"  # UTF-16 "AP_Bid"
        result = SubjectExtractor.extract_subject({"subject": hex_subject})
        assert result == "AP_Bid"

    def test_empty_subject(self):
        result = SubjectExtractor.extract_subject({"subject": ""})
        assert result == ""
```

### Integration Tests

```python
class TestEndToEndConversion:
    def test_convert_bid_to_deployment(self):
        # Upload sample PDF
        with open("samples/maps/BidMap.pdf", "rb") as f:
            upload_response = client.post("/api/upload", files={"file": f})

        assert upload_response.status_code == 201
        upload_id = upload_response.json()["upload_id"]

        # Convert
        convert_response = client.post(
            f"/api/convert/{upload_id}",
            json={"direction": "bid_to_deployment"}
        )

        assert convert_response.status_code == 200
        data = convert_response.json()
        assert data["status"] == "success"
        assert data["annotations_converted"] > 0
```

---

## Quick Reference

### Common Patterns

```python
# Open PDF
from pypdf import PdfReader
reader = PdfReader("file.pdf")
page = reader.pages[0]

# Extract annotations
if "/Annots" in page:
    for annot_ref in page["/Annots"]:
        annot = annot_ref.get_object()
        subject = annot.get("/Subject", "")

# Parse BTX
from lxml import etree
tree = etree.parse("toolchest/bidTools/icons.btx")
for tool in tree.findall(".//Tool"):
    subject = tool.findtext("Subject")

# Load mapping
with open("backend/data/mapping.md") as f:
    lines = f.readlines()[2:]  # Skip header
```

---

## Resources

- [pypdf Documentation](https://pypdf.readthedocs.io/)
- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/)
- [pdfplumber Documentation](https://github.com/jsvine/pdfplumber)
- [lxml Documentation](https://lxml.de/)
- [PDF Reference 1.7 (Adobe)](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf)
