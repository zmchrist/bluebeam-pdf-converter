"""Tests for icon renderer service."""

from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image
from pypdf import PdfWriter

from app.services.icon_config import (
    CATEGORY_DEFAULTS,
    ICON_CATEGORIES,
    IconIdAssigner,
    get_icon_config,
    get_model_text,
)
from app.services.icon_renderer import IconRenderer


class TestIconConfig:
    """Tests for icon configuration."""

    def test_get_icon_config_known_icon(self):
        """Test config retrieval for known icon."""
        config = get_icon_config("AP - Cisco MR36H")
        assert config is not None
        assert "circle_color" in config
        assert config["category"] == "APs"

    def test_get_icon_config_unknown_icon(self):
        """Test config retrieval for unknown icon."""
        config = get_icon_config("Unknown - Nonexistent Icon")
        assert config == {}

    def test_get_icon_config_includes_category(self):
        """Test that config includes category name."""
        config = get_icon_config("AP - Cisco MR36H")
        assert config["category"] == "APs"

    def test_get_icon_config_includes_image_path(self):
        """Test that config includes image path."""
        config = get_icon_config("AP - Cisco MR36H")
        assert config["image_path"] == "APs/AP - Cisco MR36H.png"

    def test_get_icon_config_applies_overrides(self):
        """Test that per-icon overrides are applied."""
        config_9120 = get_icon_config("AP - Cisco 9120")
        config_mr36h = get_icon_config("AP - Cisco MR36H")
        # 9120 has an override for model_y_offset
        assert config_9120["model_y_offset"] != config_mr36h["model_y_offset"]

    def test_get_model_text_cisco(self):
        """Test model text extraction for Cisco device."""
        assert get_model_text("AP - Cisco MR36H") == "MR36H"
        assert get_model_text("AP - Cisco 9120") == "9120"

    def test_get_model_text_ubiquiti(self):
        """Test model text extraction for Ubiquiti device."""
        assert get_model_text("P2P - Ubiquiti NanoBeam") == "NanoBeam"

    def test_get_model_text_hardline(self):
        """Test model text extraction for hardline."""
        assert get_model_text("HL - Artist") == "Artist"
        assert get_model_text("HL - Production") == "Production"

    def test_get_model_text_distribution(self):
        """Test model text extraction for distribution."""
        assert get_model_text("DIST - Mini NOC") == "Mini NOC"
        assert get_model_text("DIST - Starlink") == "Starlink"

    def test_category_defaults_exist(self):
        """Test that all categories have defaults."""
        categories = set(ICON_CATEGORIES.values())
        for cat in categories:
            assert cat in CATEGORY_DEFAULTS, f"Missing defaults for {cat}"

    def test_category_defaults_have_required_keys(self):
        """Test that category defaults have all required rendering keys."""
        required_keys = [
            "circle_color",
            "circle_border_width",
            "circle_border_color",
            "id_box_height",
            "id_box_width_ratio",
            "img_scale_ratio",
            "text_color",
        ]
        for cat_name, defaults in CATEGORY_DEFAULTS.items():
            for key in required_keys:
                assert key in defaults, f"Missing {key} in {cat_name} defaults"

    def test_new_category_defaults_exist(self):
        """Test that new categories have defaults."""
        new_categories = ["Power", "Fiber", "Boxes"]
        for cat in new_categories:
            assert cat in CATEGORY_DEFAULTS, f"Missing defaults for {cat}"

    def test_power_category_has_brown_color(self):
        """Test Power category has brown color."""
        power = CATEGORY_DEFAULTS["Power"]
        assert power["circle_color"][0] > 0.3  # Brown has higher red
        assert power["circle_color"][1] < 0.4  # Lower green

    def test_fiber_category_has_red_color(self):
        """Test Fiber category has red color (same as hardlines per reference)."""
        fiber = CATEGORY_DEFAULTS["Fiber"]
        assert fiber["circle_color"][0] > 0.7  # Red has high red
        assert fiber["brand_text"] == "FIBER"

    def test_new_switch_icons_configured(self):
        """Test new switch icons return valid config."""
        new_switches = [
            "DIST - Cisco MX",
            "SW - Fortinet 108F 8P",
            "SW - Raspberry Pi",
        ]
        for subject in new_switches:
            config = get_icon_config(subject)
            assert config != {}, f"{subject} not configured"
            assert config["category"] == "Switches"

    def test_new_p2p_icons_configured(self):
        """Test new P2P icons return valid config."""
        new_p2ps = [
            "P2P - Ubiquiti Wave AP Micro",
            "P2P - Ubiquiti Wave Nano",
            "P2P - Ubiquiti Wave Pico",
        ]
        for subject in new_p2ps:
            config = get_icon_config(subject)
            assert config != {}, f"{subject} not configured"
            assert config["category"] == "P2Ps"

    def test_fiber_hardlines_use_hardlines_category(self):
        """Test fiber connector hardlines use Hardlines category (red like reference)."""
        fiber_types = ["HL - LC Fiber", "HL - SC Fiber", "HL - ST Fiber"]
        for subject in fiber_types:
            config = get_icon_config(subject)
            assert config["category"] == "Hardlines", f"{subject} should be Hardlines"
            assert config.get("brand_text") == "FIBER", f"{subject} should have FIBER brand"

    def test_power_icons_configured(self):
        """Test power equipment icons return valid config."""
        power_icons = [
            "PWR - EcoFlow Battery",
            "PWR - Liebert UPS",
        ]
        for subject in power_icons:
            config = get_icon_config(subject)
            assert config != {}, f"{subject} not configured"
            assert config["category"] == "Power"

    def test_box_icons_configured(self):
        """Test box icons return valid config."""
        box_icons = [
            "BOX - Dri Box",
            "BOX - Zarges Box",
        ]
        for subject in box_icons:
            config = get_icon_config(subject)
            assert config != {}, f"{subject} not configured"
            assert config["category"] == "Boxes"

    def test_get_model_text_fortinet(self):
        """Test model text extraction for Fortinet device."""
        assert get_model_text("SW - Fortinet 108F 8P") == "108F 8P"

    def test_get_model_text_meraki(self):
        """Test model text extraction for Meraki device."""
        assert get_model_text("SEN - Meraki MT15") == "MT15"


class TestIconRenderer:
    """Tests for IconRenderer service."""

    @pytest.fixture
    def renderer_with_test_image(self, tmp_path):
        """Create renderer with temp directory and test image."""
        # Create fake gear icons structure
        aps_dir = tmp_path / "APs"
        aps_dir.mkdir()

        # Create a minimal PNG file for testing
        img = Image.new("RGB", (100, 100), color="blue")
        img.save(aps_dir / "AP - Cisco MR36H.png")

        return IconRenderer(tmp_path)

    def test_init(self, renderer_with_test_image):
        """Test renderer initialization."""
        assert renderer_with_test_image.gear_icons_dir is not None
        assert renderer_with_test_image._image_cache == {}

    def test_can_render_with_image(self, renderer_with_test_image):
        """Test can_render returns True when image exists."""
        with patch("app.services.icon_renderer.get_icon_config") as mock_config:
            mock_config.return_value = {
                "image_path": "APs/AP - Cisco MR36H.png",
                "category": "APs",
            }
            assert renderer_with_test_image.can_render("AP - Cisco MR36H") is True

    def test_can_render_without_config(self, renderer_with_test_image):
        """Test can_render returns False when no config."""
        with patch("app.services.icon_renderer.get_icon_config") as mock_config:
            mock_config.return_value = {}
            assert renderer_with_test_image.can_render("Unknown Icon") is False

    def test_can_render_without_image_file(self, tmp_path):
        """Test can_render returns False when image file missing."""
        renderer = IconRenderer(tmp_path)
        with patch("app.services.icon_renderer.get_icon_config") as mock_config:
            mock_config.return_value = {
                "image_path": "APs/NonExistent.png",
                "category": "APs",
            }
            assert renderer.can_render("Test Icon") is False

    def test_can_render_no_image_category(self, tmp_path):
        """Test can_render returns False for no_image categories."""
        renderer = IconRenderer(tmp_path)
        with patch("app.services.icon_renderer.get_icon_config") as mock_config:
            mock_config.return_value = {
                "image_path": None,
                "category": "Cables",
                "no_image": True,
            }
            assert renderer.can_render("FIBER") is False

    def test_load_image_returns_data(self, renderer_with_test_image):
        """Test load_image returns image data."""
        bg_color = (0.22, 0.34, 0.65)
        data, width, height = renderer_with_test_image.load_image(
            "APs/AP - Cisco MR36H.png", bg_color
        )

        assert isinstance(data, bytes)
        assert len(data) > 0
        assert width == 100
        assert height == 100

    def test_load_image_caching(self, renderer_with_test_image):
        """Test that images are cached after loading."""
        bg_color = (0.22, 0.34, 0.65)

        # First load
        data1, w1, h1 = renderer_with_test_image.load_image(
            "APs/AP - Cisco MR36H.png", bg_color
        )

        # Check cache populated
        cache_key = f"APs/AP - Cisco MR36H.png:{bg_color}"
        assert cache_key in renderer_with_test_image._image_cache

        # Second load should use cache
        data2, w2, h2 = renderer_with_test_image.load_image(
            "APs/AP - Cisco MR36H.png", bg_color
        )

        assert data1 == data2
        assert w1 == w2
        assert h1 == h2

    def test_render_icon_returns_indirect_object(self, renderer_with_test_image):
        """Test that render_icon returns an IndirectObject."""
        with patch("app.services.icon_renderer.get_icon_config") as mock_config:
            mock_config.return_value = {
                "image_path": "APs/AP - Cisco MR36H.png",
                "category": "APs",
                "circle_color": (0.22, 0.34, 0.65),
                "circle_border_width": 0.5,
                "circle_border_color": (0.0, 0.0, 0.0),
                "id_box_height": 4.0,
                "id_box_width_ratio": 0.55,
                "id_box_border_width": 0.6,
                "img_scale_ratio": 0.70,
                "brand_text": "CISCO",
                "brand_font_size": 1.9,
                "brand_y_offset": -4.0,
                "brand_x_offset": -0.2,
                "model_font_size": 1.6,
                "model_y_offset": 2.5,
                "model_x_offset": -0.7,
                "text_color": (1.0, 1.0, 1.0),
            }

            writer = PdfWriter()
            rect = [100.0, 200.0, 125.0, 230.0]

            result = renderer_with_test_image.render_icon(
                writer, "AP - Cisco MR36H", rect
            )

            assert result is not None

    def test_render_icon_no_config_returns_none(self, renderer_with_test_image):
        """Test render_icon returns None for unknown icon."""
        with patch("app.services.icon_renderer.get_icon_config") as mock_config:
            mock_config.return_value = {}

            writer = PdfWriter()
            rect = [100.0, 200.0, 125.0, 230.0]

            result = renderer_with_test_image.render_icon(writer, "Unknown Icon", rect)

            assert result is None

    def test_render_icon_no_brand_text(self, renderer_with_test_image):
        """Test render_icon works without brand text."""
        with patch("app.services.icon_renderer.get_icon_config") as mock_config:
            mock_config.return_value = {
                "image_path": "APs/AP - Cisco MR36H.png",
                "category": "Hardlines",
                "circle_color": (0.3, 0.3, 0.3),
                "circle_border_width": 0.5,
                "circle_border_color": (0.0, 0.0, 0.0),
                "id_box_height": 4.0,
                "id_box_width_ratio": 0.55,
                "id_box_border_width": 0.6,
                "img_scale_ratio": 0.70,
                "brand_text": "",  # No brand text
                "brand_font_size": 1.9,
                "brand_y_offset": -4.0,
                "brand_x_offset": -0.2,
                "model_font_size": 1.6,
                "model_y_offset": 2.5,
                "model_x_offset": -0.7,
                "text_color": (1.0, 1.0, 1.0),
            }

            writer = PdfWriter()
            rect = [100.0, 200.0, 125.0, 230.0]

            result = renderer_with_test_image.render_icon(
                writer, "HL - Artist", rect
            )

            assert result is not None


class TestCompoundRendering:
    """Tests for compound annotation rendering."""

    @pytest.fixture
    def renderer_with_test_image(self, tmp_path):
        """Create renderer with temp directory and test image."""
        aps_dir = tmp_path / "APs"
        aps_dir.mkdir()
        img = Image.new("RGB", (100, 100), color="blue")
        img.save(aps_dir / "AP - Cisco MR36H.png")
        return IconRenderer(tmp_path)

    def test_render_compound_icon_returns_components(self, renderer_with_test_image):
        """Test render_compound_icon returns list of component dicts."""
        with patch("app.services.icon_renderer.get_icon_config") as mock_config:
            mock_config.return_value = {
                "image_path": "APs/AP - Cisco MR36H.png",
                "category": "APs",
                "circle_color": (0.22, 0.34, 0.65),
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
                "text_color": (1.0, 1.0, 1.0),
                "id_text_color": None,
            }

            writer = PdfWriter()
            result = renderer_with_test_image.render_compound_icon(
                writer, "AP - Cisco MR36H", (500.0, 600.0), id_label="j100"
            )

            assert result is not None
            assert len(result) == 7  # All 7 components

            # Verify roles
            roles = [c["role"] for c in result]
            assert roles[0] == "root_id_text"
            assert "circle" in roles
            assert "image" in roles
            assert "brand_text" in roles
            assert "model_text" in roles
            assert "container" in roles
            assert "id_box_border" in roles

    def test_render_compound_icon_no_config_returns_none(self, renderer_with_test_image):
        """Test render_compound_icon returns None for unknown subject."""
        with patch("app.services.icon_renderer.get_icon_config") as mock_config:
            mock_config.return_value = {}
            writer = PdfWriter()
            result = renderer_with_test_image.render_compound_icon(
                writer, "Unknown Icon", (500.0, 600.0)
            )
            assert result is None

    def test_render_compound_icon_no_image(self, tmp_path):
        """Test compound icon with no_image flag produces fewer components."""
        renderer = IconRenderer(tmp_path)
        with patch("app.services.icon_renderer.get_icon_config") as mock_config:
            mock_config.return_value = {
                "image_path": None,
                "category": "Cables",
                "no_image": True,
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
                "text_color": (1.0, 1.0, 1.0),
                "id_text_color": None,
            }

            writer = PdfWriter()
            result = renderer.render_compound_icon(
                writer, "FIBER", (500.0, 600.0), id_label="f100"
            )

            assert result is not None
            # Should have: root, id_box, container, circle, model_text = 5
            # No image, no brand_text
            roles = [c["role"] for c in result]
            assert "root_id_text" in roles
            assert "circle" in roles
            assert "image" not in roles
            assert "brand_text" not in roles

    def test_render_compound_icon_no_brand(self, renderer_with_test_image):
        """Test compound icon without brand text omits brand component."""
        with patch("app.services.icon_renderer.get_icon_config") as mock_config:
            mock_config.return_value = {
                "image_path": "APs/AP - Cisco MR36H.png",
                "category": "APs",
                "circle_color": (0.22, 0.34, 0.65),
                "circle_border_width": 0.75,
                "circle_border_color": (0.0, 0.0, 0.0),
                "id_box_height": 2.3,
                "id_box_width_ratio": 0.41,
                "id_box_border_width": 0.35,
                "id_font_size": 3.9,
                "img_scale_ratio": 0.70,
                "brand_text": "",  # No brand
                "brand_font_size": 1.8,
                "brand_y_offset": -3.2,
                "brand_x_offset": -0.2,
                "model_font_size": 2.2,
                "model_y_offset": 2.5,
                "model_x_offset": -0.2,
                "text_color": (1.0, 1.0, 1.0),
                "id_text_color": None,
            }

            writer = PdfWriter()
            result = renderer_with_test_image.render_compound_icon(
                writer, "SW - Cisco Micro 4P", (500.0, 600.0)
            )

            assert result is not None
            roles = [c["role"] for c in result]
            assert "brand_text" not in roles
            assert len(result) == 6  # All except brand

    def test_compound_component_rects_are_absolute(self, renderer_with_test_image):
        """Test that component rects use absolute page coordinates."""
        with patch("app.services.icon_renderer.get_icon_config") as mock_config:
            mock_config.return_value = {
                "image_path": "APs/AP - Cisco MR36H.png",
                "category": "APs",
                "circle_color": (0.22, 0.34, 0.65),
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
                "text_color": (1.0, 1.0, 1.0),
                "id_text_color": None,
            }

            writer = PdfWriter()
            result = renderer_with_test_image.render_compound_icon(
                writer, "AP - Cisco MR36H", (5000.0, 6000.0)
            )

            # All rects should be near the center (5000, 6000)
            for comp in result:
                x1, y1, x2, y2 = comp["rect"]
                assert x2 > x1, f"{comp['role']} has invalid rect width"
                assert y2 > y1, f"{comp['role']} has invalid rect height"
                # Should be within ~30 pts of center
                assert abs((x1 + x2) / 2 - 5000) < 30, f"{comp['role']} too far from center X"
                assert abs((y1 + y2) / 2 - 6000) < 30, f"{comp['role']} too far from center Y"

    def test_compound_component_subtypes(self, renderer_with_test_image):
        """Test that components have correct PDF subtypes."""
        with patch("app.services.icon_renderer.get_icon_config") as mock_config:
            mock_config.return_value = {
                "image_path": "APs/AP - Cisco MR36H.png",
                "category": "APs",
                "circle_color": (0.22, 0.34, 0.65),
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
                "text_color": (1.0, 1.0, 1.0),
                "id_text_color": None,
            }

            writer = PdfWriter()
            result = renderer_with_test_image.render_compound_icon(
                writer, "AP - Cisco MR36H", (500.0, 600.0)
            )

            subtype_map = {c["role"]: c["subtype"] for c in result}
            assert subtype_map["root_id_text"] == "/FreeText"
            assert subtype_map["id_box_border"] == "/Square"
            assert subtype_map["container"] == "/FreeText"
            assert subtype_map["circle"] == "/Circle"
            assert subtype_map["image"] == "/Square"
            assert subtype_map["model_text"] == "/FreeText"
            assert subtype_map["brand_text"] == "/FreeText"


class TestIconRendererIntegration:
    """Integration tests with real files."""

    @pytest.fixture
    def real_gear_icons_dir(self):
        """Get real gear icons directory if available."""
        # Try different relative paths
        paths_to_try = [
            Path("../samples/icons/gearIcons"),
            Path("samples/icons/gearIcons"),
            Path(__file__).parent.parent.parent / "samples" / "icons" / "gearIcons",
        ]

        for path in paths_to_try:
            if path.exists():
                return path

        return None

    def test_with_real_gear_icons(self, real_gear_icons_dir):
        """Test with actual gear icons directory if available."""
        if not real_gear_icons_dir:
            pytest.skip("Gear icons directory not found")

        renderer = IconRenderer(real_gear_icons_dir)

        # Test a known icon
        assert renderer.can_render("AP - Cisco MR36H") is True

    def test_render_real_mr36h_icon(self, real_gear_icons_dir):
        """Test rendering real MR36H icon."""
        if not real_gear_icons_dir:
            pytest.skip("Gear icons directory not found")

        renderer = IconRenderer(real_gear_icons_dir)
        writer = PdfWriter()
        rect = [100.0, 700.0, 125.0, 730.0]

        result = renderer.render_icon(writer, "AP - Cisco MR36H", rect, id_label="j100")

        assert result is not None

    def test_all_renderable_icons(self, real_gear_icons_dir):
        """Test that all icons marked as renderable actually render."""
        if not real_gear_icons_dir:
            pytest.skip("Gear icons directory not found")

        renderer = IconRenderer(real_gear_icons_dir)
        writer = PdfWriter()
        rect = [100.0, 700.0, 125.0, 730.0]

        renderable_count = 0
        for subject in ICON_CATEGORIES.keys():
            if renderer.can_render(subject):
                result = renderer.render_icon(writer, subject, rect)
                assert result is not None, f"Failed to render {subject}"
                renderable_count += 1

        # Should have at least some renderable icons
        assert renderable_count > 0


class TestIconIdAssigner:
    """Tests for IconIdAssigner service."""

    def test_init_empty_counters(self):
        """Test assigner initializes with empty counters."""
        assigner = IconIdAssigner()
        assert assigner._counters == {}

    def test_get_next_id_ap_prefix_first(self):
        """Test AP icons get j-prefix IDs."""
        assigner = IconIdAssigner()
        assert assigner.get_next_id("AP - Cisco MR36H") == "j100"
        assert assigner.get_next_id("AP - Cisco MR36H") == "j101"
        assert assigner.get_next_id("AP - Cisco MR36H") == "j102"

    def test_get_next_id_camera_number_first(self):
        """Test cameras get number-first format (100a, 101a)."""
        assigner = IconIdAssigner()
        assert assigner.get_next_id("CCTV - Cisco MV93X") == "100a"
        assert assigner.get_next_id("CCTV - Cisco MV93X") == "101a"
        assert assigner.get_next_id("CCTV - Cisco MV93X") == "102a"

    def test_get_next_id_hardline_double_letter(self):
        """Test hardlines get double-letter prefix (bb100)."""
        assigner = IconIdAssigner()
        assert assigner.get_next_id("HL - Artist") == "bb100"
        assert assigner.get_next_id("HL - Artist") == "bb101"

    def test_get_next_id_p2p_single_letter(self):
        """Test P2Ps get single-letter prefix."""
        assigner = IconIdAssigner()
        assert assigner.get_next_id("P2P - Ubiquiti NanoBeam") == "s100"
        assert assigner.get_next_id("P2P - Ubiquiti GigaBeam") == "x100"

    def test_get_next_id_switches_independent_counters(self):
        """Test switches with shared prefix but different starts increment independently."""
        assigner = IconIdAssigner()
        # d prefix with different starts
        assert assigner.get_next_id("SW - Cisco 9300X 24X") == "d300"
        assert assigner.get_next_id("SW - Cisco 9300 12X36M") == "d500"
        assert assigner.get_next_id("SW - Cisco 9300X 24X") == "d301"
        assert assigner.get_next_id("SW - Cisco 9300 12X36M") == "d501"

    def test_get_next_id_nocs_share_counter(self):
        """Test all NOCs share same f100 counter."""
        assigner = IconIdAssigner()
        assert assigner.get_next_id("DIST - Micro NOC") == "f100"
        assert assigner.get_next_id("DIST - Mini NOC") == "f101"
        assert assigner.get_next_id("DIST - Standard NOC") == "f102"

    def test_get_next_id_unknown_returns_none(self):
        """Test unknown device returns None."""
        assigner = IconIdAssigner()
        assert assigner.get_next_id("Unknown Device") is None
        assert assigner.get_next_id("PWR - EcoFlow Battery") is None  # No ID configured

    def test_reset_clears_counters(self):
        """Test reset clears all counters."""
        assigner = IconIdAssigner()
        assigner.get_next_id("AP - Cisco MR36H")
        assigner.get_next_id("AP - Cisco MR36H")
        assigner.reset()
        assert assigner._counters == {}
        assert assigner.get_next_id("AP - Cisco MR36H") == "j100"

    def test_get_current_counts(self):
        """Test get_current_counts returns copy of counters."""
        assigner = IconIdAssigner()
        assigner.get_next_id("AP - Cisco MR36H")
        counts = assigner.get_current_counts()
        assert counts == {"j_100": 100}
        # Verify it's a copy
        counts["j_100"] = 999
        assert assigner._counters["j_100"] == 100

    def test_multiple_device_types_independent(self):
        """Test different device types have independent counters."""
        assigner = IconIdAssigner()
        assert assigner.get_next_id("AP - Cisco MR36H") == "j100"
        assert assigner.get_next_id("AP - Cisco MR78") == "k100"
        assert assigner.get_next_id("AP - Cisco MR36H") == "j101"
        assert assigner.get_next_id("AP - Cisco MR78") == "k101"

    def test_idf_independent_counters(self):
        """Test IDF switches have independent e-prefix counters."""
        assigner = IconIdAssigner()
        assert assigner.get_next_id("SW - IDF Cisco 9300 24X") == "e100"
        assert assigner.get_next_id("SW - IDF Cisco 9300X 24X") == "e300"
        assert assigner.get_next_id("SW - IDF Cisco 9300 24X") == "e101"
