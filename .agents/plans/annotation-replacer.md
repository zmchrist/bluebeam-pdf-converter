# Feature: Phase 3 Step 1 - Annotation Replacer Implementation

The following plan should be complete, but it's important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils, types, and models. Import from the right files etc.

## Feature Description

Implement the `AnnotationReplacer` service that replaces bid icon annotations in PDF files with corresponding deployment icon annotations. This is the core conversion engine that:
1. Takes parsed bid annotations from PDFs
2. Looks up deployment subjects via the mapping parser
3. Creates new deployment annotations with preserved coordinates/size
4. Removes old bid annotations from the PDF
5. Inserts new deployment annotations at the same positions

## User Story

As a project estimator
I want to convert bid map PDF annotations to deployment icons automatically
So that I can transform 75+ marked locations in under 1 minute instead of 2-4 hours manually

## Problem Statement

The project has completed Phase 1-2 (PDF parsing, BTX loading, mapping parser) but the core annotation replacement logic in `annotation_replacer.py` is still a stub with `NotImplementedError`. Without this service, the PDF conversion workflow cannot function.

## Solution Statement

Implement `AnnotationReplacer` with methods to:
- Iterate through parsed annotations and map bid subjects to deployment subjects
- Create new PDF annotation dictionaries preserving coordinates and size
- Modify the PDF page's `/Annots` array by removing bid annotations and adding deployment annotations
- Track conversion statistics (converted, skipped, skipped subjects list)
- Handle edge cases (missing mappings, missing BTX data) gracefully

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: Medium-High
**Primary Systems Affected**: `backend/app/services/annotation_replacer.py`, PDF processing pipeline
**Dependencies**: PyPDF2 3.x, existing services (mapping_parser, btx_loader, pdf_parser)

---

## CONTEXT REFERENCES

### Relevant Codebase Files - MANDATORY READING BEFORE IMPLEMENTING

| File | Lines | Why |
|------|-------|-----|
| `backend/app/services/annotation_replacer.py` | ALL | **TARGET FILE** - Current stub to implement |
| `backend/app/services/pdf_parser.py` | 72-164 | Shows how annotations are extracted, rect format, data structure |
| `backend/app/services/mapping_parser.py` | 104-127 | Shows `get_deployment_subject()` and `get_category()` API |
| `backend/app/services/btx_loader.py` | 405-417 | Shows `get_icon_data()` API and IconData structure |
| `backend/app/models/annotation.py` | ALL | `Annotation`, `AnnotationCoordinates`, `AnnotationMapping` models |
| `backend/app/models/mapping.py` | 22-29 | `IconData` model structure (subject, category, metadata) |
| `backend/app/utils/errors.py` | 48-62 | `MappingNotFoundError`, `ConversionError` exceptions |
| `.claude/reference/pdf-processing-best-practices.md` | 348-406 | Annotation replacement strategy and PyPDF2 patterns |
| `backend/tests/test_btx_loader.py` | ALL | Test pattern examples to follow |

### New Files to Create

- `backend/tests/test_annotation_replacer.py` - Comprehensive unit tests (expand existing stub)

### Files to Update

- `backend/app/services/annotation_replacer.py` - Full implementation (currently stub)

### Relevant Documentation - READ BEFORE IMPLEMENTING

- [pypdf Adding Annotations](https://pypdf.readthedocs.io/en/stable/user/adding-pdf-annotations.html) - Creating annotation objects
- [pypdf Reading Annotations](https://pypdf.readthedocs.io/en/stable/user/reading-pdf-annotations.html) - Understanding annotation structure
- [pypdf PdfWriter Class](https://pypdf.readthedocs.io/en/stable/modules/PdfWriter.html) - Page manipulation API
- [GitHub pypdf Issue #2664](https://github.com/py-pdf/pypdf/issues/2664) - Single annotation removal pattern

### Patterns to Follow

**Import Pattern** (from existing services):
```python
import logging
from pathlib import Path
from app.models.annotation import Annotation, AnnotationMapping
from app.models.mapping import IconData
from app.utils.errors import MappingNotFoundError, ConversionError

logger = logging.getLogger(__name__)
```

**Error Handling Pattern** (from `pdf_parser.py`):
```python
try:
    # Operation
except Exception:
    logger.debug(f"Error message: {e}")
    continue  # Or raise appropriate custom exception
```

**Docstring Pattern** (from `btx_loader.py`):
```python
def method_name(self, param: Type) -> ReturnType:
    """
    Brief description.

    Args:
        param: Description of parameter

    Returns:
        Description of return value

    Raises:
        ErrorType: When error occurs
    """
```

**Test Pattern** (from `test_btx_loader.py`):
```python
class TestClassName:
    """Test suite for ServiceName."""

    def test_method_name_scenario(self):
        """Test description."""
        # Setup
        # Action
        # Assert
```

---

## IMPLEMENTATION PLAN

### Phase 1: Foundation - Imports and Class Setup

Establish proper imports, logging, and class structure following existing patterns.

**Tasks:**
- Add required imports (PyPDF2 generic module, logging, models)
- Set up logger instance
- Document class and method signatures

### Phase 2: Core Implementation - Annotation Creation

Implement the method to create deployment annotation dictionaries.

**Tasks:**
- Implement `create_deployment_annotation()` method
- Preserve rect (coordinates/size) from bid annotation
- Set deployment subject in new annotation
- Include required PDF annotation fields (/Type, /Subtype, /Rect, /Subject)

### Phase 3: Core Implementation - Annotation Replacement

Implement the main replacement logic that processes all annotations.

**Tasks:**
- Implement `replace_annotations()` method
- Iterate through annotations and look up mappings
- Track converted/skipped counts
- Remove old annotations from page
- Add new annotations to page
- Return statistics tuple

### Phase 4: Testing - Comprehensive Unit Tests

Create thorough tests for all scenarios.

**Tasks:**
- Test annotation creation with valid data
- Test replacement with valid mappings
- Test handling of missing mappings (skip gracefully)
- Test handling of missing BTX data (skip gracefully)
- Test edge cases (empty annotations list, all skipped)

---

## STEP-BY-STEP TASKS

IMPORTANT: Execute every task in order, top to bottom. Each task is atomic and independently testable.

---

### Task 1: UPDATE `backend/app/services/annotation_replacer.py` - Add Imports

**IMPLEMENT**: Add required imports at top of file

```python
"""
Annotation replacement service.

Replaces bid icon annotations with deployment icon annotations
while preserving exact coordinates and sizing.
"""

import logging
from typing import Any

from PyPDF2 import PdfWriter
from PyPDF2.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    TextStringObject,
)

from app.models.annotation import Annotation, AnnotationCoordinates
from app.models.mapping import IconData
from app.services.btx_loader import BTXReferenceLoader
from app.services.mapping_parser import MappingParser
from app.utils.errors import ConversionError

logger = logging.getLogger(__name__)
```

**PATTERN**: Follow import organization from `btx_loader.py:1-18`
**IMPORTS**: PyPDF2 generic module for creating annotation dictionaries
**GOTCHA**: PyPDF2 uses `generic` module for low-level PDF objects, not the reader/writer classes
**VALIDATE**: `cd backend && python -c "from app.services.annotation_replacer import *; print('Imports OK')"`

---

### Task 2: UPDATE `backend/app/services/annotation_replacer.py` - Implement Class Attributes

**IMPLEMENT**: Add type hints and improve `__init__` documentation

```python
class AnnotationReplacer:
    """
    Service for replacing bid annotations with deployment annotations.

    This service handles the core conversion logic:
    1. Looks up bid subject in mapping to find deployment subject
    2. Gets deployment icon data from BTX loader
    3. Creates new annotation dictionary with preserved coordinates
    4. Removes bid annotation from PDF page
    5. Inserts deployment annotation at same position
    """

    def __init__(
        self,
        mapping_parser: MappingParser,
        btx_loader: BTXReferenceLoader,
    ):
        """
        Initialize annotation replacer.

        Args:
            mapping_parser: MappingParser instance with loaded mappings
            btx_loader: BTXReferenceLoader instance with loaded icons
        """
        self.mapping_parser = mapping_parser
        self.btx_loader = btx_loader
```

**PATTERN**: Follow docstring style from `btx_loader.py:21-37`
**VALIDATE**: `cd backend && python -c "from app.services.annotation_replacer import AnnotationReplacer; print('Class OK')"`

---

### Task 3: UPDATE `backend/app/services/annotation_replacer.py` - Implement `create_deployment_annotation`

**IMPLEMENT**: Create PDF annotation dictionary for deployment icon

```python
    def create_deployment_annotation(
        self,
        bid_annotation: Annotation,
        deployment_subject: str,
        icon_data: IconData | None = None,
    ) -> DictionaryObject:
        """
        Create deployment annotation dictionary from bid annotation.

        Preserves exact coordinates and size from bid annotation,
        updates subject to deployment subject.

        Args:
            bid_annotation: Original bid annotation with coordinates
            deployment_subject: Deployment icon subject name
            icon_data: Optional icon data from BTX (for visual appearance)

        Returns:
            DictionaryObject ready to insert into PDF page
        """
        coords = bid_annotation.coordinates

        # Reconstruct PDF rect format: [x1, y1, x2, y2]
        x1 = coords.x
        y1 = coords.y
        x2 = coords.x + coords.width
        y2 = coords.y + coords.height

        rect = ArrayObject([
            FloatObject(x1),
            FloatObject(y1),
            FloatObject(x2),
            FloatObject(y2),
        ])

        # Create annotation dictionary
        annot = DictionaryObject()
        annot.update({
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Stamp"),
            NameObject("/Rect"): rect,
            NameObject("/Subject"): TextStringObject(deployment_subject),
            NameObject("/F"): NumberObject(4),  # Print flag
        })

        # Add contents if available from original annotation
        if bid_annotation.raw_data and "/Contents" in bid_annotation.raw_data:
            contents = bid_annotation.raw_data.get("/Contents", "")
            if contents:
                annot[NameObject("/Contents")] = TextStringObject(str(contents))

        logger.debug(
            f"Created deployment annotation: {deployment_subject} "
            f"at ({coords.x}, {coords.y})"
        )

        return annot
```

**PATTERN**: Follow PyPDF2 generic object patterns from `.claude/reference/pdf-processing-best-practices.md:388-396`
**IMPORTS**: Uses `DictionaryObject`, `ArrayObject`, `FloatObject`, `NameObject`, `TextStringObject`, `NumberObject` from PyPDF2.generic
**GOTCHA**: PDF rect is [x1, y1, x2, y2] not [x, y, width, height] - must convert back from AnnotationCoordinates
**GOTCHA**: Must use `NameObject("/Key")` for dictionary keys, not plain strings
**VALIDATE**: `cd backend && python -c "
from app.services.annotation_replacer import AnnotationReplacer
from app.models.annotation import Annotation, AnnotationCoordinates

# Create mock dependencies
class MockMapper:
    def get_deployment_subject(self, s): return 'Deploy'
class MockLoader:
    def get_icon_data(self, s, t='deployment'): return None

replacer = AnnotationReplacer(MockMapper(), MockLoader())
annot = Annotation(
    subject='Test',
    coordinates=AnnotationCoordinates(x=100, y=200, width=50, height=50, page=1),
    annotation_type='/Stamp'
)
result = replacer.create_deployment_annotation(annot, 'TestDeploy')
print(f'Created annotation: {result}')
print('create_deployment_annotation OK')
"`

---

### Task 4: UPDATE `backend/app/services/annotation_replacer.py` - Implement `_find_and_remove_annotation`

**IMPLEMENT**: Helper method to find and remove annotation from page by coordinates

```python
    def _find_and_remove_annotation(
        self,
        page: Any,
        target_coords: AnnotationCoordinates,
        target_subject: str,
    ) -> bool:
        """
        Find and remove annotation from page by matching coordinates and subject.

        Args:
            page: PDF page object (from PdfWriter)
            target_coords: Coordinates of annotation to remove
            target_subject: Subject of annotation to remove

        Returns:
            True if annotation was found and removed, False otherwise
        """
        if "/Annots" not in page:
            logger.debug("Page has no /Annots array")
            return False

        annots = page["/Annots"]
        if not annots:
            return False

        # Find annotation by matching rect and subject
        to_remove_idx = None
        for idx, annot_ref in enumerate(annots):
            try:
                annot_obj = annot_ref.get_object()

                # Check subject match
                subj = annot_obj.get("/Subject") or annot_obj.get("/Subj") or ""
                if str(subj) != target_subject:
                    continue

                # Check rect match (approximate due to float precision)
                rect = annot_obj.get("/Rect", [])
                if len(rect) >= 4:
                    x1 = float(rect[0])
                    y1 = float(rect[1])
                    # Match within tolerance
                    if abs(x1 - target_coords.x) < 0.01 and abs(y1 - target_coords.y) < 0.01:
                        to_remove_idx = idx
                        break
            except Exception as e:
                logger.debug(f"Error checking annotation {idx}: {e}")
                continue

        if to_remove_idx is not None:
            del annots[to_remove_idx]
            logger.debug(f"Removed annotation at index {to_remove_idx}: {target_subject}")
            return True

        return False
```

**PATTERN**: Follow annotation iteration pattern from `pdf_parser.py:114-159`
**GOTCHA**: Must handle both `/Subject` and `/Subj` keys (Bluebeam uses both)
**GOTCHA**: Float comparison needs tolerance for coordinate matching
**VALIDATE**: `cd backend && python -c "from app.services.annotation_replacer import AnnotationReplacer; print('Helper method OK')"`

---

### Task 5: UPDATE `backend/app/services/annotation_replacer.py` - Implement `replace_annotations`

**IMPLEMENT**: Main replacement method that processes all annotations

```python
    def replace_annotations(
        self,
        annotations: list[Annotation],
        page: Any,
    ) -> tuple[int, int, list[str]]:
        """
        Replace all bid annotations with deployment annotations on a page.

        For each annotation:
        1. Look up bid subject in mapping to find deployment subject
        2. Get deployment icon data from BTX loader
        3. Remove original bid annotation from page
        4. Create and insert deployment annotation at same coordinates

        Args:
            annotations: List of bid annotations from PDFAnnotationParser
            page: PDF page object to modify (from PdfWriter or PdfReader)

        Returns:
            Tuple of (converted_count, skipped_count, skipped_subjects)
            - converted_count: Number of annotations successfully replaced
            - skipped_count: Number of annotations skipped
            - skipped_subjects: List of bid subjects that were skipped

        Raises:
            ConversionError: If critical conversion failure occurs
        """
        converted_count = 0
        skipped_count = 0
        skipped_subjects: list[str] = []

        if not annotations:
            logger.warning("No annotations provided for replacement")
            return 0, 0, []

        # Ensure page has /Annots array
        if "/Annots" not in page:
            from PyPDF2.generic import ArrayObject
            page[NameObject("/Annots")] = ArrayObject()

        for annotation in annotations:
            bid_subject = annotation.subject

            if not bid_subject:
                logger.debug("Skipping annotation with empty subject")
                skipped_count += 1
                skipped_subjects.append("(empty subject)")
                continue

            # Look up deployment subject
            deployment_subject = self.mapping_parser.get_deployment_subject(bid_subject)
            if not deployment_subject:
                logger.info(f"No mapping found for bid subject: {bid_subject}")
                skipped_count += 1
                skipped_subjects.append(bid_subject)
                continue

            # Get deployment icon data (optional, for visual appearance)
            icon_data = self.btx_loader.get_icon_data(deployment_subject, "deployment")
            if not icon_data:
                logger.warning(
                    f"No BTX icon data for deployment subject: {deployment_subject}, "
                    f"proceeding with subject replacement only"
                )
                # Continue anyway - we can still replace the subject

            try:
                # Remove original bid annotation
                removed = self._find_and_remove_annotation(
                    page,
                    annotation.coordinates,
                    bid_subject,
                )
                if not removed:
                    logger.debug(
                        f"Could not find bid annotation to remove: {bid_subject}"
                    )
                    # Still proceed with adding deployment annotation

                # Create deployment annotation
                new_annot = self.create_deployment_annotation(
                    annotation,
                    deployment_subject,
                    icon_data,
                )

                # Add to page
                page["/Annots"].append(new_annot)

                converted_count += 1
                logger.debug(
                    f"Converted: {bid_subject} -> {deployment_subject}"
                )

            except Exception as e:
                logger.error(f"Error converting annotation {bid_subject}: {e}")
                skipped_count += 1
                skipped_subjects.append(bid_subject)
                continue

        logger.info(
            f"Annotation replacement complete: "
            f"{converted_count} converted, {skipped_count} skipped"
        )

        return converted_count, skipped_count, skipped_subjects
```

**PATTERN**: Follow error handling pattern from `pdf_parser.py:114-163` (try/except with continue)
**PATTERN**: Follow logging pattern from `btx_loader.py` (debug for details, info for summary)
**IMPORTS**: ArrayObject for creating /Annots if missing
**GOTCHA**: Gracefully handle missing mappings - skip and track, don't fail entire conversion
**GOTCHA**: Gracefully handle missing BTX data - replace subject anyway, just without visual appearance
**GOTCHA**: Must ensure `/Annots` array exists before appending
**VALIDATE**: `cd backend && python -c "from app.services.annotation_replacer import AnnotationReplacer; print('replace_annotations OK')"`

---

### Task 6: CREATE comprehensive tests in `backend/tests/test_annotation_replacer.py`

**IMPLEMENT**: Full test suite following existing patterns

```python
"""Tests for annotation replacer service."""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import ArrayObject, DictionaryObject, NameObject

from app.models.annotation import Annotation, AnnotationCoordinates
from app.models.mapping import IconData
from app.services.annotation_replacer import AnnotationReplacer


class MockMappingParser:
    """Mock mapping parser for testing."""

    def __init__(self, mappings: dict[str, str] | None = None):
        self.mappings = mappings or {}

    def get_deployment_subject(self, bid_subject: str) -> str | None:
        return self.mappings.get(bid_subject)


class MockBTXLoader:
    """Mock BTX loader for testing."""

    def __init__(self, icons: dict[str, IconData] | None = None):
        self.icons = icons or {}

    def get_icon_data(self, subject: str, icon_type: str = "deployment") -> IconData | None:
        return self.icons.get(subject)


class TestAnnotationReplacer:
    """Test suite for AnnotationReplacer service."""

    # Test initialization

    def test_init(self):
        """Test replacer initialization."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        assert replacer.mapping_parser == mapper
        assert replacer.btx_loader == loader

    # Test create_deployment_annotation

    def test_create_deployment_annotation_basic(self):
        """Test creating deployment annotation with basic data."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        bid_annot = Annotation(
            subject="AP_Bid",
            coordinates=AnnotationCoordinates(
                x=100.0, y=200.0, width=50.0, height=50.0, page=1
            ),
            annotation_type="/Stamp",
        )

        result = replacer.create_deployment_annotation(bid_annot, "AP_Deploy")

        assert result is not None
        assert result["/Type"] == "/Annot"
        assert result["/Subtype"] == "/Stamp"
        assert str(result["/Subject"]) == "AP_Deploy"

        # Check rect preserves coordinates
        rect = result["/Rect"]
        assert float(rect[0]) == 100.0  # x1
        assert float(rect[1]) == 200.0  # y1
        assert float(rect[2]) == 150.0  # x2 = x + width
        assert float(rect[3]) == 250.0  # y2 = y + height

    def test_create_deployment_annotation_with_icon_data(self):
        """Test creating annotation with BTX icon data."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        icon_data = IconData(
            subject="AP_Deploy",
            category="Access Points",
            metadata={"source_file": "test.btx"},
        )

        bid_annot = Annotation(
            subject="AP_Bid",
            coordinates=AnnotationCoordinates(
                x=100.0, y=200.0, width=50.0, height=50.0, page=1
            ),
            annotation_type="/Stamp",
        )

        result = replacer.create_deployment_annotation(
            bid_annot, "AP_Deploy", icon_data
        )

        assert result is not None
        assert str(result["/Subject"]) == "AP_Deploy"

    def test_create_deployment_annotation_preserves_contents(self):
        """Test that Contents field is preserved from original annotation."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        bid_annot = Annotation(
            subject="AP_Bid",
            coordinates=AnnotationCoordinates(
                x=100.0, y=200.0, width=50.0, height=50.0, page=1
            ),
            annotation_type="/Stamp",
            raw_data={"/Contents": "Original content"},
        )

        result = replacer.create_deployment_annotation(bid_annot, "AP_Deploy")

        assert "/Contents" in result
        assert "Original content" in str(result["/Contents"])

    # Test replace_annotations

    def test_replace_annotations_empty_list(self):
        """Test replacement with empty annotations list."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        # Create a mock page with /Annots
        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject()

        converted, skipped, skipped_subjs = replacer.replace_annotations([], page)

        assert converted == 0
        assert skipped == 0
        assert skipped_subjs == []

    def test_replace_annotations_with_mapping(self):
        """Test successful replacement with valid mapping."""
        mappings = {"AP_Bid": "AP_Deploy"}
        icons = {
            "AP_Deploy": IconData(
                subject="AP_Deploy",
                category="Access Points",
            )
        }
        mapper = MockMappingParser(mappings)
        loader = MockBTXLoader(icons)
        replacer = AnnotationReplacer(mapper, loader)

        # Create mock page
        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject()

        annotations = [
            Annotation(
                subject="AP_Bid",
                coordinates=AnnotationCoordinates(
                    x=100.0, y=200.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            )
        ]

        converted, skipped, skipped_subjs = replacer.replace_annotations(
            annotations, page
        )

        assert converted == 1
        assert skipped == 0
        assert skipped_subjs == []
        # Check annotation was added
        assert len(page["/Annots"]) == 1

    def test_replace_annotations_missing_mapping(self):
        """Test that annotations without mapping are skipped."""
        mapper = MockMappingParser({})  # Empty mappings
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject()

        annotations = [
            Annotation(
                subject="Unknown_Icon",
                coordinates=AnnotationCoordinates(
                    x=100.0, y=200.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            )
        ]

        converted, skipped, skipped_subjs = replacer.replace_annotations(
            annotations, page
        )

        assert converted == 0
        assert skipped == 1
        assert "Unknown_Icon" in skipped_subjs

    def test_replace_annotations_missing_btx_data_still_converts(self):
        """Test that missing BTX data doesn't prevent conversion."""
        mappings = {"AP_Bid": "AP_Deploy"}
        mapper = MockMappingParser(mappings)
        loader = MockBTXLoader({})  # No BTX data

        replacer = AnnotationReplacer(mapper, loader)

        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject()

        annotations = [
            Annotation(
                subject="AP_Bid",
                coordinates=AnnotationCoordinates(
                    x=100.0, y=200.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            )
        ]

        converted, skipped, skipped_subjs = replacer.replace_annotations(
            annotations, page
        )

        # Should still convert (just without visual appearance)
        assert converted == 1
        assert skipped == 0

    def test_replace_annotations_empty_subject_skipped(self):
        """Test that annotations with empty subject are skipped."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject()

        annotations = [
            Annotation(
                subject="",  # Empty subject
                coordinates=AnnotationCoordinates(
                    x=100.0, y=200.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            )
        ]

        converted, skipped, skipped_subjs = replacer.replace_annotations(
            annotations, page
        )

        assert converted == 0
        assert skipped == 1
        assert "(empty subject)" in skipped_subjs

    def test_replace_annotations_multiple_mixed(self):
        """Test replacement with mix of valid and invalid mappings."""
        mappings = {
            "AP_Bid": "AP_Deploy",
            "Switch_Bid": "Switch_Deploy",
        }
        mapper = MockMappingParser(mappings)
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject()

        annotations = [
            Annotation(
                subject="AP_Bid",
                coordinates=AnnotationCoordinates(
                    x=100.0, y=200.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            ),
            Annotation(
                subject="Unknown_Icon",  # No mapping
                coordinates=AnnotationCoordinates(
                    x=200.0, y=300.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            ),
            Annotation(
                subject="Switch_Bid",
                coordinates=AnnotationCoordinates(
                    x=300.0, y=400.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            ),
        ]

        converted, skipped, skipped_subjs = replacer.replace_annotations(
            annotations, page
        )

        assert converted == 2
        assert skipped == 1
        assert "Unknown_Icon" in skipped_subjs
        assert len(page["/Annots"]) == 2

    def test_replace_annotations_creates_annots_array_if_missing(self):
        """Test that /Annots array is created if page doesn't have one."""
        mappings = {"AP_Bid": "AP_Deploy"}
        mapper = MockMappingParser(mappings)
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        # Page without /Annots
        page = DictionaryObject()

        annotations = [
            Annotation(
                subject="AP_Bid",
                coordinates=AnnotationCoordinates(
                    x=100.0, y=200.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            )
        ]

        converted, skipped, skipped_subjs = replacer.replace_annotations(
            annotations, page
        )

        assert converted == 1
        assert "/Annots" in page
        assert len(page["/Annots"]) == 1

    # Test _find_and_remove_annotation

    def test_find_and_remove_annotation_found(self):
        """Test finding and removing annotation by coordinates."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        # Create page with annotation
        from PyPDF2.generic import FloatObject, TextStringObject

        annot = DictionaryObject()
        annot[NameObject("/Subject")] = TextStringObject("AP_Bid")
        annot[NameObject("/Rect")] = ArrayObject([
            FloatObject(100.0),
            FloatObject(200.0),
            FloatObject(150.0),
            FloatObject(250.0),
        ])

        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject([annot])

        coords = AnnotationCoordinates(
            x=100.0, y=200.0, width=50.0, height=50.0, page=1
        )

        result = replacer._find_and_remove_annotation(page, coords, "AP_Bid")

        assert result is True
        assert len(page["/Annots"]) == 0

    def test_find_and_remove_annotation_not_found(self):
        """Test when annotation is not found."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject()

        coords = AnnotationCoordinates(
            x=100.0, y=200.0, width=50.0, height=50.0, page=1
        )

        result = replacer._find_and_remove_annotation(page, coords, "Nonexistent")

        assert result is False

    def test_find_and_remove_annotation_no_annots(self):
        """Test when page has no /Annots array."""
        mapper = MockMappingParser()
        loader = MockBTXLoader()
        replacer = AnnotationReplacer(mapper, loader)

        page = DictionaryObject()

        coords = AnnotationCoordinates(
            x=100.0, y=200.0, width=50.0, height=50.0, page=1
        )

        result = replacer._find_and_remove_annotation(page, coords, "AP_Bid")

        assert result is False


class TestAnnotationReplacerIntegration:
    """Integration tests with real PDF and BTX files."""

    def test_with_real_mapping_parser(self):
        """Test with real mapping parser if available."""
        mapping_file = Path("backend/data/mapping.md")
        if not mapping_file.exists():
            mapping_file = Path("../backend/data/mapping.md")
        if not mapping_file.exists():
            pytest.skip("mapping.md not found")

        from app.services.mapping_parser import MappingParser

        parser = MappingParser(mapping_file)
        parser.load_mappings()

        loader = MockBTXLoader()
        replacer = AnnotationReplacer(parser, loader)

        page = DictionaryObject()
        page[NameObject("/Annots")] = ArrayObject()

        # Use a real bid subject from mapping
        bid_subjects = parser.get_all_bid_subjects()
        if not bid_subjects:
            pytest.skip("No bid subjects in mapping")

        annotations = [
            Annotation(
                subject=bid_subjects[0],
                coordinates=AnnotationCoordinates(
                    x=100.0, y=200.0, width=50.0, height=50.0, page=1
                ),
                annotation_type="/Stamp",
            )
        ]

        converted, skipped, skipped_subjs = replacer.replace_annotations(
            annotations, page
        )

        assert converted == 1
        assert skipped == 0
```

**PATTERN**: Follow test organization from `test_btx_loader.py`
**PATTERN**: Use mock classes for dependencies, real files for integration tests
**GOTCHA**: Tests must handle file paths correctly (may run from different directories)
**VALIDATE**: `cd backend && uv run pytest tests/test_annotation_replacer.py -v`

---

### Task 7: VALIDATE full test suite passes

**VALIDATE**: Run all tests to ensure no regressions

```bash
cd backend && uv run pytest tests/ -v
```

---

### Task 8: VALIDATE imports and syntax

**VALIDATE**: Verify module can be imported without errors

```bash
cd backend && python -c "
from app.services.annotation_replacer import AnnotationReplacer
from app.services.mapping_parser import MappingParser
from app.services.btx_loader import BTXReferenceLoader
from pathlib import Path

# Load real mapping
mapping_parser = MappingParser(Path('data/mapping.md'))
mapping_parser.load_mappings()

# Load real BTX
btx_loader = BTXReferenceLoader(Path('../toolchest'))
btx_loader.load_toolchest()

# Create replacer
replacer = AnnotationReplacer(mapping_parser, btx_loader)

print(f'Mapping entries: {len(mapping_parser.mappings)}')
print(f'Bid icons: {btx_loader.get_bid_icon_count()}')
print(f'Deployment icons: {btx_loader.get_deployment_icon_count()}')
print('Integration OK')
"
```

---

## TESTING STRATEGY

### Unit Tests

**Scope**: Test each method in isolation with mock dependencies

| Test Case | Method | Description |
|-----------|--------|-------------|
| `test_create_deployment_annotation_basic` | `create_deployment_annotation` | Valid annotation creation |
| `test_create_deployment_annotation_preserves_contents` | `create_deployment_annotation` | Contents field preserved |
| `test_replace_annotations_empty_list` | `replace_annotations` | Handle empty input |
| `test_replace_annotations_with_mapping` | `replace_annotations` | Successful conversion |
| `test_replace_annotations_missing_mapping` | `replace_annotations` | Skip unmapped subjects |
| `test_replace_annotations_missing_btx_data` | `replace_annotations` | Continue without visual data |
| `test_replace_annotations_empty_subject` | `replace_annotations` | Skip empty subjects |
| `test_replace_annotations_multiple_mixed` | `replace_annotations` | Mixed valid/invalid |
| `test_find_and_remove_annotation_found` | `_find_and_remove_annotation` | Remove by coords |
| `test_find_and_remove_annotation_not_found` | `_find_and_remove_annotation` | Handle missing |

### Integration Tests

| Test Case | Description |
|-----------|-------------|
| `test_with_real_mapping_parser` | Test with actual mapping.md file |
| (Future) `test_with_real_pdf` | Test with BidMap.pdf once pdf_reconstructor is implemented |

### Edge Cases

- Empty annotations list
- Annotations with empty subjects
- Annotations with no mapping in mapping.md
- Annotations with mapping but no BTX visual data
- Pages without existing /Annots array
- Mixed batch (some valid, some invalid)

---

## VALIDATION COMMANDS

Execute every command to ensure zero regressions and 100% feature correctness.

### Level 1: Syntax & Style

```bash
# Check Python syntax
cd backend && python -m py_compile app/services/annotation_replacer.py

# Check imports work
cd backend && python -c "from app.services.annotation_replacer import AnnotationReplacer"
```

### Level 2: Unit Tests

```bash
# Run annotation replacer tests
cd backend && uv run pytest tests/test_annotation_replacer.py -v

# Run with coverage
cd backend && uv run pytest tests/test_annotation_replacer.py -v --cov=app/services/annotation_replacer
```

### Level 3: Integration Tests

```bash
# Run all backend tests
cd backend && uv run pytest tests/ -v

# Verify integration with real data
cd backend && python -c "
from app.services.annotation_replacer import AnnotationReplacer
from app.services.mapping_parser import MappingParser
from app.services.btx_loader import BTXReferenceLoader
from app.models.annotation import Annotation, AnnotationCoordinates
from PyPDF2.generic import DictionaryObject, ArrayObject, NameObject
from pathlib import Path

# Load dependencies
mapping = MappingParser(Path('data/mapping.md'))
mapping.load_mappings()
btx = BTXReferenceLoader(Path('../toolchest'))
btx.load_toolchest()

# Create replacer
replacer = AnnotationReplacer(mapping, btx)

# Test with mock page
page = DictionaryObject()
page[NameObject('/Annots')] = ArrayObject()

# Use real bid subject
bid_subj = list(mapping.mappings.keys())[0]
annot = Annotation(
    subject=bid_subj,
    coordinates=AnnotationCoordinates(x=100, y=200, width=50, height=50, page=1),
    annotation_type='/Stamp'
)

converted, skipped, skipped_subjs = replacer.replace_annotations([annot], page)
print(f'Converted: {converted}, Skipped: {skipped}')
assert converted == 1
print('Integration test PASSED')
"
```

### Level 4: Manual Validation

```bash
# Visual inspection of created annotation structure
cd backend && python -c "
from app.services.annotation_replacer import AnnotationReplacer
from app.models.annotation import Annotation, AnnotationCoordinates

class MockMapper:
    def get_deployment_subject(self, s): return 'AP - Cisco 9120'
class MockLoader:
    def get_icon_data(self, s, t='deployment'): return None

replacer = AnnotationReplacer(MockMapper(), MockLoader())
annot = Annotation(
    subject='Access Control - Wi-Fi Access Point',
    coordinates=AnnotationCoordinates(x=150.5, y=275.3, width=32.0, height=32.0, page=1),
    annotation_type='/Stamp'
)
result = replacer.create_deployment_annotation(annot, 'AP - Cisco 9120')
print('Created annotation dict:')
for key, value in result.items():
    print(f'  {key}: {value}')
"
```

---

## ACCEPTANCE CRITERIA

- [x] `AnnotationReplacer` class fully implemented (no `NotImplementedError`)
- [ ] `create_deployment_annotation()` creates valid PDF annotation dictionaries
- [ ] `replace_annotations()` processes annotation lists correctly
- [ ] Coordinates and size preserved from bid to deployment annotation
- [ ] Missing mappings handled gracefully (skip, track, don't fail)
- [ ] Missing BTX data handled gracefully (convert subject only)
- [ ] All unit tests pass (15+ test cases)
- [ ] Integration with real mapping.md works
- [ ] Integration with real BTX loader works
- [ ] Code follows project conventions and patterns
- [ ] No regressions in existing tests

---

## COMPLETION CHECKLIST

- [ ] Task 1: Imports added
- [ ] Task 2: Class attributes updated
- [ ] Task 3: `create_deployment_annotation` implemented
- [ ] Task 4: `_find_and_remove_annotation` implemented
- [ ] Task 5: `replace_annotations` implemented
- [ ] Task 6: Unit tests created (15+ tests)
- [ ] Task 7: All tests pass
- [ ] Task 8: Integration validation passes
- [ ] All validation commands executed successfully
- [ ] Manual testing confirms feature works

---

## NOTES

### Design Decisions

1. **Graceful Degradation**: Missing mappings or BTX data don't fail the entire conversion - they're skipped and tracked in the return value. This allows partial conversions to succeed.

2. **Subject-Only Replacement**: When BTX visual data is missing, we still replace the subject. The annotation will be visible but may not have the deployment icon appearance. This is acceptable for MVP.

3. **Coordinate Tolerance**: Float comparison uses 0.01 tolerance to handle precision differences between parsing and reconstruction.

4. **Annotation Removal**: We attempt to remove the original bid annotation before adding the deployment one. If removal fails (e.g., coordinates don't match exactly), we still add the deployment annotation - this may result in duplicates but ensures the conversion completes.

### Future Enhancements

- **Appearance Stream Support**: Currently not copying `/AP` (appearance) dictionary from BTX. Future work could extract and apply visual appearance from BTX icon data.
- **Batch Page Processing**: Current implementation handles single page. Multi-page support would need iteration.
- **Validation Callback**: Could add optional callback for progress reporting during large conversions.

### Known Limitations

- Visual appearance of deployment icons may not match Bluebeam exactly without `/AP` dictionary
- Coordinate matching for removal uses exact match with tolerance - complex transformations may fail
- No rollback if partial failure occurs mid-conversion
