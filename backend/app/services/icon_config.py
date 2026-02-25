"""
Icon configuration module.

Provides configuration data for rendering deployment icons including:
- Category mappings for deployment subjects
- Category-level default rendering parameters
- Per-icon override configurations
- Image path mappings
- Helper functions for config retrieval
"""

from pathlib import Path
from typing import Literal, TypedDict


class IdPrefixConfig(TypedDict, total=False):
    """Type definition for ID prefix configuration entries."""

    prefix: str  # Required: The prefix letter(s) for the ID (e.g., "j", "aa")
    start: int  # Required: Starting number for the counter (e.g., 100)
    format: Literal["prefix_first", "number_first"]  # Optional: ID format

# Base paths - use absolute paths relative to this file's location
# This file is at: backend/app/services/icon_config.py
# Project root is 3 levels up: backend/app/services -> backend/app -> backend -> project_root
_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parent.parent.parent.parent  # Go up to project root

SAMPLES_ICONS_DIR = _PROJECT_ROOT / "samples" / "icons"
GEAR_ICONS_DIR = SAMPLES_ICONS_DIR / "gearIcons"
DEPLOYMENT_ICONS_DIR = SAMPLES_ICONS_DIR / "deploymentIcons"

# Category subdirectories in gearIcons/
GEAR_ICON_CATEGORIES = {
    "APs": GEAR_ICONS_DIR / "APs",
    "Switches": GEAR_ICONS_DIR / "Switches",
    "P2Ps": GEAR_ICONS_DIR / "P2Ps",
    "Hardlines": GEAR_ICONS_DIR / "Hardlines",
    "Hardware": GEAR_ICONS_DIR / "Hardware",
    "Misc": GEAR_ICONS_DIR / "Misc",
}


# Maps deployment subjects to their categories
ICON_CATEGORIES: dict[str, str] = {
    # === Access Points ===
    "AP - Cisco MR36H": "APs",
    "AP - Cisco 9120": "APs",
    "AP - Cisco 9166I": "APs",
    "AP - Cisco 9166D": "APs",
    "AP - Cisco MR78": "APs",
    "AP - Cisco Marlin 4": "APs",
    "AP - Cisco DB10": "APs",
    # === Switches ===
    "SW - Cisco Micro 4P": "Switches",
    "SW - Cisco 9200 12P": "Switches",
    "SW - IDF Cisco 9300 24X": "Switches",
    # === Distribution ===
    "DIST - Mini NOC": "Switches",
    "DIST - Micro NOC": "Switches",
    "DIST - Standard NOC": "Switches",
    "DIST - Pelican NOC": "Switches",
    "DIST - MikroTik Hex": "Switches",
    "DIST - Starlink": "Switches",
    # === Additional Switches ===
    "DIST - Cisco MX": "Switches",
    "DIST - Fortinet FortiGate": "Switches",
    "DIST - Mega NOC": "Switches",
    "SW - 1G 60W PoE Extender": "Switches",
    "SW - 1G PoE+ Injectors": "Switches",
    "SW - 1G PoE+ Media Converter": "Switches",
    "SW - Cisco 9300 12X36M": "Switches",
    "SW - Cisco 9300X 24X": "Switches",
    "SW - Cisco 9300X 24Y": "Switches",
    "SW - Cisco 9500 48Y4C": "Switches",
    "SW - Fortinet 108F 8P": "Switches",
    "SW - IDF Cisco 9300 12X36M": "Switches",
    "SW - IDF Cisco 9300X 24X": "Switches",
    "SW - IDF Cisco 9300X 24Y": "Switches",
    "SW - IDF Cisco 9500 48Y4C": "Switches",
    "SW - Raspberry Pi": "Switches",
    # === Point-to-Points ===
    "P2P - Ubiquiti NanoBeam": "P2Ps",
    "P2P - Ubiquiti LiteAP": "P2Ps",
    "P2P - Ubiquiti GigaBeam": "P2Ps",
    "P2P - Ubiquiti GigaBeam LR": "P2Ps",
    # === Additional Point-to-Points ===
    "P2P - Ubiquiti Wave AP Micro": "P2Ps",
    "P2P - Ubiquiti Wave Nano": "P2Ps",
    "P2P - Ubiquiti Wave Pico": "P2Ps",
    # === IoT / VoIP ===
    "VOIP - Yealink T29G": "IoT",
    "VOIP - Yealink CP965": "IoT",
    # === CCTV / Cameras ===
    "CCTV - AXIS P5655-E": "Cameras",
    "CCTV - AXIS S9302": "Cameras",
    # === IoT / Emergency Announce ===
    "EAS - Command Unit": "IoT",
    "EAS - Laptop": "IoT",
    "EAS - Trigger Box": "IoT",
    # === IoT / IPTV ===
    "IPTV - BrightSign XT1144": "IoT",
    # === Additional CCTV / Cameras ===
    "CCTV - AXIS M5526-E": "Cameras",
    "CCTV - Cisco MV93X": "Cameras",
    # === IoT / Sensors ===
    "SEN - Meraki MT15": "IoT",
    "SEN - Meraki MT40": "IoT",
    # === Hardlines (all use same image, different model text) ===
    "HL - Artist": "Hardlines",
    "HL - Production": "Hardlines",
    "HL - PoS": "Hardlines",
    "HL - Access Control": "Hardlines",
    "HL - Sponsor": "Hardlines",
    "HL - General Internet": "Hardlines",
    "HL - Audio": "Hardlines",
    "HL - Emergency Announce System": "Hardlines",
    "HL - WAN": "Hardlines",
    # === Additional Hardlines (copper) ===
    "HL -": "Hardlines",  # Empty suffix variant
    "HL - CCTV": "Hardlines",
    "HL - Clair": "Hardlines",
    "HL - IPTV": "Hardlines",
    "HL - Lighting": "Hardlines",
    "HL - Media": "Hardlines",
    "HL - Radios": "Hardlines",
    "HL - Streaming": "Hardlines",
    "HL - Video": "Hardlines",
    # === Fiber Connectors (same red as hardlines in reference PDF) ===
    "HL - LC SM": "Hardlines",
    "HL - SC SM": "Hardlines",
    "HL - ST SM": "Hardlines",
    # === Cables (no gear images) ===
    "FIBER": "Cables",
    # === Miscellaneous (no gear images) ===
    "INFRA - Fiber Patch Panel": "Misc",
    # === Boxes (junction boxes, lock boxes) ===
    "BOX - Dri Box": "Boxes",
    "BOX - Lock Box": "Boxes",
    "BOX - Patch Box": "Boxes",
    "BOX - Zarges Box": "Boxes",
    "BOX - Zarges XL Box": "Boxes",
    # === Power Equipment ===
    "PWR - EcoFlow Battery": "Power",
    "PWR - EcoFlow Solar Panel": "Power",
    "PWR - Liebert UPS": "Power",
    "PWR - Pinty Battery": "Power",
    "PWR - Quad Box": "Power",
    # === Infrastructure (with images) ===
    "INFRA - Conduit": "Misc",
    "INFRA - Conduit Well": "Misc",
    "MISC - Bike Rack": "Misc",
}


# Category-level default rendering parameters
CATEGORY_DEFAULTS: dict[str, dict] = {
    "APs": {
        "circle_color": (0.2157, 0.3412, 0.6431),  # Navy blue from reference PDF
        "circle_border_width": 0.75,
        "circle_border_color": (0.0, 0.0, 0.0),
        "id_box_height": 2.3,
        "id_box_width_ratio": 0.41,
        "id_box_border_width": 0.35,
        "id_font_size": 3.9,
        "img_scale_ratio": 0.70,
        "brand_text": "CISCO",
        "brand_font_size": 1.8,
        "brand_y_offset": -3.2,
        "brand_x_offset": -0.2,
        "model_font_size": 2.2,
        "model_y_offset": 2.5,
        "model_x_offset": -0.2,
        "font_name": "/Helvetica-Bold",
        "text_color": (1.0, 1.0, 1.0),
        "id_text_color": None,
    },
    "Switches": {
        "circle_color": (0.267, 0.714, 0.290),  # Green from switches.pdf
        "circle_border_width": 0.75,
        "circle_border_color": (0.0, 0.0, 0.0),
        "id_box_height": 3.5,
        "id_box_width_ratio": 0.55,
        "id_box_border_width": 0.45,
        "id_font_size": 3.2,
        "img_scale_ratio": 0.70,
        "brand_text": "",
        "brand_font_size": 1.8,
        "brand_y_offset": -3.2,
        "brand_x_offset": -0.2,
        "model_font_size": 2.2,
        "model_y_offset": 2.5,
        "model_x_offset": -0.2,
        "font_name": "/Helvetica-Bold",
        "text_color": (1.0, 1.0, 1.0),
        "id_text_color": None,
    },
    "P2Ps": {
        "circle_color": (0.9843, 0.6392, 0.1059),  # Orange/amber from reference PDF
        "circle_border_width": 0.75,
        "circle_border_color": (0.0, 0.0, 0.0),
        "id_box_height": 2.3,
        "id_box_width_ratio": 0.41,
        "id_box_border_width": 0.35,
        "id_font_size": 3.9,
        "img_scale_ratio": 0.70,
        "brand_text": "UBIQUITI",
        "brand_font_size": 1.8,
        "brand_y_offset": -3.2,
        "brand_x_offset": -0.2,
        "model_font_size": 2.2,
        "model_y_offset": 2.5,
        "model_x_offset": -0.2,
        "font_name": "/Helvetica-Bold",
        "text_color": (1.0, 1.0, 1.0),
        "id_text_color": None,
    },
    "IoT": {
        "circle_color": (0.6, 0.3, 0.1),  # Brown/orange (non-camera IoT devices)
        "circle_border_width": 0.75,
        "circle_border_color": (0.0, 0.0, 0.0),
        "id_box_height": 2.3,
        "id_box_width_ratio": 0.41,
        "id_box_border_width": 0.35,
        "id_font_size": 3.9,
        "img_scale_ratio": 0.70,
        "brand_text": "",
        "brand_font_size": 1.8,
        "brand_y_offset": -3.2,
        "brand_x_offset": -0.2,
        "model_font_size": 2.2,
        "model_y_offset": 2.5,
        "model_x_offset": -0.2,
        "font_name": "/Helvetica-Bold",
        "text_color": (1.0, 1.0, 1.0),
        "id_text_color": None,
    },
    "Hardlines": {
        "circle_color": (0.7882, 0.1294, 0.1529),  # Red from reference PDF
        "circle_border_width": 0.75,
        "circle_border_color": (0.0, 0.0, 0.0),
        "id_box_height": 4.0,
        "id_box_width_ratio": 0.65,
        "id_box_border_width": 0.5,
        "id_font_size": 3.0,
        "img_scale_ratio": 1.2075,
        "img_y_offset": -0.5,
        "brand_text": "CAT6",
        "brand_font_size": 1.8,
        "brand_y_offset": -3.2,
        "brand_x_offset": -0.5,
        "model_font_size": 2.2,
        "model_y_offset": 2.5,
        "model_x_offset": -0.4,
        "font_name": "/Helvetica-Bold",
        "text_color": (1.0, 1.0, 1.0),
        "id_text_color": None,
        "model_uppercase": True,
    },
    "Cables": {
        "circle_color": (0.8, 0.6, 0.0),
        "circle_border_width": 0.75,
        "circle_border_color": (0.0, 0.0, 0.0),
        "id_box_height": 2.3,
        "id_box_width_ratio": 0.41,
        "id_box_border_width": 0.35,
        "id_font_size": 3.9,
        "img_scale_ratio": 0.70,
        "brand_text": "",
        "brand_font_size": 1.8,
        "brand_y_offset": -3.2,
        "brand_x_offset": -0.2,
        "model_font_size": 2.2,
        "model_y_offset": 2.5,
        "model_x_offset": -0.2,
        "font_name": "/Helvetica-Bold",
        "text_color": (1.0, 1.0, 1.0),
        "id_text_color": None,
        "no_image": True,
    },
    "Misc": {
        "circle_color": (0.5, 0.5, 0.5),
        "circle_border_width": 0.75,
        "circle_border_color": (0.0, 0.0, 0.0),
        "id_box_height": 2.3,
        "id_box_width_ratio": 0.41,
        "id_box_border_width": 0.35,
        "id_font_size": 3.9,
        "img_scale_ratio": 0.70,
        "brand_text": "",
        "brand_font_size": 1.8,
        "brand_y_offset": -3.2,
        "brand_x_offset": -0.2,
        "model_font_size": 2.2,
        "model_y_offset": 2.5,
        "model_x_offset": -0.2,
        "font_name": "/Helvetica-Bold",
        "text_color": (1.0, 1.0, 1.0),
        "id_text_color": None,
        "no_image": True,
    },
    "Power": {
        "circle_color": (0.4, 0.25, 0.1),
        "circle_border_width": 0.75,
        "circle_border_color": (0.0, 0.0, 0.0),
        "id_box_height": 2.3,
        "id_box_width_ratio": 0.41,
        "id_box_border_width": 0.35,
        "id_font_size": 3.9,
        "img_scale_ratio": 0.70,
        "brand_text": "",
        "brand_font_size": 1.8,
        "brand_y_offset": -3.2,
        "brand_x_offset": -0.2,
        "model_font_size": 2.2,
        "model_y_offset": 2.5,
        "model_x_offset": -0.2,
        "font_name": "/Helvetica-Bold",
        "text_color": (1.0, 1.0, 1.0),
        "id_text_color": None,
    },
    "Cameras": {
        "circle_color": (0.3176, 0.4980, 0.9098),  # Blue from cameras.pdf reference
        "circle_border_width": 0.75,
        "circle_border_color": (0.0, 0.0, 0.0),
        "id_box_height": 2.3,
        "id_box_width_ratio": 0.41,
        "id_box_border_width": 0.35,
        "id_font_size": 3.9,
        "img_scale_ratio": 0.70,
        "brand_text": "",
        "brand_font_size": 1.8,
        "brand_y_offset": -3.2,
        "brand_x_offset": -0.2,
        "model_font_size": 2.2,
        "model_y_offset": 2.5,
        "model_x_offset": -0.2,
        "font_name": "/Helvetica-Bold",
        "text_color": (1.0, 1.0, 1.0),
        "id_text_color": None,
    },
    "Fiber": {
        "circle_color": (0.7882, 0.1294, 0.1529),  # Red, same as hardlines in reference
        "circle_border_width": 0.75,
        "circle_border_color": (0.0, 0.0, 0.0),
        "id_box_height": 2.3,
        "id_box_width_ratio": 0.41,
        "id_box_border_width": 0.35,
        "id_font_size": 3.9,
        "img_scale_ratio": 0.70,
        "brand_text": "FIBER",
        "brand_font_size": 1.8,
        "brand_y_offset": -3.2,
        "brand_x_offset": -0.2,
        "model_font_size": 2.2,
        "model_y_offset": 2.5,
        "model_x_offset": -0.2,
        "font_name": "/Helvetica-Bold",
        "text_color": (1.0, 1.0, 1.0),
        "id_text_color": None,
    },
    "Boxes": {
        "circle_color": (0.35, 0.35, 0.4),
        "circle_border_width": 0.75,
        "circle_border_color": (0.0, 0.0, 0.0),
        "id_box_height": 2.3,
        "id_box_width_ratio": 0.41,
        "id_box_border_width": 0.35,
        "id_font_size": 3.9,
        "img_scale_ratio": 0.70,
        "brand_text": "",
        "brand_font_size": 1.8,
        "brand_y_offset": -3.2,
        "brand_x_offset": -0.2,
        "model_font_size": 2.2,
        "model_y_offset": 2.5,
        "model_x_offset": -0.2,
        "font_name": "/Helvetica-Bold",
        "text_color": (1.0, 1.0, 1.0),
        "id_text_color": None,
    },
}


# Per-icon override configurations (only values that differ from category defaults)
ICON_OVERRIDES: dict[str, dict] = {
    # === Access Points (tuned) ===
    "AP - Cisco MR36H": {
        "img_scale_ratio": 0.64,
        "model_x_offset": -1.0,
        "model_y_offset": 3.0,
    },
    "AP - Cisco 9120": {
        "img_scale_ratio": 1.04,
        "img_x_offset": 0.2,
        "img_y_offset": 0.8,
        "model_font_size": 1.1,
        "model_x_offset": 2.0,
        "model_y_offset": 0.0,
    },
    "AP - Cisco 9166I": {
        "img_scale_ratio": 0.98,
        "model_y_offset": 3.0,
        "model_x_offset": 0.0,
    },
    "AP - Cisco 9166D": {
        "img_scale_ratio": 0.98,
        "img_x_offset": -0.2,
        "img_y_offset": 0.6,
        "model_font_size": 1.0,
        "model_x_offset": 2.0,
        "model_y_offset": 0.0,
    },
    "AP - Cisco DB10": {
        "img_scale_ratio": 1.40,
        "img_x_offset": -0.2,
        "img_y_offset": -1.6,
        "brand_font_size": 3.9,
        "id_box_height": 5.5,
        "id_box_width_ratio": 0.73,
        "id_font_size": 1.7,
        "id_box_border_width": 0.7,
        "model_x_offset": -0.6,
    },
    "AP - Cisco MR78": {
        "img_scale_ratio": 1.04,
        "img_x_offset": -0.2,
        "img_y_offset": 0.6,
        "model_x_offset": -0.8,
        "model_y_offset": 3.2,
    },
    "AP - Cisco Marlin 4": {
        "img_scale_ratio": 1.32,
        "img_x_offset": -0.2,
        "img_y_offset": 0.4,
        "model_x_offset": -0.8,
        "model_y_offset": 3.2,
    },
    # === Switches with brand text ===
    "SW - Cisco Micro 4P": {
        "brand_text": "CISCO",
    },
    "SW - Cisco 9200 12P": {
        "brand_text": "CISCO",
        "img_scale_ratio": 1.37,
        "img_x_offset": -0.8,
        "img_y_offset": -2.0,
    },
    "SW - IDF Cisco 9300 24X": {
        "brand_text": "IDF 6U",  # IDF rack label instead of CISCO
        "img_scale_ratio": 1.3125,  # 1.25x bigger (1.05 * 1.25)
        "img_y_offset": -0.5,  # Move image down 0.5px
        "img_x_offset": -0.2,  # Move image left 0.2px
        "model_text_override": "9300 24X",
    },
    # === Distribution with brand text ===
    "DIST - Micro NOC": {
        "img_scale_ratio": 1.4,  # 2x bigger (0.70 * 2)
    },
    "DIST - MikroTik Hex": {
        "brand_text": "MIKROTIK",
    },
    "DIST - Starlink": {
        "brand_text": "STARLINK",
    },
    # === IoT devices with brand text ===
    "VOIP - Yealink T29G": {
        "brand_text": "YEALINK",
    },
    "VOIP - Yealink CP965": {
        "brand_text": "YEALINK",
    },
    "CCTV - AXIS P5655-E": {
        "brand_text": "AXIS",  # From cameras.pdf reference
    },
    "CCTV - AXIS S9302": {
        "brand_text": "AXIS",  # From cameras.pdf reference
    },
    "IPTV - BrightSign XT1144": {
        "brand_text": "BRIGHTSIGN",
    },
    # === Additional Switches with brand text ===
    "DIST - Cisco MX": {
        "brand_text": "CISCO",
    },
    "DIST - Fortinet FortiGate": {
        "brand_text": "FORTINET",
    },
    "SW - Cisco 9300 12X36M": {
        "brand_text": "CISCO",
    },
    "SW - Cisco 9300X 24X": {
        "brand_text": "CISCO",
    },
    "SW - Cisco 9300X 24Y": {
        "brand_text": "CISCO",
    },
    "SW - Cisco 9500 48Y4C": {
        "brand_text": "CISCO",
    },
    "SW - Fortinet 108F 8P": {
        "brand_text": "FORTINET",
    },
    "SW - IDF Cisco 9300 12X36M": {
        "brand_text": "IDF 6U",
        "img_scale_ratio": 1.3125,  # 1.25x bigger
        "img_y_offset": -0.5,
        "img_x_offset": -0.2,
        "model_text_override": "9300 12X36M",
    },
    "SW - IDF Cisco 9300X 24X": {
        "brand_text": "IDF 6U",
        "img_scale_ratio": 1.3125,  # 1.25x bigger
        "img_y_offset": -0.5,
        "img_x_offset": -0.2,
        "model_text_override": "9300X 24X",
    },
    "SW - IDF Cisco 9300X 24Y": {
        "brand_text": "IDF 6U",
        "img_scale_ratio": 1.3125,  # 1.25x bigger
        "img_y_offset": -0.5,
        "img_x_offset": -0.2,
        "model_text_override": "9300X 24Y",
    },
    "SW - IDF Cisco 9500 48Y4C": {
        "brand_text": "IDF 6U",
        "img_scale_ratio": 1.3125,  # 1.25x bigger
        "img_y_offset": -0.5,
        "img_x_offset": -0.2,
        "model_text_override": "9500 48Y4C",
    },
    # === Additional IoT with brand text ===
    "CCTV - AXIS M5526-E": {
        "brand_text": "AXIS",
    },
    "CCTV - Cisco MV93X": {
        "brand_text": "CISCO",
        "img_scale_ratio": 1.40,
        "img_x_offset": -0.2,
        "img_y_offset": -0.2,
    },
    "SEN - Meraki MT15": {
        "brand_text": "MERAKI",
    },
    "SEN - Meraki MT40": {
        "brand_text": "MERAKI",
    },
    # === Power with brand text ===
    "PWR - EcoFlow Battery": {
        "brand_text": "ECOFLOW",
    },
    "PWR - EcoFlow Solar Panel": {
        "brand_text": "ECOFLOW",
    },
    "PWR - Liebert UPS": {
        "brand_text": "LIEBERT",
    },
    # === Hardline text overrides ===
    "HL - Emergency Announce System": {
        "model_text_override": "EAS",
    },
    "HL - General Internet": {
        "model_text_override": "GENERAL\nINTERNET",  # Stacked text
    },
    # === Fiber connectors (use FIBER brand instead of CAT6) ===
    "HL - LC SM": {
        "brand_text": "FIBER",
    },
    "HL - SC SM": {
        "brand_text": "FIBER",
    },
    "HL - ST SM": {
        "brand_text": "FIBER",
    },
}


# Maps deployment subject to gear icon filename (relative to gearIcons/)
ICON_IMAGE_PATHS: dict[str, str | None] = {
    # === Access Points ===
    "AP - Cisco MR36H": "APs/AP - Cisco MR36H.png",
    "AP - Cisco 9120": "APs/AP - Cisco 9120.png",
    "AP - Cisco 9166I": "APs/AP - Cisco 9166.png",  # Same image for I and D variants
    "AP - Cisco 9166D": "APs/AP - Cisco 9166.png",
    "AP - Cisco MR78": "APs/AP - Cisco MR78.png",
    "AP - Cisco Marlin 4": "APs/AP - Cisco Marlin 4.png",
    "AP - Cisco DB10": "APs/AP - DB10.png",  # Note: filename is "AP - DB10" not "AP - Cisco DB10"
    # === Switches / Distribution ===
    "SW - Cisco Micro 4P": "Switches/Cisco Micro 4-P.png",
    "SW - Cisco 9200 12P": "Switches/Cisco 9200 12-P.png",
    "SW - IDF Cisco 9300 24X": "Switches/IDF.png",
    "DIST - Mini NOC": "Switches/Mini NOC.png",
    "DIST - Micro NOC": "Switches/Mini NOC.png",  # Same as Mini NOC
    "DIST - Standard NOC": "Switches/NOC.png",
    "DIST - Pelican NOC": "Switches/NOC.png",  # Use standard NOC image
    "DIST - MikroTik Hex": "Switches/MikroTik Hex.png",
    "DIST - Starlink": "Switches/Starlink.png",
    # === Additional Switches / Distribution ===
    "DIST - Cisco MX": "Switches/Cisco MX.png",
    "DIST - Fortinet FortiGate": "Switches/Fortinet FortiGate.png",
    "DIST - Mega NOC": "Switches/NOC.png",  # Reuse standard NOC image
    "SW - 1G 60W PoE Extender": "Switches/1x4 PoE Extender.png",
    "SW - 1G PoE+ Injectors": "Switches/48V PoE Injector.png",
    "SW - 1G PoE+ Media Converter": "Switches/Media Converter.png",
    "SW - Cisco 9300 12X36M": "Switches/Cisco 9300 24-P.png",  # Similar model
    "SW - Cisco 9300X 24X": "Switches/Cisco 9300 24-P.png",
    "SW - Cisco 9300X 24Y": "Switches/Cisco 9300 24-P.png",
    "SW - Cisco 9500 48Y4C": "Switches/Cisco 9500 48-P.png",
    "SW - Fortinet 108F 8P": "Switches/Fortinet 108F 8-P.png",
    "SW - IDF Cisco 9300 12X36M": "Switches/IDF.png",
    "SW - IDF Cisco 9300X 24X": "Switches/IDF.png",
    "SW - IDF Cisco 9300X 24Y": "Switches/IDF.png",
    "SW - IDF Cisco 9500 48Y4C": "Switches/IDF.png",
    "SW - Raspberry Pi": "Switches/Raspberry Pi.png",
    # === Point-to-Points ===
    "P2P - Ubiquiti NanoBeam": "P2Ps/P2P - Ubiquiti NanoBeam.png",
    "P2P - Ubiquiti LiteAP": "P2Ps/P2P - Ubiquiti LiteAP AC.png",
    "P2P - Ubiquiti GigaBeam": "P2Ps/P2P - Ubiquiti GigaBeam.png",
    "P2P - Ubiquiti GigaBeam LR": "P2Ps/P2P - Ubiquiti GigaBeam LR.png",
    # === Additional Point-to-Points ===
    "P2P - Ubiquiti Wave AP Micro": "P2Ps/P2P - Ubiquiti Wave AP Micro.png",
    "P2P - Ubiquiti Wave Nano": "P2Ps/P2P - Ubiquiti Wave Nano.png",
    "P2P - Ubiquiti Wave Pico": "P2Ps/P2P - Ubiquiti Wave Pico.png",
    # === IoT / VoIP ===
    "VOIP - Yealink T29G": "Misc/Yealink T29G.png",
    "VOIP - Yealink CP965": "Misc/Yealink P965.png",  # Note: filename is "P965" not "CP965"
    # === IoT / CCTV ===
    "CCTV - AXIS P5655-E": "Misc/AXIS P5655-E.png",
    "CCTV - AXIS S9302": "Misc/AXIS S9302 Workstation.png",
    # === Additional IoT / CCTV ===
    "CCTV - AXIS M5526-E": "Misc/AXIS M5526-E.png",
    "CCTV - Cisco MV93X": "Misc/MV93X.png",
    # === IoT / Sensors ===
    "SEN - Meraki MT15": "Misc/Meraki MT15.png",
    "SEN - Meraki MT40": "Misc/Meraki MT40.png",
    # === IoT / Emergency Announce ===
    "EAS - Command Unit": "Misc/Emergency Announce Command Unit.png",
    "EAS - Laptop": "Misc/EAS Laptop.png",
    "EAS - Trigger Box": "Misc/Emergency Announce Trigger Box.png",
    # === IoT / IPTV ===
    "IPTV - BrightSign XT1144": "Misc/Brightsign XT1144.png",
    # === Hardlines (all use CAT6 Cable image) ===
    "HL - Artist": "Hardlines/CAT6 Cable.png",
    "HL - Production": "Hardlines/CAT6 Cable.png",
    "HL - PoS": "Hardlines/CAT6 Cable.png",
    "HL - Access Control": "Hardlines/CAT6 Cable.png",
    "HL - Sponsor": "Hardlines/CAT6 Cable.png",
    "HL - General Internet": "Hardlines/CAT6 Cable.png",
    "HL - Audio": "Hardlines/CAT6 Cable.png",
    "HL - Emergency Announce System": "Hardlines/CAT6 Cable.png",
    "HL - WAN": "Hardlines/CAT6 Cable.png",
    # === Additional Hardlines (copper - use CAT6 Cable) ===
    "HL -": "Hardlines/CAT6 Cable.png",
    "HL - CCTV": "Hardlines/CAT6 Cable.png",
    "HL - Clair": "Hardlines/CAT6 Cable.png",
    "HL - IPTV": "Hardlines/CAT6 Cable.png",
    "HL - Lighting": "Hardlines/CAT6 Cable.png",
    "HL - Media": "Hardlines/CAT6 Cable.png",
    "HL - Radios": "Hardlines/CAT6 Cable.png",
    "HL - Streaming": "Hardlines/CAT6 Cable.png",
    "HL - Video": "Hardlines/CAT6 Cable.png",
    # === Fiber Connectors (specific images) ===
    "HL - LC SM": "Hardlines/LC SM.png",
    "HL - SC SM": "Hardlines/SC SM.png",
    "HL - ST SM": "Hardlines/ST SM.png",
    # === Cables (NO gear images) ===
    "FIBER": None,
    # === Miscellaneous (NO gear images) ===
    "INFRA - Fiber Patch Panel": None,
    # === Boxes ===
    "BOX - Dri Box": "Misc/Dri Box.png",
    "BOX - Lock Box": "Misc/Lock Box.png",
    "BOX - Patch Box": "Misc/Patch Box.png",
    "BOX - Zarges Box": "Misc/Zarges Junction Box.png",
    "BOX - Zarges XL Box": "Misc/Zarges XL Junction Box.png",
    # === Power Equipment ===
    "PWR - EcoFlow Battery": "Misc/EcoFlow Battery.png",
    "PWR - EcoFlow Solar Panel": "Misc/EcoFlow Solar Panel.png",
    "PWR - Liebert UPS": "Misc/Liebert UPS.png",
    "PWR - Pinty Battery": "Misc/Pinty Battery.png",
    "PWR - Quad Box": "Misc/Quad Box.png",
    # === Infrastructure ===
    "INFRA - Conduit": "Misc/Conduit.png",
    "INFRA - Conduit Well": "Misc/Conduit Well.png",
    "MISC - Bike Rack": "Misc/Bike Rack.png",
}


# ID prefix configuration for device types
# format: "prefix_first" = "j100", "number_first" = "100a"
ID_PREFIX_CONFIG: dict[str, IdPrefixConfig] = {
    # === Access Points (prefix first: j100, k100, etc.) ===
    "AP - Cisco MR36H": {"prefix": "j", "start": 100},
    "AP - Cisco MR78": {"prefix": "k", "start": 100},
    "AP - Cisco 9166I": {"prefix": "l", "start": 100},
    "AP - Cisco 9166D": {"prefix": "m", "start": 100},
    "AP - Cisco 9120": {"prefix": "n", "start": 100},
    "AP - Cisco Marlin 4": {"prefix": "o", "start": 100},
    "AP - Cisco DB10": {"prefix": "p", "start": 100},

    # === Cameras (number first: 100a, 101a, etc.) ===
    "CCTV - Cisco MV93X": {"prefix": "a", "start": 100, "format": "number_first"},
    "CCTV - AXIS P5655-E": {"prefix": "b", "start": 100, "format": "number_first"},
    "CCTV - AXIS M5526-E": {"prefix": "c", "start": 100, "format": "number_first"},

    # === Hardlines (double letter prefix: aa100, bb100, etc.) ===
    "HL - Access Control": {"prefix": "aa", "start": 100},
    "HL - Artist": {"prefix": "bb", "start": 100},
    "HL - Audio": {"prefix": "cc", "start": 100},
    "HL - CCTV": {"prefix": "dd", "start": 100},
    "HL - Clair": {"prefix": "ee", "start": 100},
    "HL - Emergency Announce System": {"prefix": "ff", "start": 100},
    "HL - General Internet": {"prefix": "gg", "start": 100},
    "HL - IPTV": {"prefix": "hh", "start": 100},
    "HL - Lighting": {"prefix": "ii", "start": 100},
    "HL - Media": {"prefix": "jj", "start": 100},
    "HL - PoS": {"prefix": "kk", "start": 100},
    "HL - Production": {"prefix": "ll", "start": 100},
    "HL - Radios": {"prefix": "mm", "start": 100},
    "HL - Sponsor": {"prefix": "nn", "start": 100},
    "HL - Streaming": {"prefix": "oo", "start": 100},
    "HL - Video": {"prefix": "pp", "start": 100},

    # === P2Ps (single letter prefix: s100, t100, etc.) ===
    "P2P - Ubiquiti NanoBeam": {"prefix": "s", "start": 100},
    "P2P - Ubiquiti LiteAP": {"prefix": "t", "start": 100},
    "P2P - Ubiquiti Wave Nano": {"prefix": "u", "start": 100},
    "P2P - Ubiquiti Wave Pico": {"prefix": "v", "start": 100},
    "P2P - Ubiquiti Wave AP Micro": {"prefix": "w", "start": 100},
    "P2P - Ubiquiti GigaBeam": {"prefix": "x", "start": 100},
    "P2P - Ubiquiti GigaBeam LR": {"prefix": "y", "start": 100},

    # === Switches (single letter, various starts for independent counters) ===
    "SW - Cisco Micro 4P": {"prefix": "a", "start": 100},
    "SW - Fortinet 108F 8P": {"prefix": "b", "start": 100},
    "SW - Cisco 9200 12P": {"prefix": "c", "start": 100},
    "SW - Cisco 9300X 24X": {"prefix": "d", "start": 300},
    "SW - Cisco 9300 12X36M": {"prefix": "d", "start": 500},
    "SW - Cisco 9300X 24Y": {"prefix": "d", "start": 700},
    "SW - Cisco 9500 48Y4C": {"prefix": "d", "start": 900},

    # === IDFs (e prefix, various starts) ===
    "SW - IDF Cisco 9300 24X": {"prefix": "e", "start": 100},
    "SW - IDF Cisco 9300X 24X": {"prefix": "e", "start": 300},
    "SW - IDF Cisco 9300 12X36M": {"prefix": "e", "start": 500},
    "SW - IDF Cisco 9300X 24Y": {"prefix": "e", "start": 700},
    "SW - IDF Cisco 9500 48Y4C": {"prefix": "e", "start": 900},

    # === NOCs (all share f prefix, same counter) ===
    "DIST - Micro NOC": {"prefix": "f", "start": 100},
    "DIST - Mini NOC": {"prefix": "f", "start": 100},
    "DIST - Standard NOC": {"prefix": "f", "start": 100},
    "DIST - Mega NOC": {"prefix": "f", "start": 100},
    "DIST - Pelican NOC": {"prefix": "f", "start": 100},
}


def get_icon_config(subject: str) -> dict:
    """
    Get merged configuration for an icon (category defaults + icon overrides).

    Checks JSON overrides file first. If found, returns that config directly.
    Otherwise falls through to Python merge logic.

    Args:
        subject: Deployment subject name (e.g., "AP - Cisco MR36H")

    Returns:
        Dictionary with merged configuration including:
        - All category default parameters
        - Any per-icon overrides applied on top
        - image_path: Path to gear icon image (or None)
        - category: Category name
        Returns empty dict if subject not found in configuration.
    """
    # Check JSON overrides first (lazy import to avoid circular deps)
    from app.services.icon_override_store import IconOverrideStore
    from app.config import settings

    store = IconOverrideStore(settings.icon_overrides_file)
    json_config = store.get_icon(subject)
    if json_config:
        return json_config

    category = ICON_CATEGORIES.get(subject)
    if not category:
        return {}

    # Start with category defaults
    config = CATEGORY_DEFAULTS.get(category, {}).copy()

    # Apply per-icon overrides
    overrides = ICON_OVERRIDES.get(subject, {})
    config.update(overrides)

    # Add image path and category
    config["image_path"] = ICON_IMAGE_PATHS.get(subject)
    config["category"] = category

    return config


def get_model_text(subject: str) -> str:
    """
    Extract model text from deployment subject.

    Parses the subject name to extract just the model identifier,
    removing category prefixes and brand names.

    Args:
        subject: Deployment subject (e.g., "AP - Cisco MR36H")

    Returns:
        Model text for display (e.g., "MR36H")

    Examples:
        >>> get_model_text("AP - Cisco MR36H")
        'MR36H'
        >>> get_model_text("HL - Artist")
        'Artist'
        >>> get_model_text("P2P - Ubiquiti NanoBeam")
        'NanoBeam'
        >>> get_model_text("DIST - Mini NOC")
        'Mini NOC'
    """
    if " - " in subject:
        parts = subject.split(" - ")
        if len(parts) >= 2:
            # Get the model part (after the prefix)
            model_part = parts[-1]
            # Remove brand prefix if present
            for brand in [
                "Cisco ", "Ubiquiti ", "Axis ", "Yealink ", "BrightSign ",
                "Fortinet ", "Meraki ", "EcoFlow ", "Liebert ", "Netgear ", "Netonix ",
            ]:
                if model_part.startswith(brand):
                    return model_part[len(brand):]
            return model_part
    return subject


def get_brand_for_icon(subject: str) -> str:
    """
    Get the brand name for an icon.

    Args:
        subject: Deployment subject name

    Returns:
        Brand name string or empty string if no brand
    """
    config = get_icon_config(subject)
    return config.get("brand_text", "")


def get_id_prefix_config(subject: str) -> IdPrefixConfig | None:
    """
    Get ID prefix configuration for a deployment subject.

    Args:
        subject: Deployment subject name (e.g., "AP - Cisco MR36H")

    Returns:
        IdPrefixConfig with prefix config or None if no ID configured.
        Example: {"prefix": "j", "start": 100, "format": "prefix_first"}
    """
    return ID_PREFIX_CONFIG.get(subject)


class IconIdAssigner:
    """
    Assigns sequential IDs to icons during PDF conversion.

    Each device type has a unique prefix and starting number.
    Counters are tracked independently for each prefix+start combination.

    Example:
        assigner = IconIdAssigner()
        assigner.get_next_id("AP - Cisco MR36H")  # Returns "j100"
        assigner.get_next_id("AP - Cisco MR36H")  # Returns "j101"
        assigner.get_next_id("CCTV - Cisco MV93X")  # Returns "100a" (number-first format)
    """

    def __init__(self):
        """Initialize with empty counters."""
        self._counters: dict[str, int] = {}

    def get_next_id(self, deployment_subject: str) -> str | None:
        """
        Get next sequential ID for a deployment subject.

        Args:
            deployment_subject: Deployment subject name (e.g., "AP - Cisco MR36H")

        Returns:
            Sequential ID string (e.g., "j100", "100a", "aa100") or None if no ID configured.
        """
        config = ID_PREFIX_CONFIG.get(deployment_subject)
        if not config:
            return None

        prefix = config["prefix"]
        start = config["start"]
        format_type = config.get("format", "prefix_first")

        # Counter key includes start to handle d100/d300/d500 independently
        counter_key = f"{prefix}_{start}"

        if counter_key not in self._counters:
            self._counters[counter_key] = start
        else:
            self._counters[counter_key] += 1

        current_num = self._counters[counter_key]

        if format_type == "number_first":
            return f"{current_num}{prefix}"
        else:
            return f"{prefix}{current_num}"

    def reset(self):
        """Reset all counters for a new conversion."""
        self._counters.clear()

    def get_current_counts(self) -> dict[str, int]:
        """Get current counter values (for debugging/logging)."""
        return self._counters.copy()
