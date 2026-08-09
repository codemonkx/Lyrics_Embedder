from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class SongModel(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String, unique=True, nullable=False)
    title = Column(String, default="")
    artist = Column(String, default="")
    album = Column(String, default="")
    duration = Column(Float, default=0.0)
    status = Column(String, default="Unmatched")
    lyric_id = Column(Integer, ForeignKey("lyrics.id"), nullable=True)
    sample_rate = Column(Integer, nullable=True)
    bits_per_sample = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=True)
    bitrate = Column(Float, nullable=True)
    replay_gain = Column(String, nullable=True)
    date_modified = Column(Float, nullable=True)
    actual_sample_rate = Column(Integer, nullable=True)
    spectral_cutoff = Column(Float, nullable=True)
    legit = Column(Integer, nullable=True)
    legit_reason = Column(String, nullable=True)

    lyric = relationship("LyricModel", back_populates="songs")


class LyricModel(Base):
    __tablename__ = "lyrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String, unique=True, nullable=False)
    type = Column(String, default="LRC")
    last_timestamp = Column(Float, default=0.0)
    plain_text_preview = Column(Text, default="")

    songs = relationship("SongModel", back_populates="lyric")


class MatchModel(Base):
    __tablename__ = "matches"

    song_id = Column(Integer, ForeignKey("songs.id"), primary_key=True)
    lyric_id = Column(Integer, ForeignKey("lyrics.id"), primary_key=True)
    score = Column(Float, nullable=False)


class SettingModel(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
