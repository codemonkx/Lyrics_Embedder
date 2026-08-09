from typing import List, Dict, Any
from PySide6.QtCore import QThread, Signal
from app.core.constants import SUPPORTED_AUDIO_EXTENSIONS, SUPPORTED_LYRIC_EXTENSIONS
from app.database.database import DatabaseManager
from app.database.repositories import TrackRepository, LyricRepository, MatchRepository
from app.metadata.reader import MetadataReader
from app.lyrics.parser import LyricParser
from app.lyrics.matcher import MatchingEngine
from app.audio.verification import AudioVerificationEngine
from app.models.track import Track
from app.models.lyric import Lyric
from app.core.logging import logger

class ScanWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, db_manager: DatabaseManager, music_dir: str, lyrics_dir: str, threshold: float, verify_audio: bool, custom_weights: Dict[str, float]):
        super().__init__()
        self.db_manager = db_manager
        self.music_dir = music_dir
        self.lyrics_dir = lyrics_dir
        self.threshold = threshold
        self.verify_audio = verify_audio
        self.custom_weights = custom_weights
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        session = self.db_manager.get_session()
        try:
            track_repo = TrackRepository(session)
            lyric_repo = LyricRepository(session)
            match_repo = MatchRepository(session)

            self.progress.emit(5, "Scanning music library directory...")
            import os
            from pathlib import Path

            music_files = []
            if os.path.exists(self.music_dir):
                for root, _, files in os.walk(self.music_dir):
                    if self._is_cancelled: return
                    for f in files:
                        if Path(f).suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS:
                            music_files.append(os.path.join(root, f))

            lyric_files = []
            if self.lyrics_dir and os.path.exists(self.lyrics_dir):
                for root, _, files in os.walk(self.lyrics_dir):
                    if self._is_cancelled: return
                    for f in files:
                        if Path(f).suffix.lower() in SUPPORTED_LYRIC_EXTENSIONS:
                            lyric_files.append(os.path.join(root, f))

            total_music = len(music_files)
            total_lyrics = len(lyric_files)

            # Step 1: Parse & Store Lyrics
            self.progress.emit(25, f"Parsing {total_lyrics} lyrics files...")
            parsed_lyrics = []
            for idx, lyr_file in enumerate(lyric_files):
                if self._is_cancelled: return
                lyr_data = LyricParser.parse_file(lyr_file)
                lyric_dto = Lyric(
                    file_path=lyr_data["file_path"],
                    type=lyr_data["type"],
                    last_timestamp=lyr_data["last_timestamp"],
                    plain_text_preview=lyr_data["plain_text_preview"]
                )
                saved_lyric = lyric_repo.add_or_update(lyric_dto)
                lyr_dict = lyric_dto.model_dump()
                lyr_dict["id"] = saved_lyric.id
                lyr_dict["metadata"] = lyr_data["metadata"]
                parsed_lyrics.append(lyr_dict)

            # Step 2: Read & Store Tracks Metadata
            self.progress.emit(45, f"Reading metadata from {total_music} audio tracks...")
            parsed_songs = []
            for idx, song_file in enumerate(music_files):
                if self._is_cancelled: return
                song_data = MetadataReader.read_metadata(song_file)
                track_dto = Track(**song_data)
                saved_track = track_repo.add_or_update(track_dto)
                song_dict = track_dto.model_dump()
                song_dict["id"] = saved_track.id
                parsed_songs.append(song_dict)

            # Step 3: Optional Audio Verification
            if self.verify_audio and total_music > 0:
                self.progress.emit(65, "Inspecting audio integrity & cutoff frequencies...")
                for idx, song in enumerate(parsed_songs):
                    if self._is_cancelled: return
                    res = AudioVerificationEngine.verify_file(song["file_path"])
                    song["actual_sample_rate"] = res.actual_sample_rate
                    song["spectral_cutoff"] = res.spectral_cutoff
                    song["legit"] = res.legit
                    song["legit_reason"] = res.reason
                    
                    t_obj = Track(**song)
                    track_repo.add_or_update(t_obj)

            # Step 4: Fuzzy Matching Engine
            if parsed_lyrics:
                self.progress.emit(85, "Running weighted RapidFuzz lyric matcher...")
                matches = MatchingEngine.find_matches(parsed_songs, parsed_lyrics, self.threshold, self.custom_weights)
                for song_id, lyric_id, score in matches:
                    if self._is_cancelled: return
                    match_repo.save_match(song_id, lyric_id, score)

            self.progress.emit(100, "Library scan complete.")
            all_tracks = track_repo.get_all()
            stats = {
                "total_songs": len(all_tracks),
                "matched_songs": sum(1 for t in all_tracks if t.lyric_id is not None),
                "unmatched_songs": sum(1 for t in all_tracks if t.lyric_id is None),
                "suspicious_songs": sum(1 for t in all_tracks if t.legit == 0)
            }
            self.finished.emit(stats)

        except Exception as e:
            logger.error(f"ScanWorker error: {e}")
            self.error.emit(str(e))
        finally:
            session.close()
