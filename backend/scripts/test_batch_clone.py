"""
Batch clone conversion test.

Converts all bid icons in BidMap.pdf to deployment icons by cloning
templates from DeploymentMap.pdf.
"""

from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import (
    ArrayObject, DictionaryObject, FloatObject,
    NameObject, TextStringObject, NumberObject,
    DecodedStreamObject
)
import re
import uuid

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEPLOYMENT_PDF = PROJECT_ROOT / "samples" / "maps" / "DeploymentMap.pdf"
BID_PDF = PROJECT_ROOT / "samples" / "maps" / "BidMap.pdf"
OUTPUT_PDF = PROJECT_ROOT / "samples" / "maps" / "test_batch_clone_output.pdf"

# Mapping from bid subjects to deployment subjects
# This should match mapping.md but for available templates
BID_TO_DEPLOYMENT = {
    # Access Points
    "Artist - Indoor Wi-Fi Access Point": "AP - Cisco MR36H",
    "Production - Indoor Wi-Fi Access Point": "AP - Cisco MR36H",
    "Production - Medium Density Wi-Fi Access Point": "AP - Cisco 9166I",
    "Production - Medium Density Directional Wi-Fi Access Point": "AP - Cisco 9166D",
    "Point-of-Sale - Indoor Wi-Fi Access Point": "AP - Cisco MR36H",
    "Point-of-Sale - Outdoor Wi-Fi Access Point": "AP - Cisco MR36H",
    "Access Control - Indoor Wi-Fi Access Point": "AP - Cisco MR36H",
    "Access Control - Outdoor Wi-Fi Access Point": "AP - Cisco MR36H",
    "High Density - Wi-Fi Access Point": "AP - Cisco 9166I",
    "High Density - Stadium Wi-Fi Access Point": "AP - Cisco 9166D",

    # Switches
    "Distribution - Edge Switch": "SW - Cisco 9200 12P",
    "Distribution - Compact Edge Switch": "SW - Cisco Micro 4P",
    "Distribution - Clair Custom IDF Rack": "SW - IDF Cisco 9300 24X",
    "Distribution - Clair Network Core Rack Compact": "DIST - Micro NOC",
    "Distribution - Cellular Gateway": "Distribution - Cellular Gateway",
    "Distribution - ISP": "Distribution - ISP",

    # Hardlines
    "Ethernet Hardline": "HL - General Internet",
    "AV - Ethernet Hardline": "HL - Audio",
    "Emergency Announce - Ethernet Hardline": "HL - Emergency Announce System",
    "High Capacity - Ethernet Hardline": "HL - General Internet",
    "Point-of-Sale - Ethernet Hardline": "HL - PoS",

    # Other
    "Fiber Junction": "BOX - Zarges Box",
}


def transform_stream_coordinates(stream_bytes: bytes, delta_x: float, delta_y: float) -> bytes:
    """Transform coordinates in PDF stream content."""
    try:
        stream = stream_bytes.decode('latin-1')
    except:
        stream = stream_bytes.decode('utf-8', errors='replace')

    # Transform moveto: x y m
    def transform_m(match):
        x, y = float(match.group(1)), float(match.group(2))
        return f'{x + delta_x:.6f} {y + delta_y:.6f} m'

    stream = re.sub(r'([\d.]+)\s+([\d.]+)\s+m\b', transform_m, stream)

    # Transform lineto: x y l
    def transform_l(match):
        x, y = float(match.group(1)), float(match.group(2))
        return f'{x + delta_x:.6f} {y + delta_y:.6f} l'

    stream = re.sub(r'([\d.]+)\s+([\d.]+)\s+l\b', transform_l, stream)

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

    # Transform rectangle: x y w h re
    def transform_re(match):
        x, y, w, h = float(match.group(1)), float(match.group(2)), float(match.group(3)), float(match.group(4))
        return f'{x + delta_x:.6f} {y + delta_y:.6f} {w:.6f} {h:.6f} re'

    stream = re.sub(
        r'([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+re\b',
        transform_re,
        stream
    )

    return stream.encode('latin-1')


def load_deployment_templates(pdf_path: Path) -> dict:
    """Load all deployment annotation templates from PDF."""
    reader = PdfReader(str(pdf_path))
    page = reader.pages[0]
    annots_ref = page.get('/Annots')

    if hasattr(annots_ref, 'get_object'):
        annots = annots_ref.get_object()
    else:
        annots = annots_ref

    templates = {}

    for annot_ref in annots:
        try:
            if hasattr(annot_ref, 'get_object'):
                annot = annot_ref.get_object()
            else:
                annot = annot_ref

            subj = str(annot.get('/Subj', ''))
            if not subj:
                continue

            ap = annot.get('/AP')
            if not ap:
                continue

            ap_n = ap.get('/N')
            if not ap_n:
                continue

            if hasattr(ap_n, 'get_object'):
                ap_obj = ap_n.get_object()
            else:
                ap_obj = ap_n

            try:
                stream = ap_obj.get_data()
                stream_size = len(stream)

                # Keep the largest template for each subject
                if subj not in templates or stream_size > len(templates[subj]['stream']):
                    templates[subj] = {
                        'annot': annot,
                        'ap': ap_obj,
                        'stream': stream,
                        'rect': [float(r) for r in annot.get('/Rect', [])],
                    }
            except:
                pass
        except:
            pass

    return templates


def clone_annotation(
    writer: PdfWriter,
    template: dict,
    target_rect: list,
    new_subject: str,
) -> DictionaryObject:
    """Clone template annotation to new position."""
    template_annot = template['annot']
    template_ap = template['ap']
    template_rect = template['rect']

    # Calculate delta
    delta_x = target_rect[0] - template_rect[0]
    delta_y = target_rect[1] - template_rect[1]

    # Get template dimensions
    template_width = template_rect[2] - template_rect[0]
    template_height = template_rect[3] - template_rect[1]

    # New rect preserves template size at target position
    new_rect = [
        target_rect[0],
        target_rect[1],
        target_rect[0] + template_width,
        target_rect[1] + template_height,
    ]

    # Transform stream content
    stream_data = template['stream']
    transformed_stream = transform_stream_coordinates(stream_data, delta_x, delta_y)

    # Create new appearance stream
    new_ap = DecodedStreamObject()
    new_ap._data = transformed_stream

    new_ap[NameObject('/Type')] = NameObject('/XObject')
    new_ap[NameObject('/Subtype')] = NameObject('/Form')
    new_ap[NameObject('/FormType')] = NumberObject(1)
    new_ap[NameObject('/BBox')] = ArrayObject([
        FloatObject(new_rect[0]), FloatObject(new_rect[1]),
        FloatObject(new_rect[2]), FloatObject(new_rect[3]),
    ])
    new_ap[NameObject('/Matrix')] = ArrayObject([
        NumberObject(1), NumberObject(0), NumberObject(0), NumberObject(1),
        FloatObject(-new_rect[0]), FloatObject(-new_rect[1]),
    ])

    # Copy or create resources
    if '/Resources' in template_ap:
        new_ap[NameObject('/Resources')] = template_ap['/Resources']
    else:
        res = DictionaryObject()
        res[NameObject('/ProcSet')] = ArrayObject([NameObject('/PDF')])
        new_ap[NameObject('/Resources')] = res

    # Add appearance to PDF
    ap_ref = writer._add_object(new_ap)

    # Create annotation dictionary
    new_annot = DictionaryObject()
    new_annot[NameObject('/Type')] = NameObject('/Annot')
    new_annot[NameObject('/Subtype')] = template_annot.get('/Subtype', NameObject('/Circle'))
    new_annot[NameObject('/Rect')] = ArrayObject([
        FloatObject(new_rect[0]), FloatObject(new_rect[1]),
        FloatObject(new_rect[2]), FloatObject(new_rect[3]),
    ])
    new_annot[NameObject('/Subj')] = TextStringObject(new_subject)
    new_annot[NameObject('/NM')] = TextStringObject(str(uuid.uuid4())[:16].upper())
    new_annot[NameObject('/F')] = NumberObject(4)

    # Copy colors
    if '/IC' in template_annot:
        new_annot[NameObject('/IC')] = template_annot['/IC']
    if '/C' in template_annot:
        new_annot[NameObject('/C')] = template_annot['/C']
    if '/BS' in template_annot:
        new_annot[NameObject('/BS')] = template_annot['/BS']

    # Set appearance
    ap_dict = DictionaryObject()
    ap_dict[NameObject('/N')] = ap_ref
    new_annot[NameObject('/AP')] = ap_dict

    return new_annot


def main():
    print("=" * 60)
    print("Batch Clone Conversion Test")
    print("=" * 60)

    # Load deployment templates
    print(f"\n1. Loading deployment templates from DeploymentMap.pdf...")
    templates = load_deployment_templates(DEPLOYMENT_PDF)
    print(f"   Loaded {len(templates)} unique templates")

    # Load BidMap and create writer
    print(f"\n2. Loading BidMap.pdf...")
    bid_reader = PdfReader(str(BID_PDF))
    writer = PdfWriter()
    for page in bid_reader.pages:
        writer.add_page(page)

    # Get page annotations
    page = writer.pages[0]
    annots_ref = page.get('/Annots')
    if hasattr(annots_ref, 'get_object'):
        annots = annots_ref.get_object()
    else:
        annots = annots_ref

    # Find all bid annotations to convert
    print(f"\n3. Finding bid annotations to convert...")
    total_annotations = len(annots)
    to_convert = []

    for idx, annot_ref in enumerate(annots):
        try:
            if hasattr(annot_ref, 'get_object'):
                annot = annot_ref.get_object()
            else:
                annot = annot_ref

            bid_subj = str(annot.get('/Subj', ''))
            if bid_subj in BID_TO_DEPLOYMENT:
                deploy_subj = BID_TO_DEPLOYMENT[bid_subj]
                if deploy_subj in templates:
                    rect = [float(r) for r in annot.get('/Rect', [])]
                    to_convert.append({
                        'idx': idx,
                        'bid_subject': bid_subj,
                        'deploy_subject': deploy_subj,
                        'rect': rect,
                    })
        except:
            pass

    print(f"   Total annotations: {total_annotations}")
    print(f"   To convert: {len(to_convert)}")

    # Convert annotations (remove old, add new)
    print(f"\n4. Converting annotations...")
    converted = 0
    skipped = 0

    # Process in reverse order so indices remain valid when deleting
    for item in sorted(to_convert, key=lambda x: -x['idx']):
        try:
            # Get template
            template = templates[item['deploy_subject']]

            # Clone annotation
            new_annot = clone_annotation(
                writer,
                template,
                item['rect'],
                item['deploy_subject'],
            )

            # Remove old annotation
            del annots[item['idx']]

            # Add new annotation
            annots.append(new_annot)

            converted += 1
        except Exception as e:
            print(f"   Error converting {item['bid_subject']}: {e}")
            skipped += 1

    print(f"   Converted: {converted}")
    print(f"   Skipped: {skipped}")

    # Breakdown by type
    print(f"\n   By type:")
    by_type = {}
    for item in to_convert:
        t = item['deploy_subject']
        if t not in by_type:
            by_type[t] = 0
        by_type[t] += 1
    for t, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"     {t}: {count}")

    # Save output
    print(f"\n5. Saving to {OUTPUT_PDF}...")
    with open(OUTPUT_PDF, 'wb') as f:
        writer.write(f)

    # Verify
    print(f"\n6. Verifying output...")
    verify_reader = PdfReader(str(OUTPUT_PDF))
    verify_page = verify_reader.pages[0]
    verify_annots = verify_page.get('/Annots')
    if hasattr(verify_annots, 'get_object'):
        verify_annots = verify_annots.get_object()

    deploy_count = 0
    deploy_with_ap = 0
    for annot_ref in verify_annots:
        try:
            annot = annot_ref.get_object() if hasattr(annot_ref, 'get_object') else annot_ref
            subj = str(annot.get('/Subj', ''))
            # Check if it's a deployment subject (starts with deployment prefixes)
            if any(subj.startswith(p) for p in ['AP -', 'SW -', 'HL -', 'DIST -', 'BOX -', 'P2P -', 'Distribution -']):
                deploy_count += 1
                ap = annot.get('/AP')
                if ap and ap.get('/N'):
                    deploy_with_ap += 1
        except:
            pass

    print(f"   Deployment icons found: {deploy_count}")
    print(f"   With appearance stream: {deploy_with_ap}")

    print("\n" + "=" * 60)
    print("BATCH CONVERSION COMPLETE!")
    print("=" * 60)
    print(f"\nOpen {OUTPUT_PDF} to verify the icons render correctly.")


if __name__ == "__main__":
    main()
