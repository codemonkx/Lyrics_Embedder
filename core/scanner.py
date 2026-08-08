import os
from pathlib import Path
from typing import List, Set

class FileScanner:
    MUSIC_EXTENSIONS = {'.flac', '.mp3', '.m4a', '.ogg', '.wav'}
    LYRIC_EXTENSIONS = {'.lrc', '.ttml'}
    IGNORE_DIR_NAMES = {'node_modules', '__pycache__', 'venv', 'env', 'build', 'dist'}

    @classmethod
    def _scan_directory(cls, directory: Path, extensions: Set[str]) -> List[Path]:
        """Recursively scans directory structure, skipping hidden/ignored folders."""
        found_files = []
        try:
            for entry in os.scandir(directory):
                # Ignore hidden files/directories and build/cache/dep directories
                if entry.name.startswith('.') or entry.name in cls.IGNORE_DIR_NAMES:
                    continue
                if entry.is_dir(follow_symlinks=False):
                    found_files.extend(cls._scan_directory(Path(entry.path), extensions))
                elif entry.is_file():
                    suffix = Path(entry.name).suffix.lower()
                    if suffix in extensions:
                        found_files.append(Path(entry.path))
        except Exception:
            pass
        return found_files

    @classmethod
    def scan_music_files(cls, directory: str) -> List[Path]:
        """Recursively scans a directory for supported music files."""
        path = Path(directory)
        if not path.exists():
            return []
        return cls._scan_directory(path, cls.MUSIC_EXTENSIONS)

    @classmethod
    def scan_lyric_files(cls, directory: str) -> List[Path]:
        """Recursively scans a directory for supported lyric files."""
        path = Path(directory)
        if not path.exists():
            return []
        return cls._scan_directory(path, cls.LYRIC_EXTENSIONS)

