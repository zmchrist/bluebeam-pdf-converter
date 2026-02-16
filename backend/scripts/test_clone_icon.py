"""
Test script for cloning deployment icons from DeploymentMap.pdf.

This script implements the clone-based approach to icon conversion:
1. Extract a deployment icon template from DeploymentMap.pdf
2. Transform its coordinates to match a bid icon position
3. Insert the cloned icon into a copy of BidMap.pdf
4. Verify the icon renders correctly
"""

from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject, DictionaryObject, FloatObject,
    NameObject, StreamObject, TextStringObject,
    NumberObject, DecodedStreamObject
)
import re
import uuid

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEPLOYMENT_PDF = PROJECT_ROOT / "samples" / "maps" / "DeploymentMap.pdf"
BID_PDF = PROJECT_ROOT / "samples" / "maps" / "BidMap.pdf"
OUTPUT_PDF = PROJECT_ROOT / "samples" / "maps" / "test_clone_output.pdf"

# Test subjects
BID_SUBJECT = "Artist - Indoor Wi-Fi Access Point"
DEPLOYMENT_SUBJECT = "AP - Cisco MR36H"  # This exists in DeploymentMap.pdf


def list_deployment_subjects(pdf_path: Path) -> dict:
    """List all unique subjects in the deployment PDF."""
    reader = PdfReader(str(pdf_path))
    page = reader.pages[0]
    annots_ref = page.get('/Annots')

    if not annots_ref:
        return {}

    # Handle IndirectObject
    if hasattr(annots_ref, 'get_object'):
        annots = annots_ref.get_object()
    else:
        annots = annots_ref

    subjects = {}
    for annot_ref in annots:
        try:
            if hasattr(annot_ref, 'get_object'):
                annot = annot_ref.get_object()
            else:
                annot = annot_ref

            subj = str(annot.get('/Subj', annot.get('/Subject', '')))
            if subj and subj not in subjects:
                rect = annot.get('/Rect')
                ap = annot.get('/AP')

                # Get appearance stream info
                ap_info = None
                if ap:
                    ap_n = ap.get('/N')
                    if ap_n:
                        if hasattr(ap_n, 'get_object'):
                            ap_obj = ap_n.get_object()
                        else:
                            ap_obj = ap_n
                        try:
                            stream_data = ap_obj.get_data()
                            ap_info = {
                                'size': len(stream_data),
                                'bbox': ap_obj.get('/BBox'),
                                'matrix': ap_obj.get('/Matrix'),
                            }
                        except:
                            ap_info = {'size': 'unknown'}

                subjects[subj] = {
                    'rect': [float(r) for r in rect] if rect else None,
                    'has_ap': ap is not None,
                    'ap_info': ap_info,
                    'subtype': str(annot.get('/Subtype', '')),
                }
        except Exception as e:
            print(f"  Error reading annotation: {e}")

    return subjects


def find_template_annotation(pdf_path: Path, subject: str):
    """
    Find annotation with given subject and extract it with appearance stream.
    Selects the template with the LARGEST appearance stream (most complete rendering).

    Returns:
        Tuple of (reader, annot_obj, ap_obj) or (None, None, None) if not found
    """
    reader = PdfReader(str(pdf_path))
    page = reader.pages[0]
    annots_ref = page.get('/Annots')

    if not annots_ref:
        return None, None, None

    if hasattr(annots_ref, 'get_object'):
        annots = annots_ref.get_object()
    else:
        annots = annots_ref

    best_annot = None
    best_ap = None
    best_size = 0

    for annot_ref in annots:
        try:
            if hasattr(annot_ref, 'get_object'):
                annot = annot_ref.get_object()
            else:
                annot = annot_ref

            subj = str(annot.get('/Subj', ''))
            if subj == subject:
                ap = annot.get('/AP')
                if ap:
                    ap_n = ap.get('/N')
                    if ap_n:
                        if hasattr(ap_n, 'get_object'):
                            ap_obj = ap_n.get_object()
                        else:
                            ap_obj = ap_n
                        try:
                            stream_size = len(ap_obj.get_data())
                            if stream_size > best_size:
                                best_size = stream_size
                                best_annot = annot
                                best_ap = ap_obj
                        except:
                            pass
        except Exception as e:
            print(f"  Error checking annotation: {e}")

    if best_annot:
        return reader, best_annot, best_ap

    return None, None, None


def find_template_annotation_partial(pdf_path: Path, partial_subject: str):
    """Find annotation with subject containing partial string. Selects largest template."""
    reader = PdfReader(str(pdf_path))
    page = reader.pages[0]
    annots_ref = page.get('/Annots')

    if not annots_ref:
        return None, None, None

    if hasattr(annots_ref, 'get_object'):
        annots = annots_ref.get_object()
    else:
        annots = annots_ref

    best_annot = None
    best_ap = None
    best_size = 0

    for annot_ref in annots:
        try:
            if hasattr(annot_ref, 'get_object'):
                annot = annot_ref.get_object()
            else:
                annot = annot_ref

            subj = str(annot.get('/Subj', ''))
            if partial_subject.lower() in subj.lower():
                ap = annot.get('/AP')
                if ap:
                    ap_n = ap.get('/N')
                    if ap_n:
                        if hasattr(ap_n, 'get_object'):
                            ap_obj = ap_n.get_object()
                        else:
                            ap_obj = ap_n
                        try:
                            stream_size = len(ap_obj.get_data())
                            if stream_size > best_size:
                                best_size = stream_size
                                best_annot = annot
                                best_ap = ap_obj
                        except:
                            pass
        except Exception:
            pass

    if best_annot:
        return reader, best_annot, best_ap

    return None, None, None


def transform_stream_coordinates(stream_bytes: bytes, delta_x: float, delta_y: float) -> bytes:
    """
    Transform absolute coordinates in PDF stream content.

    PDF operators that use coordinates:
    - 'm' (moveto): x y m
    - 'l' (lineto): x y l
    - 'c' (curveto): x1 y1 x2 y2 x3 y3 c
    - 're' (rectangle): x y w h re

    Numbers for colors (rg, RG) and line width (w) should NOT be transformed.

    Note: Stream content may be on single line or multi-line.
    """
    try:
        stream = stream_bytes.decode('latin-1')
    except:
        stream = stream_bytes.decode('utf-8', errors='replace')

    # Transform coordinates using regex on the entire stream
    # Pattern approach: find each operator and transform its coordinates

    # Transform moveto: x y m
    def transform_m(match):
        x, y = float(match.group(1)), float(match.group(2))
        return f'{x + delta_x:.6f} {y + delta_y:.6f} m'

    stream = re.sub(
        r'([\d.]+)\s+([\d.]+)\s+m\b',
        transform_m,
        stream
    )

    # Transform lineto: x y l
    def transform_l(match):
        x, y = float(match.group(1)), float(match.group(2))
        return f'{x + delta_x:.6f} {y + delta_y:.6f} l'

    stream = re.sub(
        r'([\d.]+)\s+([\d.]+)\s+l\b',
        transform_l,
        stream
    )

    # Transform curveto: x1 y1 x2 y2 x3 y3 c
    def transform_c(match):
        coords = [float(match.group(i)) for i in range(1, 7)]
        new_coords = [
            coords[0] + delta_x, coords[1] + delta_y,
            coords[2] + delta_x, coords[3] + delta_y,
            coords[4] + delta_x, coords[5] + delta_y,
        ]
        return f'{new_coords[0]:.6f} {new_coords[1]:.6f} {new_coords[2]:.6f} {new_coords[3]:.6f} {new_coords[4]:.6f} {new_coords[5]:.6f} c'

    stream = re.sub(
        r'([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+c\b',
        transform_c,
        stream
    )

    # Transform rectangle: x y w h re (only x,y, not w,h)
    def transform_re(match):
        x, y, w, h = float(match.group(1)), float(match.group(2)), float(match.group(3)), float(match.group(4))
        return f'{x + delta_x:.6f} {y + delta_y:.6f} {w:.6f} {h:.6f} re'

    stream = re.sub(
        r'([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+re\b',
        transform_re,
        stream
    )

    return stream.encode('latin-1')


def transform_coordinates(
    template_annot: DictionaryObject,
    template_ap: StreamObject,
    target_rect: list,
) -> tuple:
    """
    Transform template annotation coordinates to target position.

    Returns:
        Tuple of (new_annotation_dict, new_appearance_stream)
    """
    # Get template rect
    template_rect = [float(r) for r in template_annot['/Rect']]

    # Calculate delta
    delta_x = target_rect[0] - template_rect[0]
    delta_y = target_rect[1] - template_rect[1]

    print(f"    Template rect: {template_rect}")
    print(f"    Target rect: {target_rect}")
    print(f"    Delta: ({delta_x:.2f}, {delta_y:.2f})")

    # Get template dimensions
    template_width = template_rect[2] - template_rect[0]
    template_height = template_rect[3] - template_rect[1]

    # New rect preserves template size but at target position
    new_rect = [
        target_rect[0],
        target_rect[1],
        target_rect[0] + template_width,
        target_rect[1] + template_height,
    ]

    # Transform stream content
    stream_data = template_ap.get_data()
    print(f"    Original stream size: {len(stream_data)} bytes")

    transformed_stream = transform_stream_coordinates(stream_data, delta_x, delta_y)
    print(f"    Transformed stream size: {len(transformed_stream)} bytes")

    # Create new appearance stream using DecodedStreamObject
    # Note: Do NOT copy /Filter - DecodedStreamObject contains uncompressed data
    # and pypdf will handle compression during write if needed
    new_ap = DecodedStreamObject()
    new_ap._data = transformed_stream

    new_ap[NameObject('/Type')] = NameObject('/XObject')
    new_ap[NameObject('/Subtype')] = NameObject('/Form')
    new_ap[NameObject('/FormType')] = NumberObject(1)

    # New BBox matches new rect
    new_ap[NameObject('/BBox')] = ArrayObject([
        FloatObject(new_rect[0]),
        FloatObject(new_rect[1]),
        FloatObject(new_rect[2]),
        FloatObject(new_rect[3]),
    ])

    # New Matrix offsets to new origin
    new_ap[NameObject('/Matrix')] = ArrayObject([
        NumberObject(1), NumberObject(0),
        NumberObject(0), NumberObject(1),
        FloatObject(-new_rect[0]), FloatObject(-new_rect[1]),
    ])

    # Copy resources
    if '/Resources' in template_ap:
        new_ap[NameObject('/Resources')] = template_ap['/Resources']
    else:
        # Minimal resources
        res = DictionaryObject()
        res[NameObject('/ProcSet')] = ArrayObject([NameObject('/PDF')])
        new_ap[NameObject('/Resources')] = res

    # Create new annotation dictionary
    new_annot = DictionaryObject()
    new_annot[NameObject('/Type')] = NameObject('/Annot')
    new_annot[NameObject('/Subtype')] = template_annot.get('/Subtype', NameObject('/Circle'))
    new_annot[NameObject('/Rect')] = ArrayObject([
        FloatObject(new_rect[0]),
        FloatObject(new_rect[1]),
        FloatObject(new_rect[2]),
        FloatObject(new_rect[3]),
    ])
    new_annot[NameObject('/F')] = NumberObject(4)  # Print flag

    # Copy colors
    if '/IC' in template_annot:
        new_annot[NameObject('/IC')] = template_annot['/IC']
    if '/C' in template_annot:
        new_annot[NameObject('/C')] = template_annot['/C']

    # Copy border style
    if '/BS' in template_annot:
        new_annot[NameObject('/BS')] = template_annot['/BS']

    # Copy rect difference
    if '/RD' in template_annot:
        new_annot[NameObject('/RD')] = template_annot['/RD']

    return new_annot, new_ap


def clone_annotation_to_position(
    writer: PdfWriter,
    page_idx: int,
    template_annot: DictionaryObject,
    template_ap: StreamObject,
    target_rect: list,
    new_subject: str,
) -> None:
    """Clone template annotation to new position on page."""

    # Transform coordinates
    new_annot, new_ap = transform_coordinates(template_annot, template_ap, target_rect)

    # Update subject
    new_annot[NameObject('/Subj')] = TextStringObject(new_subject)

    # Generate unique name
    new_annot[NameObject('/NM')] = TextStringObject(str(uuid.uuid4())[:16].upper())

    # Add appearance stream to PDF and create reference
    ap_ref = writer._add_object(new_ap)
    ap_dict = DictionaryObject()
    ap_dict[NameObject('/N')] = ap_ref
    new_annot[NameObject('/AP')] = ap_dict

    # Add annotation to page
    page = writer.pages[page_idx]
    annots_ref = page.get('/Annots')

    if annots_ref:
        if hasattr(annots_ref, 'get_object'):
            annots = annots_ref.get_object()
        else:
            annots = annots_ref
    else:
        annots = ArrayObject()
        page[NameObject('/Annots')] = annots

    annots.append(new_annot)
    print(f"    Added cloned annotation with subject: {new_subject}")


def main():
    print("=" * 60)
    print("Clone Icon Test")
    print("=" * 60)

    # First, list available subjects in DeploymentMap.pdf
    print("\n1. Scanning DeploymentMap.pdf for available subjects...")
    subjects = list_deployment_subjects(DEPLOYMENT_PDF)

    ap_subjects = [s for s, info in subjects.items() if info['has_ap']]
    print(f"   Found {len(ap_subjects)} subjects with appearance streams:")
    for s in sorted(ap_subjects)[:10]:
        info = subjects[s]
        print(f"     - {s}")
        if info['ap_info']:
            print(f"       Stream size: {info['ap_info'].get('size', 'unknown')} bytes")
    if len(ap_subjects) > 10:
        print(f"     ... and {len(ap_subjects) - 10} more")

    # Find a template with appearance stream
    print(f"\n2. Looking for template: {DEPLOYMENT_SUBJECT}")
    reader, template_annot, template_ap = find_template_annotation(DEPLOYMENT_PDF, DEPLOYMENT_SUBJECT)

    if not template_annot:
        print("   Exact match not found, trying partial match...")
        # Try variations
        for partial in ["MR36H", "9120", "Cisco"]:
            reader, template_annot, template_ap = find_template_annotation_partial(DEPLOYMENT_PDF, partial)
            if template_annot:
                actual_subject = str(template_annot.get('/Subj', ''))
                print(f"   Found: {actual_subject}")
                break

    if not template_annot:
        print("   ERROR: No suitable template found!")
        print("\n   Available subjects:")
        for s in sorted(ap_subjects):
            print(f"     {s}")
        return

    template_rect = [float(r) for r in template_annot['/Rect']]
    stream_size = len(template_ap.get_data())
    print(f"   Template rect: {template_rect}")
    print(f"   AP stream size: {stream_size} bytes")

    # Show stream content sample
    stream_data = template_ap.get_data()
    try:
        stream_text = stream_data.decode('latin-1')
        print("   Stream preview (first 200 chars):")
        print(f"   {stream_text[:200]}...")
    except:
        print("   (binary stream)")

    # Load BidMap.pdf and find target annotation
    print(f"\n3. Loading BidMap.pdf and finding: {BID_SUBJECT}")
    bid_reader = PdfReader(str(BID_PDF))
    writer = PdfWriter()

    # Clone all pages
    for page in bid_reader.pages:
        writer.add_page(page)

    # Find bid annotation
    page = writer.pages[0]
    annots_ref = page.get('/Annots')

    if hasattr(annots_ref, 'get_object'):
        annots = annots_ref.get_object()
    else:
        annots = annots_ref

    target_rect = None
    target_idx = None

    for idx, annot_ref in enumerate(annots):
        try:
            if hasattr(annot_ref, 'get_object'):
                annot = annot_ref.get_object()
            else:
                annot = annot_ref

            subj = str(annot.get('/Subj', ''))
            if subj == BID_SUBJECT:
                target_rect = [float(r) for r in annot['/Rect']]
                target_idx = idx
                print(f"   Found bid annotation at index {idx}")
                print(f"   Bid rect: {target_rect}")
                break
        except Exception as e:
            print(f"   Error checking annotation {idx}: {e}")

    if target_rect is None:
        print(f"   ERROR: Bid annotation '{BID_SUBJECT}' not found!")
        # List available bid subjects
        print("\n   Available bid subjects:")
        for idx, annot_ref in enumerate(annots[:20]):
            try:
                if hasattr(annot_ref, 'get_object'):
                    annot = annot_ref.get_object()
                else:
                    annot = annot_ref
                subj = str(annot.get('/Subj', ''))
                if subj:
                    print(f"     {subj}")
            except:
                pass
        return

    # Remove bid annotation
    print(f"\n4. Removing bid annotation at index {target_idx}...")
    del annots[target_idx]

    # Clone deployment annotation to target position
    print("\n5. Cloning deployment annotation to bid position...")
    clone_annotation_to_position(
        writer, 0, template_annot, template_ap,
        target_rect, DEPLOYMENT_SUBJECT
    )

    # Save output
    print(f"\n6. Saving to: {OUTPUT_PDF}")
    with open(OUTPUT_PDF, 'wb') as f:
        writer.write(f)

    # Verify
    print("\n7. Verifying output...")
    verify_reader = PdfReader(str(OUTPUT_PDF))
    verify_page = verify_reader.pages[0]
    verify_annots = verify_page.get('/Annots')

    if hasattr(verify_annots, 'get_object'):
        verify_annots = verify_annots.get_object()

    found_deployment = False
    for annot_ref in verify_annots:
        try:
            if hasattr(annot_ref, 'get_object'):
                annot = annot_ref.get_object()
            else:
                annot = annot_ref

            subj = str(annot.get('/Subj', ''))
            if DEPLOYMENT_SUBJECT in subj:
                found_deployment = True
                ap = annot.get('/AP')
                has_ap = '/N' in ap if ap else False
                print(f"   Found: {subj}")
                print(f"   Has appearance: {has_ap}")
                break
        except:
            pass

    if found_deployment:
        print("\n" + "=" * 60)
        print("SUCCESS! Clone completed.")
        print("=" * 60)
        print(f"\nOpen {OUTPUT_PDF} to verify the icon renders correctly.")
    else:
        print("\nWARNING: Deployment annotation not found in output!")


if __name__ == "__main__":
    main()
