import os
from pathlib import Path

# Application Metadata
APP_NAME = "LyricForge Pro"
APP_VERSION = "2.0.0 PRO"
APP_ORGANIZATION = "LyricForge"
APP_DOMAIN = "lyricforge.pro"

# Color Palette Design Tokens (Nothing OS Dark Visual Identity)
COLOR_BG_BASE = "#0B0C0E"
COLOR_BG_SURFACE = "#121417"
COLOR_BG_ELEVATED = "#181B1F"
COLOR_BORDER_SUBTLE = "#272A2F"
COLOR_BORDER_FOCUS = "#3D424D"

COLOR_ACCENT_RED = "#FF002B"
COLOR_ACCENT_RED_HOVER = "#D40024"
COLOR_ACCENT_RED_DIM = "#2A0910"

COLOR_TEXT_PRIMARY = "#F2F2F2"
COLOR_TEXT_SECONDARY = "#92969D"
COLOR_TEXT_MUTED = "#62666D"

COLOR_SUCCESS = "#34D399"
COLOR_WARNING = "#FBBF24"
COLOR_ERROR = "#F87171"

# Supported File Formats
SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".flac", ".wav", ".m4a", ".ogg", ".aac", ".wma", ".aiff"}
SUPPORTED_LYRIC_EXTENSIONS = {".lrc", ".ttml", ".xml"}

# Default Matching Engine Thresholds & Matrix Weights
DEFAULT_MATCH_THRESHOLD = 60.0
DEFAULT_WEIGHTS = {
    "title": 0.35,
    "artist": 0.25,
    "album": 0.15,
    "filename": 0.10,
    "duration": 0.10,
    "directory": 0.05
}

# Filesystem Watcher Debounce (ms)
WATCHDOG_DEBOUNCE_MS = 500
