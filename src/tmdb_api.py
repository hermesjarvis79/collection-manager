"""
Collection Manager — TMDB API Client
Fetches movie metadata, cover art, and trailer information from The Movie Database.
"""

import os
import requests
from pathlib import Path
from typing import Optional, Dict, Any

from dotenv import load_dotenv

load_dotenv()

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"
COVER_SIZE = "w500"  # poster size for covers
BACKDROP_SIZE = "w780"


class TmdbClient:
    """Client for The Movie Database (TMDB) API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TMDB_API_KEY", "")
        self._session = requests.Session()
        self._session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        self._cache_dir = Path.home() / ".collection-manager" / "covers"
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def _get(self, endpoint: str, params: dict = None) -> dict:
        """Make a GET request to TMDB API."""
        if not self.api_key:
            raise ValueError("TMDB API key not configured. Set TMDB_API_KEY in .env")

        params = params or {}
        params["api_key"] = self.api_key

        response = self._session.get(f"{TMDB_BASE_URL}{endpoint}", params=params, timeout=15)
        response.raise_for_status()
        return response.json()

    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[dict]:
        """
        Search for a movie by title. Returns the best match or None.
        """
        params = {"query": title, "include_adult": "false"}
        if year:
            params["year"] = year

        data = self._get("/search/movie", params)
        results = data.get("results", [])

        if not results:
            return None

        # Return the first (best) result
        return results[0]

    def get_movie_details(self, tmdb_id: int) -> dict:
        """
        Get full movie details including credits and videos.
        """
        data = self._get(f"/movie/{tmdb_id}", {
            "append_to_response": "credits,videos"
        })
        return data

    def get_full_metadata(self, title: str, year: Optional[int] = None) -> Optional[dict]:
        """
        Search for a movie and return comprehensive metadata.
        Returns a dict with all fields needed for the database.
        """
        # Step 1: Search
        search_result = self.search_movie(title, year)
        if not search_result:
            return None

        tmdb_id = search_result["id"]

        # Step 2: Get full details
        details = self.get_movie_details(tmdb_id)

        # Step 3: Extract trailer YouTube key
        trailer_key = self._extract_trailer_key(details)

        # Step 4: Extract director and cast
        director = self._extract_director(details)
        cast = self._extract_cast(details)

        # Step 5: Build cover art URL
        cover_url = None
        if details.get("poster_path"):
            cover_url = f"{TMDB_IMAGE_BASE}/{COVER_SIZE}{details['poster_path']}"

        return {
            "title": details.get("title", title),
            "tmdb_id": tmdb_id,
            "imdb_id": details.get("imdb_id"),
            "year": year or self._extract_year_from_date(details.get("release_date")),
            "genre": self._extract_genres(details),
            "rating": details.get("vote_average"),
            "synopsis": details.get("overview"),
            "runtime_minutes": details.get("runtime"),
            "director": director,
            "cast": cast,
            "cover_art_url": cover_url,
            "trailer_youtube_key": trailer_key,
        }

    def download_cover(self, cover_url: str, tmdb_id: int) -> Optional[str]:
        """Download cover art and save locally. Returns local file path."""
        if not cover_url:
            return None

        ext = cover_url.split(".")[-1].split("/")[0] or "jpg"
        local_path = self._cache_dir / f"{tmdb_id}.{ext}"

        if local_path.exists():
            return str(local_path)

        try:
            response = self._session.get(cover_url, timeout=30)
            response.raise_for_status()
            local_path.write_bytes(response.content)
            return str(local_path)
        except Exception as e:
            print(f"Warning: Failed to download cover for {tmdb_id}: {e}")
            return None

    def get_trailer_url(self, youtube_key: str) -> str:
        """Build a YouTube URL from a video key."""
        if youtube_key:
            return f"https://www.youtube.com/watch?v={youtube_key}"
        return ""

    # ── Private helpers ───────────────────────────────────────────────────

    @staticmethod
    def _extract_trailer_key(details: dict) -> Optional[str]:
        """Extract the first YouTube trailer key from movie videos."""
        videos = details.get("videos", {}).get("results", [])
        for video in videos:
            if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                return video.get("key")
        # Fallback: any YouTube video
        for video in videos:
            if video.get("site") == "YouTube":
                return video.get("key")
        return None

    @staticmethod
    def _extract_director(details: dict) -> str:
        """Extract the director name from credits."""
        crew = details.get("credits", {}).get("crew", [])
        for person in crew:
            if person.get("job") == "Director":
                return person.get("name", "")
        return ""

    @staticmethod
    def _extract_cast(details: dict, limit: int = 5) -> str:
        """Extract top cast members as a comma-separated string."""
        cast_list = details.get("credits", {}).get("cast", [])
        names = [c["name"] for c in cast_list[:limit] if c.get("name")]
        return ", ".join(names)

    @staticmethod
    def _extract_genres(details: dict) -> str:
        """Extract genres as a comma-separated string."""
        genres = details.get("genres", [])
        return ", ".join(g["name"] for g in genres if g.get("name"))

    @staticmethod
    def _extract_year_from_date(date_str: str) -> Optional[int]:
        """Extract year from a date string like '2024-03-15'."""
        if date_str and len(date_str) >= 4:
            try:
                return int(date_str[:4])
            except ValueError:
                return None
        return None
