"""
Collection Manager — Settings Manager
Reads and writes app settings from the database.
"""

from typing import Optional


class Settings:
    """Manages application settings stored in the database."""

    DEFAULTS = {
        "watched_folder": "",
        "threshold_type": "percentage",  # "percentage" or "absolute_gb"
        "threshold_value": "85",         # 85% or X GB
        "auto_delete": "false",          # "true" or "false"
        "vlc_path": "",
        "carousel_size": "40",           # 30, 40, 50, or 100
        "stats_visible": "true",
        "setup_complete": "false",
    }

    def __init__(self, db):
        self._db = db
        self._ensure_defaults()

    def _ensure_defaults(self):
        """Set any missing defaults."""
        for key, value in self.DEFAULTS.items():
            if self._db.get_setting(key) is None:
                self._db.set_setting(key, value)

    def get(self, key: str) -> Optional[str]:
        """Get a setting value, falling back to defaults."""
        value = self._db.get_setting(key)
        if value is None:
            return self.DEFAULTS.get(key)
        return value

    def set(self, key: str, value: str):
        """Set a setting value."""
        self._db.set_setting(key, str(value))

    def get_all(self) -> dict:
        """Return all settings as a dict."""
        settings = dict(self.DEFAULTS)
        settings.update(self._db.get_all_settings())
        return settings

    def is_setup_complete(self) -> bool:
        return self.get("setup_complete") == "true"

    def mark_setup_complete(self):
        self.set("setup_complete", "true")
