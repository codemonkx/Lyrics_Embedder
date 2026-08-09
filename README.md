# 🎵 LYRICFORGE PRO v2.0
> **Commercial-Grade Desktop Music Library, Synchronized Lyric Embedding & Audio Spectral Analysis Platform**

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI-PySide6%20%2F%20Qt%20Quick%20(QML)-red.svg)](https://www.qt.io/)
[![Database](https://img.shields.io/badge/ORM-SQLAlchemy-green.svg)](https://www.sqlalchemy.org/)
[![Tests](https://img.shields.io/badge/Tests-18%2F18%20Passed-success.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)

---

## 🌟 Overview

**LyricForge Pro** is a modern desktop music library management, synchronized lyric matching, tag embedding, and audio spectral analysis application built with **PySide6 + Qt Quick (QML)**, **SQLAlchemy**, **Pydantic**, **SciPy FFT**, **RapidFuzz**, and **Watchdog**.

Designed with a content-first information architecture inspired by professional digital audio workstations and modern desktop tools, LyricForge Pro offers a stealth dark interface, interactive frequency spectrum graphs, explainable lyric matching algorithms, and zero-loss database safety.

---

## ✨ Key Features

### 1. 🎨 Product-Grade QML Presentation Layer
* **Stealth Dark Design Token System**: Custom dark color palette (`#0B0C0E` base, `#121417` surface, `#181B1F` elevated) with signature Nothing Crimson (`#FF002B`) primary accents.
* **Frameless OS Window System**: Native Windows DWM window dragging (`startSystemMove`), 8-directional border edge drag-resizing (`startSystemResize`), and taskbar minimize/restore integration.
* **High-Density Track Table**: Multi-column track list table (`Title`, `Artist`, `Album`, `Format`, `Duration`, `Status`) with 38px compact row heights, vinyl audio badges (`🎵`), and smooth 120ms hover animations.
* **Contextual Track Inspector Drawer**: Collapsible slide-over drawer detailing format specifications, lyric editor preview, spectrum provider graph, and primary/secondary action buttons.
* **Interactive Tab Filter Bar**: Filter library tracks instantly by status (`ALL TRACKS`, `MATCHED`, `UNMATCHED`, `NEEDS REVIEW`).
* **Floating Toast Notifications**: Non-intrusive bottom-right status overlays for library scans, lyric embedding, and directory changes.

### 2. 📝 Smart Synchronized Lyric Engine
* **Multi-Format Parsing**: Full support for `.lrc` (LRC) and `.ttml` (TTML) synchronized lyric formats.
* **Multi-Stage Fuzzy Matching Engine**: RapidFuzz weighted matching algorithm comparing title, artist, album, duration, and filename.
* **Safe Audio Tag Embedding**: Writes synchronized lyrics directly into ID3, Vorbis, and FLAC tags using Mutagen with automatic safety backups before file modification.

### 3. 🔬 Audio Integrity & Spectral Inspection
* **SciPy FFT Spectral Analyzer**: Calculates magnitude spectrums and brickwall Nyquist cutoff frequencies to detect lossy-transcoded or fake upscale audio files.
* **PyQtGraph QML Image Provider Bridge**: Renders crash-free spectral plots directly inside QML `SpectrumView` widgets via `image://spectrum/file_path`.
* **Zero-Dependency Native WAV Fallback**: Native Python WAV reader (`scipy.io.wavfile.read`) ensuring instant spectrum plotting for `.wav` files even if FFmpeg is absent.
* **Empirical Scientific Evidence Breakdown**: Clear separation between **Observation** (cutoff frequency), **Interpretation** (spectral characteristics), and **Confidence Rating**.

### 4. ⚙️ Real-Time Monitoring & Database Layer
* **SQLAlchemy ORM Data Access**: DAO repository pattern mapping ORM models (`SongModel`, `LyricModel`, `MatchModel`, `SettingModel`) to Pydantic DTOs.
* **Automatic Safety Backups & Schema Migration**: Automatic database backups (`backups/lyricforge_db_backup.db`) and non-destructive column auto-migrations (`PRAGMA table_info`).
* **Debounced Watchdog Listener**: Real-time filesystem monitor with a 500ms single-shot timer queue to deduplicate filesystem changes.
* **Platformdirs Integration**: Standard OS configuration and user log directories (`C:\Users\<User>\AppData\Local\LyricForge`).

---

## 🏗 System Architecture

```
                                  LYRICFORGE PRO
                                        |
                          PySide6 QApplication (main.py)
                                        |
               +------------------------+------------------------+
               |                                                 |
        Qt Quick / QML                                     Python Core
    (Presentation Layer)                                (Engine & Logic)
               |                                                 |
   +-----------+-----------+                      +--------------+--------------+
   |                       |                      |              |              |
 QML Views            PyQtGraph Image          Services       Database        Workers
 (Library, Audio,      Provider Bridge        (Library,      (SQLAlchemy    (Scanning,
  Lyrics, Settings)   (Spectrum Plot)          Lyrics, Audio) + Pydantic)    Matching, FFT)
                                                  |              |              |
                                             +----+----+    +----+----+    +----+----+
                                             |         |    |         |    |         |
                                          Mutagen RapidFuzz SciPy  FFmpeg Watchdog platformdirs
```

---

## 🚀 Getting Started

### Prerequisites
* **Python**: Version `3.11` or newer.
* **FFmpeg** *(Optional)*: Recommended for spectral analysis of compressed formats (`.mp3`, `.flac`, `.m4a`, `.ogg`).

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https.github.com/codemonkx/Lyrics_Embedder.git
cd Lyrics_Embedder
pip install -r requirements.txt
```

### 2. Launching the Application
Launch the LyricForge Pro desktop GUI:
```bash
python app.py
```
Or launch using python package module path:
```bash
python -m app.main
```

### 3. Running Automated Tests
Run the complete unit test suite:
```bash
pytest -v
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Description |
| :--- | :--- |
| `Ctrl + K` or `Ctrl + F` | Focus global search input |
| `Ctrl + R` | Trigger instant music library re-scan |
| `Escape` | Clear active track selection inspector |

---

## 📁 Directory Structure Reference

```
Lyrics_Embedder/
├── app.py                      # Main entry point launcher
├── requirements.txt            # Target dependency manifest
├── README.md                   # Project documentation
├── app/                        # Python Core Package
│   ├── core/                   # Constants, config, logging, application paths
│   ├── models/                 # Pydantic DTO models (Track, Lyric, Analysis)
│   ├── database/               # SQLAlchemy engine, ORM models, repositories
│   ├── audio/                  # FFmpeg decoder, SciPy FFT, SpectrumImageProvider
│   ├── lyrics/                 # LRC, TTML parsers, RapidFuzz matching engine
│   ├── metadata/               # Mutagen metadata reader & tag writer
│   ├── workers/                # Cancellable QThread background threads
│   ├── monitoring/             # Watchdog debounced filesystem watcher
│   ├── services/               # QObject QML bridge controllers
│   └── platform/               # Win32 native event filter
├── qml/                        # Qt Quick / QML Presentation System
│   ├── Main.qml                # Root ApplicationWindow shell
│   ├── theme/                  # Colors.qml, Typography.qml, Metrics.qml
│   ├── components/             # Sidebar, Header, TrackTable, Inspector, FilterBar
│   └── pages/                  # LibraryPage, AnalysisPage, ReportsPage, SettingsPage
└── tests/                      # Automated Test Suite
    ├── test_core.py            # Core engine unit tests
    └── test_pro.py             # SQLAlchemy & Pydantic Pro tests
```

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
