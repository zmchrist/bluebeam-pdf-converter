#!/usr/bin/env python
"""
Diagnostic script to understand annotation parsing issues.

This script:
1. Parses BidMap.pdf and prints detailed annotation data
2. Lists all unique subjects found with counts
3. Shows which subjects have mappings vs which don't
4. Extracts subjects from BTX files for comparison
"""

import sys
from pathlib import Path

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from collections import Counter
from PyPDF2 import PdfReader


def analyze_pdf_annotations(pdf_path: Path) -> list[dict]:
    """
    Extract ALL annotation data from PDF, showing raw structure.

    Returns list of annotation dictionaries with all keys/values.
    """
    reader = PdfReader(pdf_path)
    print(f"\n{'='*80}")
    print(f"PDF ANALYSIS: {pdf_path.name}")
    print(f"{'='*80}")
    print(f"Pages: {len(reader.pages)}")

    page = reader.pages[0]
    if "/Annots" not in page:
        print("No annotations found in PDF!")
        return []

    annots = page["/Annots"]
    print(f"Total annotation references: {len(annots)}")

    annotations = []
    for i, annot_ref in enumerate(annots):
        try:
            annot = annot_ref.get_object()

            # Extract ALL keys and values
            annot_data = {}
            for key in annot.keys():
                try:
                    value = annot[key]
                    # Store as-is for analysis
                    annot_data[str(key)] = value
                except Exception as e:
                    annot_data[str(key)] = f"<error: {e}>"

            annotations.append(annot_data)
        except Exception as e:
            annotations.append({"_error": str(e)})

    return annotations


def print_annotation_details(annotations: list[dict], limit: int = 10):
    """Print detailed info for first N annotations."""
    print(f"\n{'='*80}")
    print(f"FIRST {limit} ANNOTATIONS (DETAILED)")
    print(f"{'='*80}")

    for i, annot in enumerate(annotations[:limit]):
        print(f"\n--- Annotation {i+1} ---")
        for key, value in sorted(annot.items()):
            # Format value for display
            value_str = str(value)
            if len(value_str) > 200:
                value_str = value_str[:200] + "..."
            print(f"  {key}: {value_str}")


def analyze_subjects(annotations: list[dict]):
    """Analyze and count all subject-related fields."""
    print(f"\n{'='*80}")
    print("SUBJECT ANALYSIS")
    print(f"{'='*80}")

    # Collect subjects from various possible fields
    subjects = []
    subject_sources = Counter()

    for annot in annotations:
        subject = None
        source = None

        # Try different fields that might contain subject
        if "/Subject" in annot and annot["/Subject"]:
            subject = str(annot["/Subject"])
            source = "/Subject"
        elif "/Subj" in annot and annot["/Subj"]:
            subject = str(annot["/Subj"])
            source = "/Subj"
        elif "/T" in annot and annot["/T"]:
            subject = str(annot["/T"])
            source = "/T"
        elif "/Contents" in annot and annot["/Contents"]:
            subject = str(annot["/Contents"])
            source = "/Contents"

        if subject:
            subjects.append(subject)
            subject_sources[source] += 1
        else:
            subjects.append("")
            subject_sources["<empty>"] += 1

    print("\nSubject field sources:")
    for source, count in subject_sources.most_common():
        print(f"  {source}: {count}")

    # Count unique subjects
    subject_counts = Counter(subjects)

    print(f"\nTotal annotations: {len(annotations)}")
    print(f"Annotations with subjects: {len([s for s in subjects if s])}")
    print(f"Annotations without subjects: {len([s for s in subjects if not s])}")
    print(f"Unique subjects: {len([k for k in subject_counts.keys() if k])}")

    return subject_counts


def print_subject_counts(subject_counts: Counter):
    """Print all unique subjects with their counts."""
    print(f"\n{'='*80}")
    print("UNIQUE SUBJECTS (with counts)")
    print(f"{'='*80}")

    # Sort by count descending
    for subject, count in subject_counts.most_common():
        if subject:
            print(f"  [{count:3d}] {subject}")

    # Print empty count at end
    if "" in subject_counts:
        print(f"\n  [{subject_counts['']}] <EMPTY SUBJECT>")


def check_mappings(subject_counts: Counter, mapping_file: Path):
    """Check which subjects have mappings vs which don't."""
    print(f"\n{'='*80}")
    print("MAPPING ANALYSIS")
    print(f"{'='*80}")

    # Load mappings from file
    if not mapping_file.exists():
        print(f"Mapping file not found: {mapping_file}")
        return

    mappings = {}
    with mapping_file.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    in_table = False
    for line in lines:
        line = line.strip()
        if line.startswith("|") and "Bid Icon Subject" in line:
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                bid_subject = parts[1]
                deploy_subject = parts[2]
                if bid_subject and deploy_subject:
                    mappings[bid_subject] = deploy_subject

    print(f"Total mappings in mapping.md: {len(mappings)}")

    # Check PDF subjects against mappings
    matched = []
    unmatched = []

    for subject, count in subject_counts.items():
        if not subject:
            continue
        if subject in mappings:
            matched.append((subject, count, mappings[subject]))
        else:
            unmatched.append((subject, count))

    print(f"\nMatched subjects (have mappings): {len(matched)}")
    for subject, count, deploy in matched:
        print(f"  [{count:3d}] {subject} -> {deploy}")

    print(f"\nUnmatched subjects (NO mappings): {len(unmatched)}")
    for subject, count in sorted(unmatched, key=lambda x: -x[1]):
        print(f"  [{count:3d}] {subject}")

    # Calculate skipped counts
    matched_annot_count = sum(count for _, count, _ in matched)
    unmatched_annot_count = sum(count for _, count in unmatched)
    empty_count = subject_counts.get("", 0)

    print("\n--- SUMMARY ---")
    print(f"Annotations with matching subjects: {matched_annot_count}")
    print(f"Annotations without matching subjects: {unmatched_annot_count}")
    print(f"Annotations with empty subjects: {empty_count}")
    print(f"Total skipped (no match + empty): {unmatched_annot_count + empty_count}")


def analyze_annotation_types(annotations: list[dict]):
    """Analyze annotation types to understand what we're dealing with."""
    print(f"\n{'='*80}")
    print("ANNOTATION TYPES ANALYSIS")
    print(f"{'='*80}")

    type_counts = Counter()
    type_with_subjects = Counter()
    type_without_subjects = Counter()

    for annot in annotations:
        annot_type = str(annot.get("/Subtype", "<unknown>"))
        type_counts[annot_type] += 1

        # Check if has subject
        subject = annot.get("/Subject") or annot.get("/Subj") or annot.get("/T") or annot.get("/Contents")
        if subject:
            type_with_subjects[annot_type] += 1
        else:
            type_without_subjects[annot_type] += 1

    print("\nAnnotation types breakdown:")
    for annot_type, count in type_counts.most_common():
        with_subj = type_with_subjects.get(annot_type, 0)
        without_subj = type_without_subjects.get(annot_type, 0)
        print(f"  {annot_type}: {count} total ({with_subj} with subject, {without_subj} without)")


def analyze_btx_subjects(toolchest_dir: Path):
    """Extract subjects from BTX files for comparison."""
    print(f"\n{'='*80}")
    print("BTX FILE SUBJECTS")
    print(f"{'='*80}")

    import zlib
    import re
    from lxml import etree

    def decode_hex_zlib(hex_string: str) -> str | None:
        if not hex_string or not hex_string.lower().startswith("789c"):
            return None
        try:
            compressed = bytes.fromhex(hex_string)
            decompressed = zlib.decompress(compressed)
            return decompressed.decode("utf-8").strip()
        except Exception:
            return None

    def extract_subject_from_raw(raw_content: str) -> str | None:
        if not raw_content:
            return None
        patterns = [
            r"/Subj\(([^)]+)\)",
            r"Subj\(([^)]+)\)",
            r"/Subject\(([^)]+)\)",
        ]
        for pattern in patterns:
            match = re.search(pattern, raw_content)
            if match:
                return match.group(1).strip()
        return None

    # Analyze bid tools
    bid_dir = toolchest_dir / "bidTools"
    deploy_dir = toolchest_dir / "deploymentTools"

    bid_subjects = []
    deploy_subjects = []

    for btx_path in bid_dir.glob("*.btx"):
        print(f"\n  Analyzing: {btx_path.name}")
        content = btx_path.read_bytes()
        if content.startswith(b"\xef\xbb\xbf"):
            content = content[3:]
        root = etree.fromstring(content)

        for item in root.findall(".//ToolChestItem"):
            raw_hex = item.findtext("Raw", "")
            if raw_hex and raw_hex.lower().startswith("789c"):
                raw = decode_hex_zlib(raw_hex)
                subject = extract_subject_from_raw(raw) if raw else None
                if subject:
                    bid_subjects.append(subject)

    for btx_path in deploy_dir.glob("*.btx"):
        print(f"  Analyzing: {btx_path.name}")
        content = btx_path.read_bytes()
        if content.startswith(b"\xef\xbb\xbf"):
            content = content[3:]
        root = etree.fromstring(content)

        for item in root.findall(".//ToolChestItem"):
            raw_hex = item.findtext("Raw", "")
            if raw_hex and raw_hex.lower().startswith("789c"):
                raw = decode_hex_zlib(raw_hex)
                subject = extract_subject_from_raw(raw) if raw else None
                if subject:
                    deploy_subjects.append(subject)

    print(f"\n  Bid tool subjects ({len(bid_subjects)}):")
    for subj in sorted(set(bid_subjects)):
        print(f"    - {subj}")

    print(f"\n  Deployment tool subjects ({len(deploy_subjects)}):")
    for subj in sorted(set(deploy_subjects)):
        print(f"    - {subj}")


def main():
    # Paths
    project_root = Path(__file__).parent.parent.parent
    pdf_path = project_root / "samples" / "maps" / "BidMap.pdf"
    mapping_file = project_root / "backend" / "data" / "mapping.md"
    toolchest_dir = project_root / "toolchest"

    print(f"Project root: {project_root}")
    print(f"PDF path: {pdf_path}")
    print(f"PDF exists: {pdf_path.exists()}")

    if not pdf_path.exists():
        print(f"ERROR: PDF not found at {pdf_path}")
        return

    # Analyze PDF
    annotations = analyze_pdf_annotations(pdf_path)

    # Print detailed info for first 10
    print_annotation_details(annotations, limit=10)

    # Analyze annotation types
    analyze_annotation_types(annotations)

    # Analyze subjects
    subject_counts = analyze_subjects(annotations)

    # Print all unique subjects
    print_subject_counts(subject_counts)

    # Check against mappings
    check_mappings(subject_counts, mapping_file)

    # Analyze BTX files
    analyze_btx_subjects(toolchest_dir)


if __name__ == "__main__":
    main()
