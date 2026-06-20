"""
Collection Manager — Folder Watcher
Monitors a designated folder for new movie files using the watchdog library.
"""

import os
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent


class _MovieHandler(FileSystemEventHandler):
    """Watchdog event handler that filters for video files."""

    VIDEO_EXTENSIONS = {
        '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm',
        '.m4v', '.mpg', '.mpeg', '.ts', '.m2ts', '.vob',
    }

    def __init__(self, signal_callback):
        super().__init__()
        self._signal = signal_callback

    def on_created(self, event):
        if isinstance(event, FileCreatedEvent):
            ext = Path(event.src_path).suffix.lower()
            if ext in self.VIDEO_EXTENSIONS:
                self._signal(event.src_path)


class FolderWatcher(QObject):
    """Watches a folder for new movie files and emits signals."""

    file_created = pyqtSignal(str)  # filepath

    def __init__(self, parent=None):
        super().__init__(parent)
        self._observer: Optional[Observer] = None
        self._folder: Optional[str] = None

    def set_folder(self, path: str):
        """Set the folder to watch."""
        self._folder = path

    def start(self):
        """Start watching the configured folder."""
        if not self._folder or not os.path.isdir(self._folder):
            print(f"Warning: Cannot watch folder: {self._folder}")
            return

        self.stop()  # Stop any existing observer

        self._observer = Observer()
        handler = _MovieHandler(self._signal_wrapper)
        self._observer.schedule(handler, self._folder, recursive=False)
        self._observer.start()
        print(f"Watching folder: {self._folder}")

    def stop(self):
        """Stop the folder watcher."""
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None

    def _signal_wrapper(self, filepath: str):
        """Thread-safe signal emission."""
        self.file_created.emit(filepath)

    def __del__(self):
        self.stop()
