"""Tests for Tuner API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(tmp_path):
    """Create test client with temporary override store."""
    from app.config import settings
    import app.routers.tuner as tuner_mod

    # Override the store to use temp path
    original_file = settings.icon_overrides_file
    settings.icon_overrides_file = tmp_path / "test_overrides.json"
    tuner_mod._store = None  # Reset singleton

    yield TestClient(app)

    settings.icon_overrides_file = original_file
    tuner_mod._store = None


def test_list_icons(client):
    resp = client.get("/api/tuner/icons")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 80  # 87+ icons
    subjects = [d["subject"] for d in data]
    assert "AP - Cisco MR36H" in subjects


def test_get_icon(client):
    resp = client.get("/api/tuner/icons/AP - Cisco MR36H")
    assert resp.status_code == 200
    data = resp.json()
    assert data["subject"] == "AP - Cisco MR36H"
    assert data["category"] == "APs"
    assert data["source"] == "python"


def test_get_icon_not_found(client):
    resp = client.get("/api/tuner/icons/Nonexistent Icon")
    assert resp.status_code == 404


def test_save_icon(client):
    resp = client.put(
        "/api/tuner/icons/AP - Cisco MR36H",
        json={"img_scale_ratio": 0.9, "brand_text": "UPDATED"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["img_scale_ratio"] == 0.9
    assert data["brand_text"] == "UPDATED"
    assert data["source"] == "json_override"

    # Verify persistence
    resp2 = client.get("/api/tuner/icons/AP - Cisco MR36H")
    assert resp2.json()["source"] == "json_override"
    assert resp2.json()["img_scale_ratio"] == 0.9


def test_create_icon(client):
    resp = client.post(
        "/api/tuner/icons",
        json={"subject": "NEW - Test Icon", "category": "APs"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["subject"] == "NEW - Test Icon"
    assert data["category"] == "APs"
    assert data["source"] == "custom"


def test_create_duplicate_icon(client):
    resp = client.post(
        "/api/tuner/icons",
        json={"subject": "AP - Cisco MR36H", "category": "APs"},
    )
    assert resp.status_code == 409


def test_create_icon_clone(client):
    resp = client.post(
        "/api/tuner/icons",
        json={
            "subject": "NEW - Cloned",
            "category": "APs",
            "clone_from": "AP - Cisco MR36H",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["category"] == "APs"
    assert data["brand_text"] == "CISCO"


def test_delete_icon(client):
    # First save an override
    client.put(
        "/api/tuner/icons/AP - Cisco MR36H",
        json={"img_scale_ratio": 0.9},
    )
    # Delete the override
    resp = client.delete("/api/tuner/icons/AP - Cisco MR36H")
    assert resp.status_code == 204

    # Should revert to Python config
    resp2 = client.get("/api/tuner/icons/AP - Cisco MR36H")
    assert resp2.json()["source"] == "python"


def test_list_categories(client):
    resp = client.get("/api/tuner/categories")
    assert resp.status_code == 200
    data = resp.json()
    names = [c["name"] for c in data]
    assert "APs" in names
    assert "Switches" in names


def test_list_gear_images(client):
    resp = client.get("/api/tuner/gear-images")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    assert "filename" in data[0]
    assert "thumbnail" in data[0]


def test_list_gear_images_by_category(client):
    resp = client.get("/api/tuner/gear-images?category=APs")
    assert resp.status_code == 200
    data = resp.json()
    for item in data:
        assert item["category"] == "APs"


