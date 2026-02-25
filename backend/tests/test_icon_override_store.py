"""Tests for IconOverrideStore."""

from pathlib import Path

import pytest

from app.services.icon_override_store import IconOverrideStore


@pytest.fixture
def store(tmp_path: Path) -> IconOverrideStore:
    return IconOverrideStore(tmp_path / "overrides.json")


def test_load_missing_file(store: IconOverrideStore):
    data = store.load()
    assert data["icons"] == {}
    assert data["_meta"]["version"] == 1


def test_save_and_load_roundtrip(store: IconOverrideStore):
    data = {"_meta": {"version": 1}, "icons": {"Test Icon": {"category": "APs"}}}
    store.save(data)
    loaded = store.load()
    assert loaded["icons"]["Test Icon"]["category"] == "APs"
    assert "last_modified" in loaded["_meta"]


def test_set_icon_and_get_icon(store: IconOverrideStore):
    config = {"category": "Switches", "circle_color": [0.1, 0.2, 0.3]}
    store.set_icon("SW - Test", config)
    result = store.get_icon("SW - Test")
    assert result is not None
    assert result["category"] == "Switches"
    assert result["circle_color"] == [0.1, 0.2, 0.3]


def test_get_icon_not_found(store: IconOverrideStore):
    assert store.get_icon("Nonexistent") is None


def test_delete_icon(store: IconOverrideStore):
    store.set_icon("ToDelete", {"category": "Misc"})
    assert store.delete_icon("ToDelete") is True
    assert store.get_icon("ToDelete") is None


def test_delete_nonexistent(store: IconOverrideStore):
    assert store.delete_icon("Nonexistent") is False


def test_list_icons(store: IconOverrideStore):
    store.set_icon("Icon A", {"category": "APs"})
    store.set_icon("Icon B", {"category": "Switches"})
    subjects = store.list_icons()
    assert set(subjects) == {"Icon A", "Icon B"}


def test_get_all_configs_includes_python(store: IconOverrideStore):
    configs = store.get_all_configs()
    subjects = [c["subject"] for c in configs]
    assert "AP - Cisco MR36H" in subjects


def test_get_all_configs_json_overrides_python(store: IconOverrideStore):
    store.set_icon("AP - Cisco MR36H", {
        "category": "APs",
        "circle_color": [1.0, 0.0, 0.0],
        "circle_border_width": 0.75,
        "circle_border_color": [0.0, 0.0, 0.0],
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
        "text_color": [1.0, 1.0, 1.0],
        "id_text_color": None,
        "image_path": "APs/AP - Cisco MR36H.png",
    })
    configs = store.get_all_configs()
    mr36h = [c for c in configs if c["subject"] == "AP - Cisco MR36H"][0]
    assert mr36h["source"] == "json_override"
    assert mr36h["circle_color"] == [1.0, 0.0, 0.0]


def test_atomic_write(store: IconOverrideStore):
    """Ensure file is written atomically (no .tmp left behind)."""
    store.set_icon("Atomic Test", {"category": "APs"})
    tmp_path = store.json_path.with_suffix(".tmp")
    assert not tmp_path.exists()
    assert store.json_path.exists()


def test_build_full_config(store: IconOverrideStore):
    config = store.build_full_config("AP - Cisco MR36H", {"img_scale_ratio": 0.9})
    assert config["img_scale_ratio"] == 0.9
    assert config["category"] == "APs"
    assert config["subject"] == "AP - Cisco MR36H"
