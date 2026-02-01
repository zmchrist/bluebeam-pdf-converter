#!/usr/bin/env python
"""
Test script for PDF annotation conversion.

Runs the full conversion pipeline on a sample PDF and outputs result.
Usage: python scripts/test_conversion.py
"""

import sys
from datetime import datetime
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyPDF2 import PdfReader, PdfWriter

from app.services.pdf_parser import PDFAnnotationParser
from app.services.mapping_parser import MappingParser
from app.services.btx_loader import BTXReferenceLoader
from app.services.annotation_replacer import AnnotationReplacer
from app.services.appearance_extractor import AppearanceExtractor


def main():
    """Run test conversion."""
    # Paths
    project_root = Path(__file__).parent.parent.parent
    input_pdf = project_root / "samples" / "maps" / "BidMap.pdf"
    reference_pdf = project_root / "samples" / "maps" / "DeploymentMap.pdf"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_pdf = project_root / "samples" / "maps" / f"BidMap_converted_{timestamp}.pdf"
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
    print("\n[1/6] Loading mapping configuration...")
    mapping_parser = MappingParser(mapping_file)
    mapping_parser.load_mappings()
    print(f"  Loaded {len(mapping_parser.mappings)} bid->deployment mappings")

    # Step 2: Load BTX reference icons
    print("\n[2/6] Loading BTX reference icons...")
    btx_loader = BTXReferenceLoader(toolchest_dir)
    btx_loader.load_toolchest()
    print(f"  Loaded {btx_loader.get_bid_icon_count()} bid icons")
    print(f"  Loaded {btx_loader.get_deployment_icon_count()} deployment icons")

    # Step 3: Load appearance streams from reference PDF
    print("\n[3/6] Loading appearance streams from reference PDF...")
    appearance_extractor = AppearanceExtractor()
    if reference_pdf.exists():
        num_appearances = appearance_extractor.load_from_pdf(reference_pdf)
        print(f"  Loaded {num_appearances} appearance streams from DeploymentMap.pdf")
    else:
        print(f"  WARNING: Reference PDF not found: {reference_pdf}")
        print(f"  Proceeding without visual appearance data")

    # Step 4: Parse input PDF annotations
    print("\n[4/6] Parsing input PDF annotations...")
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

    # Step 5: Convert annotations
    print("\n[5/6] Converting annotations...")
    replacer = AnnotationReplacer(mapping_parser, btx_loader, appearance_extractor)

    # Load PDF with PdfWriter to enable modification
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Clone the page to writer
    writer.add_page(reader.pages[0])
    page = writer.pages[0]

    # Run replacement (pass writer for appearance stream cloning)
    converted, skipped, skipped_subjects = replacer.replace_annotations(
        annotations, page, writer
    )

    print(f"  Converted: {converted}")
    print(f"  Skipped:   {skipped}")
    if skipped_subjects:
        print(f"  Skipped subjects:")
        for subj in sorted(set(skipped_subjects))[:10]:
            print(f"    - {subj}")

    # Step 6: Write output PDF
    print("\n[6/6] Writing output PDF...")
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
