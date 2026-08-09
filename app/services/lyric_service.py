from typing import List, Dict, Any
from PySide6.QtCore import QObject, Signal, Slot
from app.database.database import DatabaseManager
from app.database.repositories import TrackRepository, LyricRepository, MatchRepository
from app.lyrics.parser import LyricParser
from app.models.lyric import Lyric
from app.workers.lyrics import EmbedWorker
from app.core.config import config_manager
from app.core.logging import logger

class LyricService(QObject):
    embedProgress = Signal(int, str)
    embedLog = Signal(str)
    embedFinished = Signal(dict)

    def __init__(self, db_manager: DatabaseManager, library_service=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.library_service = library_service
        self.embed_worker = None

    @Slot(int, result=str)
    def getLyricPreview(self, song_id: int) -> str:
        session = self.db_manager.get_session()
        try:
            track = session.query(TrackRepository(session).session.query(SongModel).get(song_id))
            song = session.query(SongModel).get(song_id)
            if song and song.lyric:
                data = LyricParser.parse_file(song.lyric.file_path)
                return data.get("plain_text_preview", "")
            return "[No lyrics matched for this track.]"
        except Exception:
            return "[Error loading lyric file.]"
        finally:
            session.close()

    @Slot(int, str)
    def manualMatchLyric(self, song_id: int, lyric_file_path: str):
        session = self.db_manager.get_session()
        try:
            lyr_repo = LyricRepository(session)
            match_repo = MatchRepository(session)

            lyr_data = LyricParser.parse_file(lyric_file_path)
            lyric_dto = Lyric(
                file_path=lyr_data["file_path"],
                type=lyr_data["type"],
                last_timestamp=lyr_data["last_timestamp"],
                plain_text_preview=lyr_data["plain_text_preview"]
            )
            saved_lyric = lyr_repo.add_or_update(lyric_dto)
            match_repo.save_match(song_id, saved_lyric.id, 100.0)

            if self.library_service:
                self.library_service.load_tracks()
        finally:
            session.close()

    @Slot(list)
    def embedSelectedTracks(self, song_ids: List[int]):
        keep_backup = config_manager.get("keep_backup", True)
        self.embed_worker = EmbedWorker(self.db_manager, song_ids, keep_backup)
        self.embed_worker.progress.connect(self.embedProgress.emit)
        self.embed_worker.log.connect(self.embedLog.emit)
        self.embed_worker.finished.connect(self.on_embed_finished)
        self.embed_worker.start()

    def on_embed_finished(self, results: dict):
        if self.library_service:
            self.library_service.load_tracks()
        self.embedFinished.emit(results)
