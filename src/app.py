"""
Collection Manager — Application Core
Initializes the QML engine, loads the main UI, and wires up backend components.
"""

import sys
import os
from pathlib import Path

from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QUrl

from src.database import Database
from src.folder_watcher import FolderWatcher
from src.settings import Settings
from src.tmdb_api import TmdbClient
from src.vlc_launcher import VlcLauncher
from src.storage_manager import StorageManager


# ── QML-exposed backend classes ──────────────────────────────────────────────

class DatabaseBridge(QObject):
    """Exposes database operations to QML."""

    moviesChanged = pyqtSignal()
    movieAdded = pyqtSignal(str)  # title
    movieRemoved = pyqtSignal(int)  # id

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self._db = db

    @pyqtSlot(result='QVariantList')
    def getAllMovies(self) -> list:
        """Return all movies as a list of dicts for QML."""
        return self._db.get_all_movies()

    @pyqtSlot(str, result='QVariant')
    def searchMovie(self, query: str) -> dict:
        """Search TMDB and return the best match."""
        return {}

    @pyqtSlot(int, result=bool)
    def deleteMovie(self, movie_id: int) -> bool:
        """Soft-delete a movie by ID."""
        result = self._db.soft_delete_movie(movie_id)
        if result:
            self.movieRemoved.emit(movie_id)
            self.moviesChanged.emit()
        return result

    @pyqtSlot(int, result='QVariantList')
    def getOldestMovies(self, limit: int = 10) -> list:
        """Return the oldest movies by date_added."""
        return self._db.get_oldest_movies(limit)


class SettingsBridge(QObject):
    """Exposes settings to QML."""

    settingsChanged = pyqtSignal()

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self._settings = settings

    @pyqtSlot(str, result='QVariant')
    def get(self, key: str):
        return self._settings.get(key)

    @pyqtSlot(str, 'QVariant')
    def set(self, key: str, value):
        self._settings.set(key, value)
        self.settingsChanged.emit()

    @pyqtSlot(result='QVariant')
    def getAll(self):
        return self._settings.get_all()

    @pyqtSlot(result=str)
    def getWatchedFolder(self):
        return self._settings.get("watched_folder") or ""

    @pyqtSlot(str)
    def setWatchedFolder(self, path: str):
        self._settings.set("watched_folder", path)
        self.settingsChanged.emit()

    @pyqtSlot(result=str)
    def getThresholdType(self):
        return self._settings.get("threshold_type") or "percentage"

    @pyqtSlot(result=float)
    def getThresholdValue(self):
        return float(self._settings.get("threshold_value") or 85)

    @pyqtSlot(result=bool)
    def getAutoDelete(self):
        return self._settings.get("auto_delete") == "true"

    @pyqtSlot(bool)
    def setAutoDelete(self, enabled: bool):
        self._settings.set("auto_delete", "true" if enabled else "false")
        self.settingsChanged.emit()


class StorageBridge(QObject):
    """Exposes storage stats to QML."""

    thresholdReached = pyqtSignal()

    def __init__(self, storage: StorageManager, parent=None):
        super().__init__(parent)
        self._storage = storage

    @pyqtSlot(result='QVariant')
    def getStats(self) -> dict:
        return self._storage.get_stats()

    @pyqtSlot(result=float)
    def getUsedPercent(self) -> float:
        return self._storage.get_used_percent()

    @pyqtSlot(result=bool)
    def isThresholdReached(self) -> bool:
        return self._storage.is_threshold_reached()

    @pyqtSlot(int, result='QVariantList')
    def getMoviesToDelete(self, count: int = 5) -> list:
        return self._storage.get_movies_to_delete(count)


class FolderWatcherBridge(QObject):
    """Exposes folder watcher signals to QML."""

    fileDetected = pyqtSignal(str)  # filepath

    def __init__(self, watcher: FolderWatcher, parent=None):
        super().__init__(parent)
        self._watcher = watcher
        self._watcher.file_created.connect(self.fileDetected)

    @pyqtSlot(str)
    def setFolder(self, path: str):
        self._watcher.set_folder(path)

    @pyqtSlot()
    def start(self):
        self._watcher.start()

    @pyqtSlot()
    def stop(self):
        self._watcher.stop()


class VlcBridge(QObject):
    """Exposes VLC launcher to QML."""

    def __init__(self, vlc: VlcLauncher, parent=None):
        super().__init__(parent)
        self._vlc = vlc

    @pyqtSlot(str)
    def playTrailer(self, youtube_url: str):
        self._vlc.play(youtube_url)


# ── Application Entry Point ──────────────────────────────────────────────────

def main():
    app = QGuiApplication(sys.argv)
    app.setApplicationName("Collection Manager")
    app.setOrganizationName("hermesjarvis79")

    # Initialize backend components
    db = Database()
    settings = Settings(db)
    tmdb = TmdbClient()
    vlc = VlcLauncher(settings)
    storage = StorageManager(settings, db)
    watcher = FolderWatcher()

    # Create QML engine
    engine = QQmlApplicationEngine()

    # Expose backend bridges to QML context
    engine.rootContext().setContextProperty("dbBridge", DatabaseBridge(db))
    engine.rootContext().setContextProperty("settingsBridge", SettingsBridge(settings))
    engine.rootContext().setContextProperty("storageBridge", StorageBridge(storage))
    engine.rootContext().setContextProperty("watcherBridge", FolderWatcherBridge(watcher))
    engine.rootContext().setContextProperty("vlcBridge", VlcBridge(vlc))

    # Load main QML — ui/ is at the project root (parent of src/)
    project_root = Path(__file__).parent.parent
    qml_path = project_root / "ui" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))

    if not engine.rootObjects():
        print("ERROR: Failed to load QML. Check ui/main.qml exists and is valid.")
        sys.exit(1)

    # Start folder watcher if configured
    watched_folder = settings.get("watched_folder")
    if watched_folder and os.path.isdir(watched_folder):
        watcher.set_folder(watched_folder)
        watcher.start()

    sys.exit(app.exec())
