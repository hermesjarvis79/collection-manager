"""
Collection Manager — Database Module
SQLite database initialization and all CRUD operations.
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional


DB_PATH = Path.home() / ".collection-manager" / "collection.db"


class Database:
    """SQLite database for movie collection and app settings."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._init_tables()

    def _init_tables(self):
        """Create tables if they don't exist."""
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                original_filename TEXT,
                cleaned_title TEXT,
                tmdb_id INTEGER,
                imdb_id TEXT,
                year INTEGER,
                genre TEXT,
                rating REAL,
                synopsis TEXT,
                runtime_minutes INTEGER,
                director TEXT,
                cast TEXT,
                cover_art_path TEXT,
                trailer_youtube_key TEXT,
                file_path TEXT UNIQUE,
                file_size_bytes INTEGER DEFAULT 0,
                date_added TEXT DEFAULT (datetime('now')),
                date_deleted TEXT
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_movies_date_added ON movies(date_added);
            CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title);
        """)
        self._conn.commit()

    # ── Movie CRUD ───────────────────────────────────────────────────────

    def add_movie(self, movie_data: dict) -> int:
        """Insert a movie and return its ID."""
        cursor = self._conn.execute("""
            INSERT OR IGNORE INTO movies (
                title, original_filename, cleaned_title, tmdb_id, imdb_id,
                year, genre, rating, synopsis, runtime_minutes, director, cast,
                cover_art_path, trailer_youtube_key, file_path, file_size_bytes
            ) VALUES (
                :title, :original_filename, :cleaned_title, :tmdb_id, :imdb_id,
                :year, :genre, :rating, :synopsis, :runtime_minutes, :director, :cast,
                :cover_art_path, :trailer_youtube_key, :file_path, :file_size_bytes
            )
        """, movie_data)
        self._conn.commit()
        return cursor.lastrowid

    def get_all_movies(self) -> list:
        """Return all non-deleted movies as a list of dicts."""
        cursor = self._conn.execute(
            "SELECT * FROM movies WHERE date_deleted IS NULL ORDER BY title"
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_movie_by_id(self, movie_id: int) -> Optional[dict]:
        """Return a single movie by ID."""
        cursor = self._conn.execute(
            "SELECT * FROM movies WHERE id = ? AND date_deleted IS NULL", (movie_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_oldest_movies(self, limit: int = 10) -> list:
        """Return the oldest movies by date_added."""
        cursor = self._conn.execute(
            "SELECT * FROM movies WHERE date_deleted IS NULL ORDER BY date_added ASC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def soft_delete_movie(self, movie_id: int) -> bool:
        """Mark a movie as deleted (soft delete)."""
        cursor = self._conn.execute(
            "UPDATE movies SET date_deleted = datetime('now') WHERE id = ?",
            (movie_id,)
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def hard_delete_movie(self, movie_id: int) -> bool:
        """Permanently remove a movie from the database."""
        cursor = self._conn.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    def get_movie_count(self) -> int:
        """Return the total number of non-deleted movies."""
        cursor = self._conn.execute(
            "SELECT COUNT(*) FROM movies WHERE date_deleted IS NULL"
        )
        return cursor.fetchone()[0]

    def get_total_size_bytes(self) -> int:
        """Return the total file size of all non-deleted movies."""
        cursor = self._conn.execute(
            "SELECT COALESCE(SUM(file_size_bytes), 0) FROM movies WHERE date_deleted IS NULL"
        )
        return cursor.fetchone()[0]

    # ── Settings ─────────────────────────────────────────────────────────

    def set_setting(self, key: str, value: str):
        self._conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        self._conn.commit()

    def get_setting(self, key: str) -> Optional[str]:
        cursor = self._conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def get_all_settings(self) -> dict:
        cursor = self._conn.execute("SELECT key, value FROM settings")
        return {row[0]: row[1] for row in cursor.fetchall()}

    # ── Cleanup ──────────────────────────────────────────────────────────

    def close(self):
        self._conn.close()
