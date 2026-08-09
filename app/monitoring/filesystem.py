import time
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QTimer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.core.constants import WATCHDOG_DEBOUNCE_MS, SUPPORTED_AUDIO_EXTENSIONS, SUPPORTED_LYRIC_EXTENSIONS
from app.core.logging import logger

class LibraryChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_any_event(self, event):
        if event.is_directory:
            return
        ext = Path(event.src_path).suffix.lower()
        if ext in SUPPORTED_AUDIO_EXTENSIONS or ext in SUPPORTED_LYRIC_EXTENSIONS:
            self.callback(event.src_path)


class LibraryWatcher(QObject):
    file_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.observer = None
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(WATCHDOG_DEBOUNCE_MS)
        self._debounce_timer.timeout.connect(self._on_debounce_timeout)
        self._pending_files = set()

    def start_watching(self, path: str):
        self.stop_watching()
        if not path or not Path(path).exists():
            logger.warning(f"Watchdog cannot monitor non-existent directory: {path}")
            return

        try:
            handler = LibraryChangeHandler(self._handle_raw_event)
            self.observer = Observer()
            self.observer.schedule(handler, path, recursive=True)
            self.observer.start()
            logger.info(f"Watchdog library monitoring active for: {path}")
        except Exception as e:
            logger.error(f"Failed to start Watchdog library watcher for {path}: {e}")

    def stop_watching(self):
        if self.observer and self.observer.is_alive():
            try:
                self.observer.stop()
                self.observer.join(timeout=1.0)
                logger.info("Watchdog library watcher stopped.")
            except Exception as e:
                logger.warning(f"Error stopping Watchdog observer: {e}")
        self.observer = None

    def _handle_raw_event(self, file_path: str):
        """Deduplicate & debounce incoming filesystem events."""
        self._pending_files.add(file_path)
        self._debounce_timer.start()

    def _on_debounce_timeout(self):
        if self._pending_files:
            latest_file = list(self._pending_files)[-1]
            self._pending_files.clear()
            logger.info(f"Debounced filesystem change detected: {latest_file}")
            self.file_changed.emit(latest_file)
