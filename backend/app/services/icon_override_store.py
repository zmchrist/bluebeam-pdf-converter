"""JSON file persistence for icon configuration overrides."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.icon_config import (
    CATEGORY_DEFAULTS,
    ICON_CATEGORIES,
    get_icon_config,
)

logger = logging.getLogger(__name__)


class IconOverrideStore:
    """Manages reading/writing icon overrides to a JSON file."""

    def __init__(self, json_path: Path):
        self.json_path = json_path

    def load(self) -> dict[str, Any]:
        """Load the entire JSON file. Returns empty structure if file doesn't exist."""
        if not self.json_path.exists():
            return {"_meta": {"version": 1}, "icons": {}}
        try:
            with open(self.json_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Failed to load icon overrides: {e}")
            return {"_meta": {"version": 1}, "icons": {}}

    def save(self, data: dict[str, Any]) -> None:
        """Atomic write: write to temp file then rename."""
        data["_meta"] = {
            "version": 1,
            "last_modified": datetime.now(timezone.utc).isoformat(),
        }
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.json_path.with_suffix(".tmp")
        with open(tmp_path, "w") as f:
            json.dump(data, f, indent=2)
        tmp_path.rename(self.json_path)

    def get_icon(self, subject: str) -> dict[str, Any] | None:
        """Get a single icon config from JSON, or None."""
        data = self.load()
        return data.get("icons", {}).get(subject)

    def set_icon(self, subject: str, config: dict[str, Any]) -> None:
        """Upsert a complete icon config."""
        data = self.load()
        if "icons" not in data:
            data["icons"] = {}
        data["icons"][subject] = config
        self.save(data)

    def delete_icon(self, subject: str) -> bool:
        """Remove an icon from JSON. Returns True if it existed."""
        data = self.load()
        icons = data.get("icons", {})
        if subject in icons:
            del icons[subject]
            self.save(data)
            return True
        return False

    def list_icons(self) -> list[str]:
        """Return all icon subjects in JSON."""
        data = self.load()
        return list(data.get("icons", {}).keys())

    def get_all_configs(self) -> list[dict[str, Any]]:
        """
        Return merged list of all icons.

        Python-configured icons are the base. JSON overrides replace
        Python entries for the same subject. JSON-only entries are
        included as 'custom' source.
        """
        result: dict[str, dict[str, Any]] = {}

        # Start with all Python-configured icons
        for subject in ICON_CATEGORIES:
            config = get_icon_config(subject)
            if config:
                config["subject"] = subject
                config["source"] = "python"
                # Ensure defaults for fields that may not be in category defaults
                config.setdefault("img_x_offset", 0.0)
                config.setdefault("img_y_offset", 0.0)
                config.setdefault("model_text_override", None)
                config.setdefault("model_uppercase", False)
                config.setdefault("no_image", False)
                config.setdefault("id_box_y_offset", 0.0)
                config.setdefault("no_id_box", False)
                config.setdefault("layer_order", ["gear_image", "brand_text", "model_text"])
                result[subject] = config

        # Apply JSON overrides
        data = self.load()
        for subject, json_config in data.get("icons", {}).items():
            if subject in result:
                # Override existing Python config
                json_config["source"] = "json_override"
                json_config["subject"] = subject
                result[subject] = json_config
            else:
                # Custom icon (not in Python config)
                json_config["source"] = "custom"
                json_config["subject"] = subject
                result[subject] = json_config

        return list(result.values())

    def apply_to_multiple(
        self, subjects: list[str], updates: dict[str, Any]
    ) -> int:
        """Apply partial updates to multiple icons at once. Returns count of updated icons."""
        data = self.load()
        if "icons" not in data:
            data["icons"] = {}

        count = 0
        for subject in subjects:
            full_config = self.build_full_config(subject, updates)
            save_config = {
                k: v for k, v in full_config.items() if k not in ("subject", "source")
            }
            data["icons"][subject] = save_config
            count += 1

        if count > 0:
            self.save(data)
        return count

    def build_full_config(self, subject: str, partial: dict[str, Any]) -> dict[str, Any]:
        """
        Build a complete config by merging partial updates onto the current config.

        Priority: JSON override (current state) > Python config > category defaults.
        Apply partial updates on top.
        """
        # Check JSON override first - this is the current tuned state
        existing_json = self.get_icon(subject)
        if existing_json:
            base = existing_json.copy()
        else:
            # Fall back to Python config
            base = get_icon_config(subject)
            if not base:
                # New icon - use category defaults if category provided
                category = partial.get("category", "Misc")
                base = CATEGORY_DEFAULTS.get(category, CATEGORY_DEFAULTS["Misc"]).copy()
                base["category"] = category
                base["image_path"] = None

        # Set defaults for optional fields
        base.setdefault("img_x_offset", 0.0)
        base.setdefault("img_y_offset", 0.0)
        base.setdefault("model_text_override", None)
        base.setdefault("model_uppercase", False)
        base.setdefault("no_image", False)
        base.setdefault("id_box_y_offset", 0.0)
        base.setdefault("no_id_box", False)
        base.setdefault("layer_order", ["gear_image", "brand_text", "model_text"])

        # Apply partial updates (skip None values)
        for key, value in partial.items():
            if value is not None:
                base[key] = value

        base["subject"] = subject
        return base
