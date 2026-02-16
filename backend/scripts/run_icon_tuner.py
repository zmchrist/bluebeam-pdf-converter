#!/usr/bin/env python
"""
CLI entry point for icon visual verification and auto-tuning.

Usage:
    python scripts/run_icon_tuner.py compare "AP - Cisco MR36H"
    python scripts/run_icon_tuner.py compare --category APs
    python scripts/run_icon_tuner.py compare --all
    python scripts/run_icon_tuner.py tune "AP - Cisco MR36H"
    python scripts/run_icon_tuner.py tune --category APs
    python scripts/run_icon_tuner.py tune --all
    python scripts/run_icon_tuner.py extract-regions
    python scripts/run_icon_tuner.py extract-colors
"""

import argparse
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.icon_config import get_icon_config, ICON_CATEGORIES
from scripts.icon_tuner.auto_tuner import (
    auto_tune_icon,
    extract_dominant_circle_color,
    generate_proposed_config,
)
from scripts.icon_tuner.icon_comparator import (
    compute_similarity,
    create_comparison_image,
    render_icon_to_image,
)
from scripts.icon_tuner.reference_extractor import (
    extract_all_reference_icons,
    extract_reference_icons,
    save_annotated_reference,
)
from scripts.icon_tuner.region_config import (
    REFERENCE_PDF_DIR,
    REFERENCE_REGIONS,
    get_all_subjects,
)

OUTPUT_DIR = Path(__file__).parent / "icon_tuner_output"
COMPARISONS_DIR = OUTPUT_DIR / "comparisons"
REPORTS_DIR = OUTPUT_DIR / "reports"


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )


def ensure_output_dirs():
    """Create output directories."""
    COMPARISONS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def get_subjects_for_category(category: str) -> list[str]:
    """Get all subjects in a given category that have reference PDFs."""
    all_ref_subjects = set(get_all_subjects())
    return [
        subj for subj, cat in ICON_CATEGORIES.items()
        if cat == category and subj in all_ref_subjects
    ]


def cmd_compare(args):
    """Compare generated icons against reference."""
    ensure_output_dirs()

    # Determine which subjects to compare
    subjects: list[str] = []
    if args.all:
        subjects = get_all_subjects()
    elif args.category:
        subjects = get_subjects_for_category(args.category)
        if not subjects:
            print(f"No reference icons found for category: {args.category}")
            return
    elif args.subject:
        subjects = [args.subject]
    else:
        print("Specify a subject, --category, or --all")
        return

    # Extract all needed reference icons
    print(f"Comparing {len(subjects)} icon(s)...")
    ref_icons = extract_all_reference_icons()

    results: list[dict] = []

    for subject in subjects:
        ref_img = ref_icons.get(subject)
        if ref_img is None:
            print(f"  SKIP {subject}: no reference image")
            continue

        gen_img = render_icon_to_image(subject)
        if gen_img is None:
            print(f"  SKIP {subject}: cannot render")
            continue

        scores = compute_similarity(ref_img, gen_img)
        combined = scores["combined"]

        status = "OK" if combined >= 0.7 else "LOW"
        print(
            f"  [{status}] {subject}: combined={combined:.3f} "
            f"nmae={scores['nmae']:.3f} hist={scores['histogram']:.3f}"
        )

        # Save comparison image
        comp_img = create_comparison_image(ref_img, gen_img, subject, scores)
        safe_name = subject.replace(" ", "_").replace("-", "_").replace("/", "_")
        comp_path = COMPARISONS_DIR / f"compare_{safe_name}.png"
        comp_img.save(comp_path)

        results.append({
            "subject": subject,
            "combined": combined,
            "nmae": scores["nmae"],
            "histogram": scores["histogram"],
            "region_avg": scores["region_avg"],
        })

    # Summary
    if results:
        avg_combined = sum(r["combined"] for r in results) / len(results)
        print("\n--- Summary ---")
        print(f"Icons compared: {len(results)}")
        print(f"Average combined score: {avg_combined:.3f}")
        print(f"Comparison images saved to: {COMPARISONS_DIR}")

        # Save report
        report_path = REPORTS_DIR / "comparison_report.txt"
        with open(report_path, "w") as f:
            f.write("Icon Comparison Report\n")
            f.write("=" * 60 + "\n\n")
            for r in sorted(results, key=lambda x: x["combined"]):
                f.write(
                    f"{r['subject']}: combined={r['combined']:.3f} "
                    f"nmae={r['nmae']:.3f} hist={r['histogram']:.3f} "
                    f"region={r['region_avg']:.3f}\n"
                )
            f.write(f"\nAverage: {avg_combined:.3f}\n")
        print(f"Report saved to: {report_path}")


def cmd_tune(args):
    """Auto-tune icon parameters."""
    ensure_output_dirs()

    # Determine subjects
    subjects: list[str] = []
    if args.all:
        subjects = get_all_subjects()
    elif args.category:
        subjects = get_subjects_for_category(args.category)
        if not subjects:
            print(f"No reference icons found for category: {args.category}")
            return
    elif args.subject:
        subjects = [args.subject]
    else:
        print("Specify a subject, --category, or --all")
        return

    print(f"Auto-tuning {len(subjects)} icon(s)...")
    ref_icons = extract_all_reference_icons()

    all_results: dict[str, tuple[dict, list[dict]]] = {}

    for subject in subjects:
        ref_img = ref_icons.get(subject)
        if ref_img is None:
            print(f"  SKIP {subject}: no reference image")
            continue

        config = get_icon_config(subject)
        if not config:
            print(f"  SKIP {subject}: no config")
            continue

        print(f"\n  Tuning: {subject}")
        proposed, history = auto_tune_icon(
            subject, ref_img, config,
            threshold=args.threshold,
        )

        if history:
            baseline = history[0]["score"]
            final = history[-1]["score"]
            improvement = final - baseline
            print(f"    Score: {baseline:.3f} -> {final:.3f} ({improvement:+.3f})")
        else:
            print("    No improvement found")

        all_results[subject] = (proposed, history)

        # Save before/after comparison
        gen_img = render_icon_to_image(subject, config_override=proposed)
        if gen_img and ref_img:
            scores = compute_similarity(ref_img, gen_img)
            comp_img = create_comparison_image(ref_img, gen_img, subject, scores)
            safe_name = subject.replace(" ", "_").replace("-", "_").replace("/", "_")
            comp_path = COMPARISONS_DIR / f"tuned_{safe_name}.png"
            comp_img.save(comp_path)

    # Generate proposed config
    if all_results:
        config_code = generate_proposed_config(all_results)
        config_path = OUTPUT_DIR / "proposed_overrides.py"
        with open(config_path, "w") as f:
            f.write(config_code)

        print("\n--- Summary ---")
        print(f"Icons tuned: {len(all_results)}")
        print(f"Proposed config saved to: {config_path}")
        print(f"Comparison images saved to: {COMPARISONS_DIR}")


def cmd_extract_regions(args):
    """Debug: save annotated reference images showing detected regions."""
    ensure_output_dirs()

    print("Extracting regions from reference PDFs...")
    for pdf_name in REFERENCE_REGIONS:
        pdf_path = REFERENCE_PDF_DIR / pdf_name
        if not pdf_path.exists():
            print(f"  SKIP {pdf_name}: file not found")
            continue

        output_path = save_annotated_reference(pdf_path, OUTPUT_DIR)

        entries = REFERENCE_REGIONS[pdf_name]
        icons = extract_reference_icons(pdf_path)

        print(f"  {pdf_name}: expected {len(entries)}, extracted {len(icons)}")
        print(f"    Saved: {output_path}")

        # Also save individual crops
        crops_dir = OUTPUT_DIR / "crops" / pdf_name.replace(".pdf", "")
        crops_dir.mkdir(parents=True, exist_ok=True)
        for subject, img in icons.items():
            safe_name = subject.replace(" ", "_").replace("-", "_").replace("/", "_")
            img.save(crops_dir / f"{safe_name}.png")


def cmd_extract_colors(args):
    """Extract circle colors from all reference PDFs."""
    ensure_output_dirs()

    print("Extracting circle colors from reference icons...")
    ref_icons = extract_all_reference_icons()

    results: dict[str, tuple[float, float, float]] = {}

    for subject, ref_img in sorted(ref_icons.items()):
        color = extract_dominant_circle_color(ref_img)
        results[subject] = color

        # Get current config color for comparison
        config = get_icon_config(subject)
        current = config.get("circle_color", (0, 0, 0)) if config else (0, 0, 0)

        # Check if different
        diff = sum(abs(a - b) for a, b in zip(color, current))
        marker = " ***" if diff > 0.15 else ""

        print(f"  {subject}:")
        print(f"    Reference: ({color[0]:.4f}, {color[1]:.4f}, {color[2]:.4f})")
        print(f"    Current:   ({current[0]:.4f}, {current[1]:.4f}, {current[2]:.4f}){marker}")

    # Save report
    report_path = REPORTS_DIR / "color_extraction.txt"
    with open(report_path, "w") as f:
        f.write("Color Extraction Report\n")
        f.write("=" * 60 + "\n\n")
        for subject, color in sorted(results.items()):
            config = get_icon_config(subject)
            current = config.get("circle_color", (0, 0, 0)) if config else (0, 0, 0)
            diff = sum(abs(a - b) for a, b in zip(color, current))
            marker = " *** MISMATCH" if diff > 0.15 else ""
            f.write(
                f"{subject}: ref=({color[0]:.4f}, {color[1]:.4f}, {color[2]:.4f}) "
                f"cur=({current[0]:.4f}, {current[1]:.4f}, {current[2]:.4f}){marker}\n"
            )
    print(f"\nReport saved to: {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Icon visual verification and auto-tuning tool",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # compare
    compare_parser = subparsers.add_parser("compare", help="Compare icons against reference")
    compare_parser.add_argument("subject", nargs="?", help="Icon subject to compare")
    compare_parser.add_argument("--category", help="Compare all icons in category")
    compare_parser.add_argument("--all", action="store_true", help="Compare all icons")
    compare_parser.set_defaults(func=cmd_compare)

    # tune
    tune_parser = subparsers.add_parser("tune", help="Auto-tune icon parameters")
    tune_parser.add_argument("subject", nargs="?", help="Icon subject to tune")
    tune_parser.add_argument("--category", help="Tune all icons in category")
    tune_parser.add_argument("--all", action="store_true", help="Tune all icons")
    tune_parser.add_argument(
        "--threshold", type=float, default=0.85,
        help="Target combined score (default: 0.85)",
    )
    tune_parser.set_defaults(func=cmd_tune)

    # extract-regions
    regions_parser = subparsers.add_parser(
        "extract-regions", help="Debug: save annotated reference images",
    )
    regions_parser.set_defaults(func=cmd_extract_regions)

    # extract-colors
    colors_parser = subparsers.add_parser(
        "extract-colors", help="Extract circle colors from references",
    )
    colors_parser.set_defaults(func=cmd_extract_colors)

    args = parser.parse_args()
    setup_logging(args.verbose)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
