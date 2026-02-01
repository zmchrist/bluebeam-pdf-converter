"""Tests for icon renderer service."""

from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image
from PyPDF2 import PdfWriter

from app.services.icon_config import (
    CATEGORY_DEFAULTS,
    ICON_CATEGORIES,
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
