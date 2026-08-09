from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import SongModel, LyricModel, MatchModel, SettingModel
from app.models.track import Track
from app.models.lyric import Lyric
from app.models.library import LibraryStats
from app.core.logging import logger

class TrackRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Track]:
        songs = self.session.query(SongModel).all()
        tracks = []
        for s in songs:
            t = Track(
                id=s.id,
                file_path=s.file_path,
                title=s.title or "",
                artist=s.artist or "",
                album=s.album or "",
                duration=s.duration or 0.0,
                status=s.status or "Unmatched",
                lyric_id=s.lyric_id,
                sample_rate=s.sample_rate,
                bits_per_sample=s.bits_per_sample,
                channels=s.channels,
                file_size=s.file_size,
                bitrate=s.bitrate,
                replay_gain=s.replay_gain,
                date_modified=s.date_modified,
                actual_sample_rate=s.actual_sample_rate,
                spectral_cutoff=s.spectral_cutoff,
                legit=s.legit,
                legit_reason=s.legit_reason,
                lyric_path=s.lyric.file_path if s.lyric else None
            )
            tracks.append(t)
        return tracks

    def add_or_update(self, track: Track) -> Track:
        existing = self.session.query(SongModel).filter_by(file_path=track.file_path).first()
        if existing:
            existing.title = track.title
            existing.artist = track.artist
            existing.album = track.album
            existing.duration = track.duration
            existing.status = track.status
            existing.lyric_id = track.lyric_id
            existing.sample_rate = track.sample_rate
            existing.bits_per_sample = track.bits_per_sample
            existing.channels = track.channels
            existing.file_size = track.file_size
            existing.bitrate = track.bitrate
            existing.replay_gain = track.replay_gain
            existing.date_modified = track.date_modified
            if track.actual_sample_rate is not None:
                existing.actual_sample_rate = track.actual_sample_rate
            if track.spectral_cutoff is not None:
                existing.spectral_cutoff = track.spectral_cutoff
            if track.legit is not None:
                existing.legit = track.legit
            if track.legit_reason is not None:
                existing.legit_reason = track.legit_reason
            self.session.commit()
            track.id = existing.id
            return track
        else:
            new_song = SongModel(
                file_path=track.file_path,
                title=track.title,
                artist=track.artist,
                album=track.album,
                duration=track.duration,
                status=track.status,
                lyric_id=track.lyric_id,
                sample_rate=track.sample_rate,
                bits_per_sample=track.bits_per_sample,
                channels=track.channels,
                file_size=track.file_size,
                bitrate=track.bitrate,
                replay_gain=track.replay_gain,
                date_modified=track.date_modified,
                actual_sample_rate=track.actual_sample_rate,
                spectral_cutoff=track.spectral_cutoff,
                legit=track.legit,
                legit_reason=track.legit_reason
            )
            self.session.add(new_song)
            self.session.commit()
            self.session.refresh(new_song)
            track.id = new_song.id
            return track

    def clear_all(self):
        self.session.query(SongModel).delete()
        self.session.commit()


class LyricRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Lyric]:
        lyrics_models = self.session.query(LyricModel).all()
        return [
            Lyric(
                id=l.id,
                file_path=l.file_path,
                type=l.type,
                last_timestamp=l.last_timestamp,
                plain_text_preview=l.plain_text_preview or ""
            ) for l in lyrics_models
        ]

    def add_or_update(self, lyric: Lyric) -> Lyric:
        existing = self.session.query(LyricModel).filter_by(file_path=lyric.file_path).first()
        if existing:
            existing.type = lyric.type
            existing.last_timestamp = lyric.last_timestamp
            existing.plain_text_preview = lyric.plain_text_preview
            self.session.commit()
            lyric.id = existing.id
            return lyric
        else:
            new_lyr = LyricModel(
                file_path=lyric.file_path,
                type=lyric.type,
                last_timestamp=lyric.last_timestamp,
                plain_text_preview=lyric.plain_text_preview
            )
            self.session.add(new_lyr)
            self.session.commit()
            self.session.refresh(new_lyr)
            lyric.id = new_lyr.id
            return lyric

    def clear_all(self):
        self.session.query(LyricModel).delete()
        self.session.commit()


class MatchRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_match(self, song_id: int, lyric_id: int, score: float):
        existing = self.session.query(MatchModel).filter_by(song_id=song_id, lyric_id=lyric_id).first()
        if existing:
            existing.score = score
        else:
            self.session.add(MatchModel(song_id=song_id, lyric_id=lyric_id, score=score))
        
        # Update song status & lyric_id
        song = self.session.query(SongModel).get(song_id)
        if song:
            song.lyric_id = lyric_id
            song.status = "Matched"
        self.session.commit()

    def clear_all(self):
        self.session.query(MatchModel).delete()
        self.session.commit()


class SettingsRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, key: str, default: str = "") -> str:
        s = self.session.query(SettingModel).get(key)
        return s.value if s else default

    def set(self, key: str, value: str):
        s = self.session.query(SettingModel).get(key)
        if s:
            s.value = str(value)
        else:
            self.session.add(SettingModel(key=key, value=str(value)))
        self.session.commit()
