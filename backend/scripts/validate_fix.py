#!/usr/bin/env python3
"""
Validation script for PDF annotation rendering fix.

This script verifies that the PyMuPDF-based annotation replacement
produces visible annotations with valid appearance streams.
"""

import logging
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pymupdf

from app.services.annotation_replacer import AnnotationReplacer
from app.services.appearance_extractor import AppearanceExtractor
from app.services.btx_loader import BTXReferenceLoader
from app.services.mapping_parser import MappingParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def validate_annotation_has_appearance(annot: pymupdf.Annot) -> bool:
    """
    Check if an annotation has a valid appearance stream.

    Args:
        annot: PyMuPDF annotation object

    Returns:
        True if annotation can render (has valid appearance)
    """
    try:
        pixmap = annot.get_pixmap()
        return pixmap is not None and pixmap.width > 0 and pixmap.height > 0
    except Exception:
        return False


def validate_converted_pdf(pdf_path: Path) -> dict:
    """
    Validate that a converted PDF has visible annotations.

    Args:
        pdf_path: Path to the PDF to validate

    Returns:
        Dictionary with validation results
    """
    results = {
        "total_annotations": 0,
        "with_appearance": 0,
        "without_appearance": 0,
        "subjects": [],
        "success": False,
    }

    if not pdf_path.exists():
        logger.error(f"PDF not found: {pdf_path}")
        return results

    doc = pymupdf.open(pdf_path)

    try:
        for page_num, page in enumerate(doc):
            for annot in page.annots():
                if annot is None:
                    continue

                results["total_annotations"] += 1
                subject = annot.info.get("subject", "(no subject)")
                results["subjects"].append(subject)

                if validate_annotation_has_appearance(annot):
                    results["with_appearance"] += 1
                else:
                    results["without_appearance"] += 1
                    logger.warning(f"Annotation without appearance: {subject}")

    finally:
        doc.close()

    results["success"] = (
        results["total_annotations"] > 0 and
        results["without_appearance"] == 0
    )

    return results


def run_conversion_test(
    input_pdf: Path,
    output_pdf: Path,
    mapping_path: Path,
    reference_pdf: Path | None = None,
    toolchest_bid: Path | None = None,
    toolchest_deploy: Path | None = None,
) -> dict:
    """
    Run a full conversion test and validate results.

    Args:
        input_pdf: Path to input PDF with bid annotations
        output_pdf: Path for converted output PDF
        mapping_path: Path to mapping.md file
        reference_pdf: Optional path to reference PDF for appearances
        toolchest_bid: Optional path to bid toolchest
        toolchest_deploy: Optional path to deployment toolchest

    Returns:
        Dictionary with test results
    """
    results = {
        "conversion": {
            "converted": 0,
            "skipped": 0,
            "skipped_subjects": [],
        },
        "validation": {},
        "success": False,
    }

    # Load mapping
    logger.info(f"Loading mappings from: {mapping_path}")
    mapping = MappingParser(mapping_path)
    mapping.load_mappings()
    logger.info(f"Loaded {len(mapping.get_all_bid_subjects())} mappings")

    # Load BTX data
    if toolchest_bid and toolchest_deploy and toolchest_bid.parent.exists():
        logger.info("Loading BTX toolchest data...")
        btx = BTXReferenceLoader(toolchest_bid.parent)
        btx.load_toolchest()
    else:
        logger.info("No toolchest paths provided, creating mock BTX loader")
        # Create a minimal mock loader that doesn't require initialization
        class MockBTXLoader:
            def get_icon_data(self, subject: str, icon_type: str = "deployment"):
                return None
        btx = MockBTXLoader()

    # Load appearance data
    appear = None
    if reference_pdf and reference_pdf.exists():
        logger.info(f"Loading appearances from: {reference_pdf}")
        appear = AppearanceExtractor()
        count = appear.load_from_pdf(reference_pdf)
        logger.info(f"Loaded {count} appearance definitions")

    # Create replacer and run conversion
    replacer = AnnotationReplacer(mapping, btx, appear)

    logger.info(f"Converting: {input_pdf}")
    converted, skipped, skipped_subjs = replacer.replace_annotations(
        input_pdf, output_pdf
    )

    results["conversion"]["converted"] = converted
    results["conversion"]["skipped"] = skipped
    results["conversion"]["skipped_subjects"] = skipped_subjs

    logger.info(f"Conversion complete: {converted} converted, {skipped} skipped")

    if skipped_subjs:
        logger.info(f"Skipped subjects: {skipped_subjs[:10]}...")

    # Validate output
    if output_pdf.exists():
        logger.info(f"Validating output: {output_pdf}")
        results["validation"] = validate_converted_pdf(output_pdf)

        if results["validation"]["success"]:
            logger.info(
                f"VALIDATION PASSED: {results['validation']['total_annotations']} annotations "
                f"all have valid appearance streams"
            )
            results["success"] = True
        else:
            logger.error(
                f"VALIDATION FAILED: {results['validation']['without_appearance']} of "
                f"{results['validation']['total_annotations']} annotations lack appearance streams"
            )
    else:
        logger.error("Output PDF was not created")

    return results


def main():
    """Run validation with sample files."""
    # Define paths relative to backend directory
    backend_dir = Path(__file__).parent.parent
    project_root = backend_dir.parent

    # Required paths
    mapping_path = backend_dir / "data" / "mapping.md"

    # Sample PDF paths (adjust as needed)
    samples_dir = project_root / "samples" / "maps"
    input_pdf = samples_dir / "BidMap.pdf"
    output_pdf = samples_dir / "BidMap_converted_pymupdf.pdf"
    reference_pdf = samples_dir / "DeploymentMap.pdf"

    # Toolchest paths (optional)
    toolchest_dir = project_root / "toolchest"
    toolchest_bid = toolchest_dir / "bidTools"
    toolchest_deploy = toolchest_dir / "deploymentTools"

    # Check required files
    if not mapping_path.exists():
        logger.error(f"Mapping file not found: {mapping_path}")
        sys.exit(1)

    if not input_pdf.exists():
        logger.error(f"Input PDF not found: {input_pdf}")
        logger.info("Creating test PDF for validation...")

        # Create a simple test PDF
        samples_dir.mkdir(parents=True, exist_ok=True)
        doc = pymupdf.open()
        page = doc.new_page(width=612, height=792)

        # Add some test annotations with subjects from mapping
        test_annotations = [
            {"subject": "AP_Bid", "x": 100, "y": 100, "size": 30},
            {"subject": "Switch_24Port_Bid", "x": 200, "y": 100, "size": 30},
            {"subject": "IDF_Bid", "x": 300, "y": 100, "size": 30},
        ]

        for annot_data in test_annotations:
            rect = pymupdf.Rect(
                annot_data["x"],
                annot_data["y"],
                annot_data["x"] + annot_data["size"],
                annot_data["y"] + annot_data["size"],
            )
            annot = page.add_circle_annot(rect)
            info = annot.info
            info["subject"] = annot_data["subject"]
            annot.set_info(info)
            annot.set_colors(fill=(0.5, 0.5, 0.5), stroke=(0, 0, 0))
            annot.update()

        doc.save(input_pdf)
        doc.close()
        logger.info(f"Created test PDF: {input_pdf}")

    # Run validation
    print("\n" + "=" * 60)
    print("PDF Annotation Rendering Fix - Validation")
    print("=" * 60 + "\n")

    results = run_conversion_test(
        input_pdf=input_pdf,
        output_pdf=output_pdf,
        mapping_path=mapping_path,
        reference_pdf=reference_pdf if reference_pdf.exists() else None,
        toolchest_bid=toolchest_bid if toolchest_bid.exists() else None,
        toolchest_deploy=toolchest_deploy if toolchest_deploy.exists() else None,
    )

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Converted: {results['conversion']['converted']}")
    print(f"Skipped: {results['conversion']['skipped']}")

    if results["validation"]:
        print(f"Total annotations in output: {results['validation']['total_annotations']}")
        print(f"With valid appearance: {results['validation']['with_appearance']}")
        print(f"Without appearance: {results['validation']['without_appearance']}")

    print()
    if results["success"]:
        print("STATUS: PASSED")
        print(f"\nOutput PDF: {output_pdf}")
        print("Open this file in a PDF viewer to visually verify annotations are visible.")
        sys.exit(0)
    else:
        print("STATUS: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
