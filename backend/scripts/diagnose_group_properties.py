#!/usr/bin/env python
"""
Compare native Bluebeam icon group properties vs converter output.

Usage:
    uv run python scripts/diagnose_group_properties.py [converter_output.pdf]

If no converter output is provided, only analyzes the native DeploymentMap.pdf.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from pypdf import PdfReader  # noqa: E402


def dump_group_properties(pdf_path: Path, target_subject: str = "AP - Cisco MR36H"):
    """Find and dump all properties of one compound annotation group."""
    reader = PdfReader(pdf_path)
    print(f"\n{'='*80}")
    print(f"PDF: {pdf_path.name}")
    print(f"Looking for group: {target_subject}")
    print(f"{'='*80}")

    for page_num, page in enumerate(reader.pages):
        annots = page.get("/Annots", [])
        group_annots = []

        for annot_ref in annots:
            annot = annot_ref.get_object()
            subj = str(annot.get("/Subj", ""))
            if subj == target_subject:
                group_annots.append(annot)

        if not group_annots:
            continue

        print(f"\nPage {page_num + 1}: Found {len(group_annots)} annotations")

        # Sort: root first (no /IRT), then children
        roots = [a for a in group_annots if a.get("/IRT") is None]
        children = [a for a in group_annots if a.get("/IRT") is not None]

        for idx, annot in enumerate(roots + children):
            is_root = annot.get("/IRT") is None
            subtype = str(annot.get("/Subtype", "?"))
            role = "ROOT" if is_root else "CHILD"
            print(f"\n  --- {role} #{idx + 1} ({subtype}) ---")

            for key in sorted(annot.keys()):
                value = annot[key]
                value_str = str(value)
                if len(value_str) > 150:
                    value_str = value_str[:150] + "..."
                print(f"    {key}: {value_str}")

        # Only analyze first group found
        break


def main():
    project_root = Path(__file__).parent.parent.parent

    # Native Bluebeam reference
    native_pdf = project_root / "samples" / "maps" / "DeploymentMap.pdf"
    if native_pdf.exists():
        dump_group_properties(native_pdf)
    else:
        print(f"WARNING: Native reference not found: {native_pdf}")

    # Converter output (optional argument)
    if len(sys.argv) > 1:
        converter_pdf = Path(sys.argv[1])
        if converter_pdf.exists():
            dump_group_properties(converter_pdf)
        else:
            print(f"ERROR: Converter output not found: {converter_pdf}")


if __name__ == "__main__":
    main()
