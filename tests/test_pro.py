import pytest
from app.models.track import Track
from app.models.lyric import Lyric
from app.models.analysis import AudioAnalysis
from app.database.database import DatabaseManager
from app.database.repositories import TrackRepository, LyricRepository, MatchRepository
from app.lyrics.lrc import LRCParser
from app.lyrics.ttml import TTMLParser
from app.lyrics.matcher import MatchingEngine
from app.audio.fft import FFTAnalyzer
import numpy as np

def test_pydantic_track_model():
    track = Track(file_path="test.flac", title="Test Track", artist="Test Artist", date_modified="2026-08-09 00:00")
    assert track.title == "Test Track"
    assert track.artist == "Test Artist"
    assert track.date_modified == "2026-08-09 00:00"

def test_lrc_parser():
    lrc_text = "[00:12.50] Hello World\n[00:15.00] Second Line"
    res = LRCParser.parse_text(lrc_text)
    assert len(res["lines"]) == 2
    assert res["lines"][0].text == "Hello World"
    assert res["lines"][0].timestamp == 12.50

def test_ttml_parser():
    xml_text = '<tt><body><div><p begin="00:00:10.500">TTML Line</p></div></body></tt>'
    res = TTMLParser.parse_text(xml_text)
    assert len(res["lines"]) == 1
    assert res["lines"][0].text == "TTML Line"
    assert res["lines"][0].timestamp == 10.50

def test_matching_engine():
    song = {"title": "Pudhu Vellai Mazhai", "artist": "A. R. Rahman", "file_path": "song.flac"}
    lyric = {"metadata": {"ti": "Pudhu Vellai Mazhai", "ar": "A. R. Rahman"}, "file_path": "song.lrc"}
    score, breakdown = MatchingEngine.calculate_match_score(song, lyric)
    assert score >= 90.0
    assert "title" in breakdown

def test_fft_analyzer():
    sr = 44100
    t = np.linspace(0, 1.0, sr)
    data = (np.sin(2 * np.pi * 1000 * t) * 32767).astype(np.int16)
    freqs, mags, cutoff, method = FFTAnalyzer.calculate_spectrum(sr, data)
    assert len(freqs) > 0
    assert len(mags) > 0
    assert cutoff > 0

def test_sqlalchemy_repositories(tmp_path):
    db_file = tmp_path / "test.db"
    db_mgr = DatabaseManager(str(db_file))
    session = db_mgr.get_session()
    
    t_repo = TrackRepository(session)
    track = Track(file_path=str(tmp_path / "song.mp3"), title="SQL Song", artist="SQL Artist")
    saved = t_repo.add_or_update(track)
    assert saved.id is not None

    all_t = t_repo.get_all()
    assert len(all_t) == 1
    assert all_t[0].title == "SQL Song"
    session.close()
