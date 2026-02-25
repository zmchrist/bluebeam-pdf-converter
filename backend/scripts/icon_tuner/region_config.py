"""
Region configuration for reference PDF icon extraction.

Maps each reference PDF to an ordered list of deployment subjects
matching the visual order (left-to-right, top-to-bottom) as they
appear in the reference deployment PDFs.
"""

from pathlib import Path

# Base paths
_THIS_FILE = Path(__file__).resolve()
_SCRIPTS_DIR = _THIS_FILE.parent.parent
_BACKEND_DIR = _SCRIPTS_DIR.parent
_PROJECT_ROOT = _BACKEND_DIR.parent

REFERENCE_PDF_DIR = _PROJECT_ROOT / "samples" / "icons" / "deploymentIcons"

# Maps PDF filename -> list of (subject, optional_crop_box) tuples
# Order: left-to-right, top-to-bottom as they appear in the reference PDF
# crop_box format: (x1, y1, x2, y2) in pixels at 300 DPI, or None for auto-detect
REFERENCE_REGIONS: dict[str, list[tuple[str, tuple[int, int, int, int] | None]]] = {
    "accessPoints.pdf": [
        ("AP - Cisco MR36H", None),
        ("AP - Cisco MR78", None),
        ("AP - Cisco 9166I", None),
        ("AP - Cisco 9166D", None),
        ("AP - Cisco 9120", None),
        ("AP - Cisco Marlin 4", None),
        ("AP - Cisco DB10", None),
    ],
    "switches.pdf": [
        # Row 1 (8 icons)
        ("SW - Cisco Micro 4P", None),
        ("SW - Fortinet 108F 8P", None),
        ("SW - Cisco 9200 12P", None),
        ("SW - Cisco 9300X 24X", None),
        ("SW - Cisco 9300 12X36M", None),
        ("SW - Cisco 9300X 24Y", None),
        ("SW - Cisco 9500 48Y4C", None),
        # Row 2: IDFs
        ("SW - IDF Cisco 9300 24X", None),
        ("SW - IDF Cisco 9300X 24X", None),
        ("SW - IDF Cisco 9300 12X36M", None),
        ("SW - IDF Cisco 9300X 24Y", None),
        ("SW - IDF Cisco 9500 48Y4C", None),
        # Row 3: NOCs/Distribution
        ("DIST - Starlink", None),
        ("DIST - Micro NOC", None),
        ("DIST - Standard NOC", None),
        ("DIST - MikroTik Hex", None),
    ],
    "hardlines.pdf": [
        ("HL - Access Control", None),
        ("HL - Artist", None),
        ("HL - Audio", None),
        ("HL - CCTV", None),
        ("HL - Clair", None),
        ("HL - Emergency Announce System", None),
        ("HL - General Internet", None),
        ("HL - IPTV", None),
        ("HL - Lighting", None),
        ("HL - Media", None),
        ("HL - PoS", None),
        ("HL - Production", None),
        ("HL - Radios", None),
        ("HL - Sponsor", None),
        ("HL - Streaming", None),
        ("HL - Video", None),
        ("HL - WAN", None),
        # Fiber types
        ("HL - LC Fiber", None),
        ("HL - SC Fiber", None),
        ("HL - ST Fiber", None),
    ],
    "p2p.pdf": [
        ("P2P - Ubiquiti NanoBeam", None),
        ("P2P - Ubiquiti LiteAP", None),
        ("P2P - Ubiquiti Wave Nano", None),
        ("P2P - Ubiquiti Wave Pico", None),
        ("P2P - Ubiquiti Wave AP Micro", None),
        ("P2P - Ubiquiti GigaBeam", None),
        ("P2P - Ubiquiti GigaBeam LR", None),
    ],
    "cameras.pdf": [
        ("CCTV - Cisco MV93X", None),
        ("CCTV - AXIS P5655-E", None),
        ("CCTV - AXIS M5526-E", None),
        ("CCTV - AXIS S9302", None),
    ],
}


def get_all_subjects() -> list[str]:
    """Get flat list of all subjects across all reference PDFs."""
    subjects = []
    for entries in REFERENCE_REGIONS.values():
        for subject, _ in entries:
            subjects.append(subject)
    return subjects


def get_subjects_for_pdf(pdf_name: str) -> list[str]:
    """Get ordered list of subjects for a given reference PDF."""
    entries = REFERENCE_REGIONS.get(pdf_name, [])
    return [subject for subject, _ in entries]


def get_reference_pdf_for_subject(subject: str) -> str | None:
    """Find which reference PDF contains a given subject."""
    for pdf_name, entries in REFERENCE_REGIONS.items():
        for entry_subject, _ in entries:
            if entry_subject == subject:
                return pdf_name
    return None
