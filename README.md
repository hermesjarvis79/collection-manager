# Collection Manager

A Windows 11 desktop application for managing movie collections with smart storage management. Built with Python + PyQt6 + QML.

## Features

- **Folder Watcher** — Automatically detects new movie files in a designated folder
- **Smart Filename Parsing** — Cleans release tags, codec info, and group names using regex
- **Rich Metadata** — Fetches cover art, ratings, synopsis, cast, and trailers from TMDB
- **Dashboard UI** — Dark-themed cyberpunk HUD with carousel stage and grid view
- **Cinematic Carousel** — Full-color cover art with premiere-style lighting effects
- **Storage Management** — Configurable thresholds with auto-delete option (off by default)
- **VLC Integration** — Launches trailers externally in VLC

## Tech Stack

| Component | Choice |
|---|---|
| Language | Python 3.11+ |
| Framework | PyQt6 + QML |
| Database | sqlite3 (stdlib) |
| Folder Watching | `watchdog` |
| Movie Metadata | TMDB API |
| Video Playback | External VLC (CLI) |
| Packaging | PyInstaller |

## Project Structure

```
collection-manager/
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── src/
│   ├── __init__.py
│   ├── app.py               # Main application window & QML loader
│   ├── database.py          # SQLite database initialization & queries
│   ├── folder_watcher.py    # watchdog-based folder monitoring
│   ├── filename_parser.py   # Regex-based filename cleanup
│   ├── tmdb_api.py          # TMDB API client
│   ├── vlc_launcher.py      # VLC external launch helper
│   ├── settings.py          # App settings & preferences
│   └── storage_manager.py   # Storage threshold monitoring
├── ui/
│   ├── main.qml             # Main dashboard layout
│   ├── Carousel.qml         # Carousel stage component
│   ├── GridView.qml         # Grid view component
│   ├── StatsPanel.qml       # Cyberpunk HUD stats panel
│   ├── MovieCard.qml        # Individual movie card
│   ├── PreferencesDialog.qml # Settings/preferences dialog
│   └── SetupWizard.qml      # First-run setup wizard
├── resources/
│   ├── icons/               # App icons
│   └── covers/              # Cached cover art (gitignored)
└── tests/
    ├── __init__.py
    ├── test_filename_parser.py
    └── test_database.py
```

## Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and add your TMDB API key
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python main.py`

## License

MIT
