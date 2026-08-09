from typing import List
from PySide6.QtCore import QThread, Signal
from app.database.database import DatabaseManager
from app.database.repositories import TrackRepository
from app.metadata.writer import MetadataWriter
from app.core.logging import logger

class EmbedWorker(QThread):
    progress = Signal(int, str)
    log = Signal(str)
    finished = Signal(dict)

    def __init__(self, db_manager: DatabaseManager, song_ids: List[int], keep_backup: bool):
        super().__init__()
        self.db_manager = db_manager
        self.song_ids = song_ids
        self.keep_backup = keep_backup
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        session = self.db_manager.get_session()
        try:
            track_repo = TrackRepository(session)
            all_tracks = {t.id: t for t in track_repo.get_all()}

            total = len(self.song_ids)
            embedded_count = 0
            failed_count = 0

            for idx, song_id in enumerate(self.song_ids):
                if self._is_cancelled: return
                track = all_tracks.get(song_id)
                if not track or not track.lyric_path:
                    continue

                from app.lyrics.parser import LyricParser
                lyr_data = LyricParser.parse_file(track.lyric_path)
                lyrics_text = "\n".join([f"{l['time_tag']} {l['text']}" for l in lyr_data["lines"]])

                self.log.emit(f"Embedding lyrics into: {track.title or track.file_path}")
                self.progress.emit(int((idx / total) * 100), f"Writing tags: {idx+1}/{total}")

                legit_info = {
                    "actual_sample_rate": track.actual_sample_rate,
                    "spectral_cutoff": track.spectral_cutoff,
                    "legit": track.legit,
                    "reason": track.legit_reason
                }

                success, msg = MetadataWriter.embed_lyrics(track.file_path, lyrics_text, legit_info)
                if success:
                    track.status = "Embedded"
                    track_repo.add_or_update(track)
                    embedded_count += 1
                    self.log.emit(f"  [SUCCESS] {msg}")
                else:
                    track.status = "Failed"
                    track_repo.add_or_update(track)
                    failed_count += 1
                    self.log.emit(f"  [FAILED] {msg}")

            self.progress.emit(100, "Embedding process completed.")
            self.finished.emit({"embedded": embedded_count, "failed": failed_count})

        except Exception as e:
            logger.error(f"EmbedWorker error: {e}")
            self.finished.emit({"error": str(e)})
        finally:
            session.close()
