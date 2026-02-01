# Feature: PDF Conversion Test Script

The following plan should be complete, but it's important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils, types, and models. Import from the right files etc.

## Feature Description

Create a simple standalone test script that exercises the full PDF conversion pipeline end-to-end. This script will:
1. Load a sample bid PDF
2. Parse all annotations
3. Run them through the annotation replacer
4. Write a converted PDF to disk
5. Print a summary of what was converted

This provides visual validation before building more infrastructure.

## User Story

As a developer
I want to run a quick test script that converts a sample PDF
So that I can visually verify the conversion works correctly in Bluebeam before building more infrastructure

## Problem Statement

The annotation replacer service is implemented but there's no way to visually verify it works correctly with real PDFs. We need a quick feedback loop before investing in the full API infrastructure.

## Solution Statement

Create a minimal `scripts/test_conversion.py` script that chains together all existing services (pdf_parser, mapping_parser, btx_loader, annotation_replacer) and uses PyPDF2's PdfWriter to output a converted PDF file.

## Feature Metadata

**Feature Type**: Testing/Validation Tool
**Estimated Complexity**: Low
**Primary Systems Affected**: None (standalone script)
**Dependencies**: All existing backend services, PyPDF2

---

## CONTEXT REFERENCES

### Relevant Codebase Files - MANDATORY READING BEFORE IMPLEMENTING

| File | Lines | Why |
|------|-------|-----|
| `backend/app/services/pdf_parser.py` | 72-164 | `parse_pdf()` method - how to get annotations |
| `backend/app/services/annotation_replacer.py` | 171-275 | `replace_annotations()` method - core conversion |
| `backend/app/services/mapping_parser.py` | 26-102 | `load_mappings()` method |
| `backend/app/services/btx_loader.py` | 355-403 | `load_toolchest()` method |

### New Files to Create

- `backend/scripts/test_conversion.py` - Standalone test script

### Sample Files Available

- `samples/maps/BidMap.pdf` - Input test file
- `samples/maps/DeploymentMap.pdf` - Reference for expected output

### Patterns to Follow

**Script Pattern** (standalone executable):
```python
#!/usr/bin/env python
"""Script description."""

from pathlib import Path
import sys

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services... import ...

def main():
    """Main entry point."""
    ...

if __name__ == "__main__":
    main()
```

---

## IMPLEMENTATION PLAN

### Phase 1: Single Task - Create Test Script

Create one self-contained script that does everything.

---

## STEP-BY-STEP TASKS

### Task 1: CREATE `backend/scripts/test_conversion.py`

**IMPLEMENT**: Complete test conversion script

```python
#!/usr/bin/env python
"""
Test script for PDF annotation conversion.

Runs the full conversion pipeline on a sample PDF and outputs result.
Usage: python scripts/test_conversion.py
"""

import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyPDF2 import PdfReader, PdfWriter

from app.services.pdf_parser import PDFAnnotationParser
from app.services.mapping_parser import MappingParser
from app.services.btx_loader import BTXReferenceLoader
from app.services.annotation_replacer import AnnotationReplacer


def main():
    """Run test conversion."""
    # Paths
    project_root = Path(__file__).parent.parent.parent
    input_pdf = project_root / "samples" / "maps" / "BidMap.pdf"
    output_pdf = project_root / "samples" / "maps" / "BidMap_converted.pdf"
    mapping_file = Path(__file__).parent.parent / "data" / "mapping.md"
    toolchest_dir = project_root / "toolchest"

    print("=" * 60)
    print("PDF Conversion Test Script")
    print("=" * 60)

    # Validate paths
    if not input_pdf.exists():
        print(f"ERROR: Input PDF not found: {input_pdf}")
        sys.exit(1)

    print(f"\nInput:  {input_pdf}")
    print(f"Output: {output_pdf}")

    # Step 1: Load mapping configuration
    print("\n[1/5] Loading mapping configuration...")
    mapping_parser = MappingParser(mapping_file)
    mapping_parser.load_mappings()
    print(f"  Loaded {len(mapping_parser.mappings)} bid→deployment mappings")

    # Step 2: Load BTX reference icons
    print("\n[2/5] Loading BTX reference icons...")
    btx_loader = BTXReferenceLoader(toolchest_dir)
    btx_loader.load_toolchest()
    print(f"  Loaded {btx_loader.get_bid_icon_count()} bid icons")
    print(f"  Loaded {btx_loader.get_deployment_icon_count()} deployment icons")

    # Step 3: Parse input PDF annotations
    print("\n[3/5] Parsing input PDF annotations...")
    pdf_parser = PDFAnnotationParser()
    annotations = pdf_parser.parse_pdf(input_pdf)
    print(f"  Found {len(annotations)} annotations")

    # Show sample of subjects found
    subjects = [a.subject for a in annotations if a.subject]
    unique_subjects = sorted(set(subjects))
    print(f"  Unique subjects: {len(unique_subjects)}")
    for subj in unique_subjects[:5]:
        print(f"    - {subj}")
    if len(unique_subjects) > 5:
        print(f"    ... and {len(unique_subjects) - 5} more")

    # Step 4: Convert annotations
    print("\n[4/5] Converting annotations...")
    replacer = AnnotationReplacer(mapping_parser, btx_loader)

    # Load PDF with PdfWriter to enable modification
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Clone the page to writer
    writer.add_page(reader.pages[0])
    page = writer.pages[0]

    # Run replacement
    converted, skipped, skipped_subjects = replacer.replace_annotations(
        annotations, page
    )

    print(f"  Converted: {converted}")
    print(f"  Skipped:   {skipped}")
    if skipped_subjects:
        print(f"  Skipped subjects:")
        for subj in sorted(set(skipped_subjects))[:10]:
            print(f"    - {subj}")

    # Step 5: Write output PDF
    print("\n[5/5] Writing output PDF...")
    with output_pdf.open("wb") as f:
        writer.write(f)
    print(f"  Written to: {output_pdf}")

    # Summary
    print("\n" + "=" * 60)
    print("CONVERSION COMPLETE")
    print("=" * 60)
    print(f"Total annotations: {len(annotations)}")
    print(f"Successfully converted: {converted}")
    print(f"Skipped (no mapping): {skipped}")
    print(f"\nOutput file: {output_pdf}")
    print("\nNext steps:")
    print("1. Open both PDFs in Bluebeam")
    print("2. Compare annotation subjects")
    print("3. Verify coordinates are preserved")


if __name__ == "__main__":
    main()
```

**PATTERN**: Standalone script with sys.path manipulation for imports
**IMPORTS**: All existing services from app.services
**GOTCHA**: Must add backend to sys.path before importing app modules
**GOTCHA**: PdfWriter.add_page() clones the page - modifications go to writer's copy
**VALIDATE**: `cd backend && python scripts/test_conversion.py`

---

## TESTING STRATEGY

### Manual Validation

This is a test script itself. Validation is:
1. Script runs without errors
2. Output PDF is created
3. Open both PDFs in Bluebeam and compare:
   - Annotation subjects changed from bid → deployment
   - Annotation positions are preserved
   - Annotation sizes are preserved

---

## VALIDATION COMMANDS

### Level 1: Script Runs

```bash
cd backend && python scripts/test_conversion.py
```

Expected output:
- Shows progress through 5 steps
- Reports conversion statistics
- Creates `samples/maps/BidMap_converted.pdf`

### Level 2: Output File Exists

```bash
# Verify output file was created
ls -la samples/maps/BidMap_converted.pdf
```

### Level 3: Visual Validation (Manual)

Open both files in Bluebeam:
- `samples/maps/BidMap.pdf` (original)
- `samples/maps/BidMap_converted.pdf` (converted)

Check:
- [ ] Annotation count is similar
- [ ] Subjects have changed from bid icons to deployment icons
- [ ] Icon positions match between files

---

## ACCEPTANCE CRITERIA

- [ ] Script runs without errors
- [ ] Outputs clear progress messages
- [ ] Creates converted PDF file
- [ ] Reports conversion statistics (converted/skipped counts)
- [ ] Lists skipped subjects for debugging

---

## COMPLETION CHECKLIST

- [ ] Script file created at `backend/scripts/test_conversion.py`
- [ ] Script runs successfully: `python scripts/test_conversion.py`
- [ ] Output PDF created: `samples/maps/BidMap_converted.pdf`
- [ ] Visual inspection in Bluebeam confirms conversion works

---

## NOTES

### Design Decisions

1. **Standalone Script**: Not integrated into the app - this is purely for developer testing
2. **Verbose Output**: Shows each step clearly so we can see where issues occur
3. **No Error Handling**: Let exceptions propagate for debugging purposes
4. **Hardcoded Paths**: Uses project-relative paths for simplicity

### Expected Issues

The first run may reveal:
- Missing mappings for some bid subjects (expected - update mapping.md)
- Subjects that don't decode correctly (may need subject_extractor fixes)
- Visual appearance differences (expected - we're not copying /AP streams yet)

### After This Test

If conversion looks good:
1. Implement `pdf_reconstructor.py` properly
2. Wire up the API endpoints
3. Build the frontend

If issues found:
1. Debug and fix the specific service
2. Re-run test script
3. Iterate until conversion is correct
