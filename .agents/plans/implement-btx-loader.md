# Feature: BTX Loader Implementation

The following plan should be complete, but it's important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils, types, and models. Import from the right files.

## Feature Description

Implement the `BTXReferenceLoader` service to parse Bluebeam BTX (Toolchest XML) files and extract icon subject names and visual data. This service enables the annotation replacement engine to look up deployment icon appearances by subject name during PDF conversion.

BTX files contain zlib-compressed hex-encoded data fields that must be decoded to extract meaningful icon information. The loader will scan `toolchest/bidTools/` and `toolchest/deploymentTools/` directories, parse each BTX file's XML structure, decode compressed fields, and build in-memory dictionaries for O(1) lookup.

## User Story

As a PDF conversion service
I want to load icon definitions from BTX toolchest files
So that I can replace bid icons with their corresponding deployment icon appearances during PDF conversion

## Problem Statement

The annotation replacement engine needs access to deployment icon visual data (appearance streams, metadata) to replace bid annotations. Currently, the `btx_loader.py` service is a stub that raises `NotImplementedError`. Without a working BTX loader, the conversion pipeline cannot complete Phase 2.

## Solution Statement

Implement a `BTXReferenceLoader` class that:
1. Scans toolchest directories for `.btx` files
2. Parses BTX XML structure using lxml
3. Decodes hex-encoded zlib-compressed fields (starting with `789c` magic number)
4. Extracts subject names from decoded `<Title>` or decoded `<Raw>` fields
5. Builds lookup dictionaries: `{subject: IconData}`
6. Provides O(1) access to icon data by subject name

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: Medium
**Primary Systems Affected**: `backend/app/services/btx_loader.py`, test files
**Dependencies**: lxml, zlib (built-in)

---

## CONTEXT REFERENCES

### Relevant Codebase Files IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

- `backend/app/services/btx_loader.py` (lines 1-54) - Why: Current stub implementation to replace
- `backend/app/models/mapping.py` (lines 22-29) - Why: `IconData` model to use for icon data storage
- `backend/app/services/subject_extractor.py` (lines 41-74) - Why: Pattern for hex detection (`is_hex_encoded`)
- `backend/app/services/mapping_parser.py` (lines 1-50) - Why: Service pattern to follow
- `backend/tests/test_mapping_parser.py` - Why: Test pattern example with temp files

### BTX File Locations (MUST VALIDATE PATHS)

- Bid Tools: `toolchest/bidTools/CDS Bluebeam Bid Tools [01-21-2026].btx` (1 file)
- Deployment Tools: `toolchest/deploymentTools/` (8 category files)
  - `CDS Bluebeam Access Points [01-01-2026].btx`
  - `CDS Bluebeam Cables [08-22-2025].btx`
  - `CDS Bluebeam Hardlines [01-01-2026].btx`
  - `CDS Bluebeam Hardware [01-01-2026].btx`
  - `CDS Bluebeam IoT [01-01-2026].btx`
  - `CDS Bluebeam Miscellaneous [01-01-2026].btx`
  - `CDS Bluebeam Point-to-Points [01-01-2026].btx`
  - `CDS Bluebeam Switches [01-01-2026].btx`

### New Files to Create

- `backend/tests/test_btx_loader.py` - Unit tests for BTX loader service

### Relevant Documentation YOU SHOULD READ THESE BEFORE IMPLEMENTING!

- `.claude/reference/pdf-processing-best-practices.md` (Section 3: BTX File Processing)
  - Why: Contains BTX parsing patterns and examples
- `CLAUDE.md` (BTX File Format section)
  - Why: Documents actual BTX structure discovered from real files

### BTX File Format (Discovered from Real Files)

```xml
<?xml version="1.0" encoding="utf-8"?>
<BluebeamRevuToolSet Version="1">
  <Title>789c73ca4c5108c9cfcf2956d030323032d304002a93047c</Title>  <!-- hex zlib -->
  <DoScale>true</DoScale>
  <BaselineScale>77.70278 in = 9842.52 ft</BaselineScale>
  <ToolChestItem Version="1">
    <Resources>
      <ID>789c738d88f4f3f576740df50b76f60c72770100291f04c2</ID>  <!-- hex zlib -->
      <Data>789c...</Data>  <!-- hex zlib binary data -->
    </Resources>
    <Name>TLIAKJTTQFXGXJAP</Name>  <!-- internal ID, NOT display name -->
    <Type>Bluebeam.PDF.Annotations.AnnotationCircle</Type>
    <Raw>789c...</Raw>  <!-- hex zlib, contains annotation properties -->
    <X>0.07519531</X>
    <Y>0.07519531</Y>
    <Index>1414</Index>
    <Child>...</Child>  <!-- nested child annotations -->
    <Mode>drawing</Mode>
    <Sequence>...</Sequence>  <!-- optional sequence info -->
  </ToolChestItem>
</BluebeamRevuToolSet>
```

**Key Insight**: The `<Name>` element is NOT the display subject - it's an internal random ID. The actual subject name must be extracted from:
1. The decoded `<Title>` element (toolchest title, e.g., "Bid Tools")
2. OR decoded fields within `<Raw>` elements (contains annotation properties including Subject)

**Decoding Process**:
```python
import zlib

hex_string = "789c73ca4c5108c9cfcf2956d030323032d304002a93047c"
compressed = bytes.fromhex(hex_string)
decompressed = zlib.decompress(compressed)
text = decompressed.decode('utf-8')  # Result: "Bid Tools 01-2026" or similar
```

### Patterns to Follow

**Service Class Pattern** (from `mapping_parser.py`):
```python
class MappingParser:
    def __init__(self, mapping_file: Path):
        self.mapping_file = mapping_file
        self.mappings: dict[str, str] = {}
        # ...

    def load_mappings(self) -> IconMapping:
        """Load and parse mapping file."""
        if not self.mapping_file.exists():
            raise FileNotFoundError(...)
        # processing logic
        return IconMapping(...)
```

**Hex Detection Pattern** (from `subject_extractor.py:41-74`):
```python
@staticmethod
def is_hex_encoded(subject: str) -> bool:
    if not subject:
        return False
    if len(subject) % 2 != 0:
        return False
    try:
        int(subject, 16)
        return True
    except ValueError:
        return False
```

**Error Handling Pattern** (from `utils/errors.py`):
```python
class PDFConverterError(Exception):
    """Base exception for PDF converter errors."""
    pass
```

---

## IMPLEMENTATION PLAN

### Phase 1: Zlib Decoding Utilities

Create utility functions for decoding hex-encoded zlib-compressed BTX fields.

**Tasks:**
- Add zlib decoding function that handles hex→bytes→decompress→text
- Handle decoding errors gracefully (corrupted data, invalid hex)
- Detect zlib magic number (0x789c) to identify compressed fields

### Phase 2: BTX XML Parsing

Parse BTX file XML structure and extract ToolChestItem elements.

**Tasks:**
- Use lxml to parse BTX XML files
- Handle BOM (UTF-8 with BOM marker) at file start
- Extract all `<ToolChestItem>` elements
- Parse nested `<Child>` elements for complete icon data
- Extract `<Resources>` for icon visual data

### Phase 3: Subject Name Extraction

Extract meaningful subject names from decoded BTX fields.

**Tasks:**
- Decode `<Title>` to get toolchest name
- Decode `<Raw>` fields to extract annotation Subject property
- Build mapping from internal `<Name>` to decoded subject
- Handle cases where subject is embedded in annotation data

### Phase 4: Icon Data Collection

Build dictionaries for bid and deployment icon lookup.

**Tasks:**
- Scan `toolchest/bidTools/` for bid icon BTX files
- Scan `toolchest/deploymentTools/` for deployment icon BTX files
- Create IconData objects with subject, category, visual_data, metadata
- Store in `bid_icons` and `deployment_icons` dictionaries

### Phase 5: Testing & Validation

Comprehensive unit tests for BTX loader.

**Tasks:**
- Test zlib decoding with real BTX hex strings
- Test XML parsing with sample BTX content
- Test loading from actual toolchest directories
- Test subject extraction accuracy
- Verify all deployment tools load correctly

---

## STEP-BY-STEP TASKS

IMPORTANT: Execute every task in order, top to bottom. Each task is atomic and independently testable.

**NOTE ON MAPPING.MD**: The current `mapping.md` contains PLACEHOLDER subjects (e.g., "AP_Bid", "AP_Deployment") that are NOT real subject names from BTX files. These placeholders should be cleared and replaced with actual discovered subjects. The implementation agent must use best judgment to match bid icons to their corresponding deployment icons based on naming patterns, categories, and icon purpose.

### Task 1: UPDATE `backend/app/services/btx_loader.py` - Add imports and zlib decoding

- **IMPLEMENT**: Add zlib, lxml imports and `decode_hex_zlib()` utility function
- **PATTERN**: Similar to hex handling in `subject_extractor.py`
- **IMPORTS**: `import zlib`, `from lxml import etree`
- **GOTCHA**: BTX files may have UTF-8 BOM (`\ufeff`) - strip before parsing
- **VALIDATE**: Create quick test script:
  ```python
  cd backend && python -c "
  from app.services.btx_loader import BTXReferenceLoader
  result = BTXReferenceLoader.decode_hex_zlib('789c73ca4c5108c9cfcf2956d030323032d304002a93047c')
  print(f'Decoded: {result}')
  assert 'Bid' in result or 'Tool' in result, f'Unexpected result: {result}'
  "
  ```

### Task 2: UPDATE `backend/app/services/btx_loader.py` - Add BTX file parsing

- **IMPLEMENT**: Add `_parse_btx_file()` method to parse XML and extract ToolChestItem data
- **PATTERN**: Use lxml.etree.parse() with error handling
- **IMPORTS**: Already added in Task 1
- **GOTCHA**: Handle file encoding issues, remove BOM if present
- **VALIDATE**:
  ```python
  cd backend && python -c "
  from pathlib import Path
  from app.services.btx_loader import BTXReferenceLoader
  loader = BTXReferenceLoader(Path('toolchest'))
  items = loader._parse_btx_file(Path('toolchest/bidTools/CDS Bluebeam Bid Tools [01-21-2026].btx'))
  print(f'Found {len(items)} tool items')
  assert len(items) > 0, 'No items found'
  "
  ```

### Task 3: UPDATE `backend/app/services/btx_loader.py` - Extract subject from Raw

- **IMPLEMENT**: Add `_extract_subject_from_raw()` to decode Raw field and find Subject property
- **PATTERN**: The Raw field contains compressed annotation dict with Subject key
- **IMPORTS**: None additional
- **GOTCHA**: Subject may be in nested structure; try multiple extraction strategies
- **VALIDATE**:
  ```python
  cd backend && python -c "
  from pathlib import Path
  from app.services.btx_loader import BTXReferenceLoader
  loader = BTXReferenceLoader(Path('toolchest'))
  # Test with known Raw hex from BTX file
  raw_hex = '789c95526d6f9b400cfe2b273e11adc50729052242552e642393d208bab224e20321b7840a38049742fefd0eb249db226d9d2c9decb3fdf8f18b6d834fb658d10cac9ba686b062a86343d375a1691656ad7b3586602622b0d1fffdf1c6f04c8bca7559d7476011af8f5503fdaaeb8a718fadb1d92bba89b129f0886c3f74458ede68dd64ac9c4aaa82a507c7deb1fd190947d94cba6fc9543a725e4d00dab65584adb0fa004d7aa44502c2bcdd273c0191091212e6246525a7257f3e57742a71da7138f222bff81e57fecbcf5a6e7ea23b9a14abd93ca06fa7898655f312d554349d4a9aa20936171abf5168c70303d5b22ce8066cc7ae1c923529434470c9cf0dbf417768c56a8ec236e3e9f14618de071b2ac786be396704e169f72afbcb79f018a25b445851252947defe407fe48c86992e9382fa33209bcf9fa2f9576f435ea2c597201c7c1f6b76aa96b4e15979d8fe03eb0a60b35e2e9e7c6f11445ee4afd7417c05d997bece73439fb0fc549433d1ea561e0da28ee47748dc37cdc55e8064759a530868caffe760c865b58dfc8e618f608eee40dc3412120bdae2c4235140d52114d29f07b8acded3da71e089fc7d7c8ef31d77c2eb58'
  subject = loader._extract_subject_from_raw(raw_hex)
  print(f'Extracted subject: {subject}')
  "
  ```

### Task 4: UPDATE `backend/app/services/btx_loader.py` - Implement load_toolchest()

- **IMPLEMENT**: Complete `load_toolchest()` method to scan directories and populate dictionaries
- **PATTERN**: Follow `MappingParser.load_mappings()` structure
- **IMPORTS**: None additional
- **GOTCHA**: Distinguish bid vs deployment by directory path; handle missing directories
- **VALIDATE**:
  ```python
  cd backend && python -c "
  from pathlib import Path
  from app.services.btx_loader import BTXReferenceLoader
  loader = BTXReferenceLoader(Path('toolchest'))
  loader.load_toolchest()
  print(f'Bid icons loaded: {len(loader.bid_icons)}')
  print(f'Deployment icons loaded: {len(loader.deployment_icons)}')
  print(f'Bid subjects: {list(loader.bid_icons.keys())[:5]}')
  print(f'Deployment subjects: {list(loader.deployment_icons.keys())[:5]}')
  "
  ```

### Task 5: UPDATE `backend/app/services/btx_loader.py` - Add helper methods

- **IMPLEMENT**: Add `get_bid_icon_count()`, `get_deployment_icon_count()`, `get_all_subjects()` helpers
- **PATTERN**: Follow `MappingParser.get_all_bid_subjects()` pattern
- **IMPORTS**: None additional
- **GOTCHA**: Methods should work before and after `load_toolchest()` is called
- **VALIDATE**:
  ```python
  cd backend && python -c "
  from pathlib import Path
  from app.services.btx_loader import BTXReferenceLoader
  loader = BTXReferenceLoader(Path('toolchest'))
  # Before loading
  assert loader.get_bid_icon_count() == 0
  # After loading
  loader.load_toolchest()
  assert loader.get_bid_icon_count() > 0
  print(f'All subjects: {loader.get_all_subjects()[:10]}')
  "
  ```

### Task 6: CREATE `backend/tests/test_btx_loader.py` - Unit tests

- **IMPLEMENT**: Create comprehensive test suite for BTXReferenceLoader
- **PATTERN**: Mirror `test_mapping_parser.py` structure
- **IMPORTS**: `pytest`, `Path`, `tempfile` for test fixtures
- **GOTCHA**: Tests must work even if toolchest files are missing (use pytest.skip)
- **VALIDATE**: `cd backend && uv run pytest tests/test_btx_loader.py -v`

### Task 7: CREATE `backend/data/mapping.md` - Build accurate bid→deployment mapping

- **IMPLEMENT**: Clear existing placeholder mappings and create accurate mapping based on discovered BTX subjects
- **PATTERN**: Keep markdown table format with 3 columns
- **IMPORTS**: N/A (markdown file)
- **CRITICAL**: The existing mapping.md contains PLACEHOLDER subjects that are NOT real. You must:
  1. First run BTX loader to discover ALL real subject names from bid and deployment BTX files
  2. Print/log all discovered subjects for analysis
  3. Use best judgment to match bid subjects to their corresponding deployment subjects based on:
     - Similar naming patterns (e.g., "AP Cisco 9120" bid → "AP - Cisco 9120" deployment)
     - Category groupings (Access Points, Switches, etc.)
     - Icon type/purpose
  4. Clear the placeholder entries and write the REAL mappings
- **GOTCHA**: Bid and deployment subjects may have slightly different naming conventions - use fuzzy matching logic to identify pairs
- **VALIDATE**:
  ```python
  cd backend && python -c "
  from pathlib import Path
  from app.services.btx_loader import BTXReferenceLoader

  loader = BTXReferenceLoader(Path('toolchest'))
  loader.load_toolchest()

  print('=== DISCOVERED BID SUBJECTS ===')
  for subj in sorted(loader.bid_icons.keys()):
      print(f'  {subj}')

  print()
  print('=== DISCOVERED DEPLOYMENT SUBJECTS ===')
  for subj in sorted(loader.deployment_icons.keys()):
      print(f'  {subj}')

  print()
  print(f'Total bid icons: {len(loader.bid_icons)}')
  print(f'Total deployment icons: {len(loader.deployment_icons)}')
  "
  ```

### Task 8: VALIDATE mapping completeness

- **IMPLEMENT**: After creating mapping.md, verify all mappings are valid
- **PATTERN**: Cross-reference mapping entries against loaded BTX subjects
- **VALIDATE**:
  ```python
  cd backend && python -c "
  from pathlib import Path
  from app.services.btx_loader import BTXReferenceLoader
  from app.services.mapping_parser import MappingParser

  loader = BTXReferenceLoader(Path('toolchest'))
  loader.load_toolchest()

  parser = MappingParser(Path('data/mapping.md'))
  mapping = parser.load_mappings()

  bid_subjects = set(loader.bid_icons.keys())
  deployment_subjects = set(loader.deployment_icons.keys())

  errors = []
  for bid_subj, dep_subj in mapping.mappings.items():
      if bid_subj not in bid_subjects:
          errors.append(f'Missing bid: {bid_subj}')
      if dep_subj not in deployment_subjects:
          errors.append(f'Missing deployment: {dep_subj}')

  if errors:
      print('ERRORS:')
      for e in errors:
          print(f'  - {e}')
      raise AssertionError(f'{len(errors)} mapping errors found')
  else:
      print(f'SUCCESS: All {mapping.total_mappings} mappings validated')
  "
  ```

---

## TESTING STRATEGY

### Unit Tests

Based on `test_mapping_parser.py` patterns:

```python
class TestBTXReferenceLoader:
    """Test suite for BTXReferenceLoader service."""

    # Test decode_hex_zlib()
    def test_decode_hex_zlib_valid(self):
        """Test decoding valid hex-encoded zlib data."""

    def test_decode_hex_zlib_invalid_hex(self):
        """Test handling of invalid hex string."""

    def test_decode_hex_zlib_not_zlib(self):
        """Test handling of non-zlib hex data."""

    # Test _parse_btx_file()
    def test_parse_btx_file_valid(self):
        """Test parsing valid BTX file."""

    def test_parse_btx_file_missing(self):
        """Test handling of missing BTX file."""

    def test_parse_btx_file_invalid_xml(self):
        """Test handling of malformed XML."""

    # Test load_toolchest()
    def test_load_toolchest_real_files(self):
        """Test loading from actual toolchest directory."""

    def test_load_toolchest_empty_dir(self):
        """Test handling of empty toolchest directory."""

    # Test get_icon_data()
    def test_get_icon_data_found(self):
        """Test retrieving existing icon data."""

    def test_get_icon_data_not_found(self):
        """Test retrieving non-existent icon data."""
```

### Integration Tests

Test BTX loader with mapping parser:
- Verify all mapping.md bid subjects exist in bid BTX files
- Verify all mapping.md deployment subjects exist in deployment BTX files

### Edge Cases

- BTX file with UTF-8 BOM marker
- BTX file with no ToolChestItem elements
- Corrupted zlib data in hex field
- Empty `<Raw>` or `<Title>` elements
- `<Name>` element with special characters
- Nested `<Child>` elements with subjects

---

## VALIDATION COMMANDS

Execute every command to ensure zero regressions and 100% feature correctness.

### Level 1: Syntax & Import Check

```bash
cd backend && python -c "from app.services.btx_loader import BTXReferenceLoader; print('Import OK')"
```

### Level 2: Unit Tests

```bash
cd backend && uv run pytest tests/test_btx_loader.py -v
```

### Level 3: Integration Test with Real Files

```bash
cd backend && python -c "
from pathlib import Path
from app.services.btx_loader import BTXReferenceLoader

loader = BTXReferenceLoader(Path('toolchest'))
loader.load_toolchest()

print('=== BTX Loader Test ===')
print(f'Bid icons: {loader.get_bid_icon_count()}')
print(f'Deployment icons: {loader.get_deployment_icon_count()}')

# Verify at least some icons loaded
assert loader.get_bid_icon_count() > 0, 'No bid icons loaded'
assert loader.get_deployment_icon_count() > 0, 'No deployment icons loaded'

print('SUCCESS: BTX loader working correctly')
"
```

### Level 4: All Backend Tests

```bash
cd backend && uv run pytest tests/ -v
```

### Level 5: Mapping Validation

```bash
cd backend && python -c "
from pathlib import Path
from app.services.btx_loader import BTXReferenceLoader
from app.services.mapping_parser import MappingParser

loader = BTXReferenceLoader(Path('toolchest'))
loader.load_toolchest()

parser = MappingParser(Path('data/mapping.md'))
mapping = parser.load_mappings()

errors = []
for bid_subj, dep_subj in mapping.mappings.items():
    if bid_subj not in loader.bid_icons:
        errors.append(f'Missing bid: {bid_subj}')
    if dep_subj not in loader.deployment_icons:
        errors.append(f'Missing deployment: {dep_subj}')

if errors:
    print('ERRORS:')
    for e in errors:
        print(f'  - {e}')
else:
    print('SUCCESS: All mapping subjects found in BTX files')
"
```

---

## ACCEPTANCE CRITERIA

- [ ] `BTXReferenceLoader.decode_hex_zlib()` correctly decodes "789c" prefixed hex strings
- [ ] `load_toolchest()` successfully loads bid icons from `toolchest/bidTools/`
- [ ] `load_toolchest()` successfully loads deployment icons from `toolchest/deploymentTools/`
- [ ] `get_icon_data(subject, "bid")` returns IconData for valid bid subjects
- [ ] `get_icon_data(subject, "deployment")` returns IconData for valid deployment subjects
- [ ] All unit tests in `test_btx_loader.py` pass
- [ ] No regressions in existing tests (`test_mapping_parser.py`, `test_subject_extractor.py`, etc.)
- [ ] mapping.md REBUILT with real subjects discovered from BTX files (placeholders removed)
- [ ] Bid→deployment mappings created using best-judgment matching (naming patterns, categories, icon purpose)
- [ ] All mapping.md entries validated against actual BTX file subjects (100% match)
- [ ] Code follows project conventions (type hints, docstrings, error handling)

---

## COMPLETION CHECKLIST

- [ ] All 8 tasks completed in order
- [ ] Each task validation passed immediately
- [ ] All validation commands executed successfully
- [ ] Full test suite passes (unit + integration)
- [ ] No linting or type checking errors
- [ ] mapping.md rebuilt with REAL subjects discovered from BTX files (placeholders cleared)
- [ ] All bid→deployment mappings use best-judgment matching based on naming/category/purpose
- [ ] Code reviewed for quality and maintainability

---

## NOTES

### Design Decisions

1. **Static method for decode_hex_zlib**: Makes testing easier and allows reuse without instantiation
2. **Lazy loading**: `load_toolchest()` must be called explicitly - not in `__init__` - to allow configuration before loading
3. **IconData model**: Using existing Pydantic model from `mapping.py` for consistency
4. **Category extraction**: Derive category from BTX file name (e.g., "Access Points" from "CDS Bluebeam Access Points...")

### Known Challenges

1. **Subject extraction uncertainty**: The `<Name>` element is NOT the display subject. Real subject may be in:
   - Decoded `<Raw>` field as annotation property
   - Decoded `<ID>` field
   - Decoded `<Title>` at toolchest level

   Implementation must try multiple strategies and log when subject cannot be extracted.

2. **Large Data fields**: `<Data>` elements contain compressed binary image data. For MVP, we may only need to store the raw bytes without processing.

3. **Nested Children**: ToolChestItems can have nested `<Child>` elements. The loader should flatten these or handle hierarchically based on annotation replacer needs.

### Key Deliverable: Accurate Bid→Deployment Mapping

**IMPORTANT**: The current `mapping.md` contains **PLACEHOLDER subjects that are NOT real** (e.g., "AP_Bid", "AP_Deployment"). These are dummy values that must be completely replaced.

A critical output of this implementation is building the accurate "conversion key":

1. **Discover** all real subject names from BTX files (both bid and deployment)
2. **Analyze** naming patterns between bid icons and deployment icons
3. **Match** bid subjects to their corresponding deployment subjects using best judgment:
   - Similar names (e.g., "AP Cisco 9120" ↔ "AP - Cisco 9120")
   - Same category (Access Points, Switches, Hardware, etc.)
   - Same equipment type/purpose
   - Visual similarity if names don't match perfectly
4. **Clear** existing placeholder mappings in mapping.md
5. **Rebuild** mapping.md with accurate, validated real mappings

This mapping is the "conversion key" that makes the entire PDF bid→deployment conversion possible. Without accurate mappings, the conversion cannot work correctly.

### Trade-offs

- **Memory vs Speed**: Loading all icons into memory allows O(1) lookup but uses more RAM. For typical toolchest sizes (hundreds of icons), this is acceptable.
- **Exact vs Fuzzy matching**: Initial implementation uses exact subject matching. Fuzzy matching can be added later if needed.
