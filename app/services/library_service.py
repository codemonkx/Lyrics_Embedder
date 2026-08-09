from typing import List, Dict, Any
from PySide6.QtCore import QObject, Signal, Slot, Property
from app.database.database import DatabaseManager
from app.database.repositories import TrackRepository, SettingsRepository
from app.models.track import Track
from app.models.library import LibraryStats
from app.workers.scanner import ScanWorker
from app.monitoring.filesystem import LibraryWatcher
from app.core.config import config_manager
from app.core.logging import logger

class LibraryService(QObject):
    tracksChanged = Signal()
    statsChanged = Signal()
    scanProgress = Signal(int, str)
    scanFinished = Signal()

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self._tracks: List[Dict[str, Any]] = []
        self._stats = LibraryStats()
        self.scan_worker = None

        # Watchdog Filesystem Monitor
        self.watcher = LibraryWatcher(self)
        self.watcher.file_changed.connect(self.on_filesystem_changed)

        self.load_tracks()
        self.start_monitoring_if_enabled()

    def start_monitoring_if_enabled(self):
        music_dir = config_manager.get("music_dir", "")
        if config_manager.get("monitoring_enabled", False) and music_dir:
            self.watcher.start_watching(music_dir)

    def load_tracks(self):
        session = self.db_manager.get_session()
        try:
            repo = TrackRepository(session)
            tracks_objs = repo.get_all()
            self._tracks = [t.model_dump() for t in tracks_objs]
            
            matched = sum(1 for t in tracks_objs if t.lyric_id is not None)
            embedded = sum(1 for t in tracks_objs if t.status == "Embedded")
            suspicious = sum(1 for t in tracks_objs if t.legit == 0)
            
            self._stats = LibraryStats(
                total_songs=len(tracks_objs),
                matched_songs=matched,
                embedded_songs=embedded,
                unmatched_songs=len(tracks_objs) - matched,
                suspicious_songs=suspicious
            )
            self.tracksChanged.emit()
            self.statsChanged.emit()
        finally:
            session.close()

    @Property(list, notify=tracksChanged)
    def tracks(self) -> List[Dict[str, Any]]:
        return self._tracks

    @Property(int, notify=statsChanged)
    def totalTracks(self) -> int:
        return self._stats.total_songs

    @Property(int, notify=statsChanged)
    def matchedTracks(self) -> int:
        return self._stats.matched_songs

    @Property(int, notify=statsChanged)
    def unmatchedTracks(self) -> int:
        return self._stats.unmatched_songs

    @Property(int, notify=statsChanged)
    def suspiciousTracks(self) -> int:
        return self._stats.suspicious_songs

    @Slot(str, str, float, bool)
    def startScan(self, music_dir: str, lyrics_dir: str, threshold: float = 60.0, verify_audio: bool = True):
        config_manager.set("music_dir", music_dir)
        config_manager.set("lyrics_dir", lyrics_dir)
        config_manager.set("threshold", threshold)
        config_manager.set("verify_audio", verify_audio)

        weights = config_manager.get("weights", {})

        self.scan_worker = ScanWorker(
            self.db_manager, music_dir, lyrics_dir, threshold, verify_audio, weights
        )
        self.scan_worker.progress.connect(self.scanProgress.emit)
        self.scan_worker.finished.connect(self.on_scan_worker_finished)
        self.scan_worker.start()

        if config_manager.get("monitoring_enabled", False):
            self.watcher.start_watching(music_dir)

    def on_scan_worker_finished(self, stats: dict):
        self.load_tracks()
        self.scanFinished.emit()

    def on_filesystem_changed(self, file_path: str):
        logger.info(f"Filesystem watcher trigger re-scan for: {file_path}")
        m_dir = config_manager.get("music_dir", "")
        l_dir = config_manager.get("lyrics_dir", "")
        if m_dir:
            self.startScan(m_dir, l_dir)

    @Slot()
    def resetLibrary(self):
        session = self.db_manager.get_session()
        try:
            TrackRepository(session).clear_all()
            self.load_tracks()
        finally:
            session.close()
