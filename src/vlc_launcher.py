"""
Collection Manager — VLC Launcher
Launches VLC media player with a given URL (e.g., YouTube trailer).
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


class VlcLauncher:
    """Handles launching VLC with a given media URL."""

    def __init__(self, settings=None):
        self._settings = settings
        self._vlc_path = self._find_vlc()

    def _find_vlc(self) -> Optional[str]:
        """Locate the VLC executable."""
        # Check settings first
        if self._settings:
            configured = self._settings.get("vlc_path")
            if configured and os.path.isfile(configured):
                return configured

        # Check environment
        env_path = os.getenv("VLC_PATH")
        if env_path and os.path.isfile(env_path):
            return env_path

        # Platform-specific defaults
        if sys.platform == "win32":
            candidates = [
                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
            ]
            for path in candidates:
                if os.path.isfile(path):
                    return path
        else:
            # Linux / macOS
            for cmd in ["vlc", "/usr/bin/vlc", "/Applications/VLC.app/Contents/MacOS/VLC"]:
                try:
                    subprocess.run([cmd, "--version"], capture_output=True, timeout=5)
                    return cmd
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue

        return None

    def play(self, url: str):
        """Launch VLC with the given URL."""
        if not self._vlc_path:
            print("ERROR: VLC not found. Please configure the path in Preferences.")
            return

        try:
            subprocess.Popen(
                [self._vlc_path, url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"Launched VLC with: {url}")
        except Exception as e:
            print(f"ERROR: Failed to launch VLC: {e}")

    @property
    def is_available(self) -> bool:
        return self._vlc_path is not None
