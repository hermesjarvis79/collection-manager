"""
Collection Manager — Storage Manager
Monitors disk usage and manages storage thresholds.
"""

import shutil
from typing import Optional


class StorageManager:
    """Monitors storage and determines when movies need to be deleted."""

    def __init__(self, settings, db):
        self._settings = settings
        self._db = db

    def get_stats(self) -> dict:
        """Return storage statistics for the watched folder's drive."""
        folder = self._settings.get("watched_folder") or "/"
        try:
            usage = shutil.disk_usage(folder)
            return {
                "total_gb": round(usage.total / (1024 ** 3), 2),
                "used_gb": round(usage.used / (1024 ** 3), 2),
                "free_gb": round(usage.free / (1024 ** 3), 2),
                "used_percent": round((usage.used / usage.total) * 100, 1),
                "movie_count": self._db.get_movie_count(),
                "library_size_gb": round(self._db.get_total_size_bytes() / (1024 ** 3), 2),
            }
        except Exception as e:
            print(f"Error getting disk usage: {e}")
            return {
                "total_gb": 0,
                "used_gb": 0,
                "free_gb": 0,
                "used_percent": 0,
                "movie_count": 0,
                "library_size_gb": 0,
            }

    def get_used_percent(self) -> float:
        """Return the current disk usage percentage."""
        stats = self.get_stats()
        return stats["used_percent"]

    def is_threshold_reached(self) -> bool:
        """Check if the storage threshold has been breached."""
        threshold_type = self._settings.get("threshold_type") or "percentage"
        threshold_value = float(self._settings.get("threshold_value") or 85)
        stats = self.get_stats()

        if threshold_type == "percentage":
            return stats["used_percent"] >= threshold_value
        elif threshold_type == "absolute_gb":
            return stats["free_gb"] <= threshold_value
        return False

    def get_movies_to_delete(self, count: int = 5) -> list:
        """Return the oldest movies that should be considered for deletion."""
        return self._db.get_oldest_movies(count)

    def get_threshold_label(self) -> str:
        """Return a human-readable threshold description."""
        t_type = self._settings.get("threshold_type") or "percentage"
        t_value = self._settings.get("threshold_value") or "85"
        if t_type == "percentage":
            return f"Alert when disk is {t_value}% full"
        else:
            return f"Alert when free space drops below {t_value} GB"
