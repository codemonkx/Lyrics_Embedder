from typing import Optional, Union
from pydantic import BaseModel, Field

class Track(BaseModel):
    id: Optional[int] = None
    file_path: str
    title: str = ""
    artist: str = ""
    album: str = ""
    duration: float = 0.0
    sample_rate: Optional[int] = None
    bits_per_sample: Optional[int] = None
    channels: Optional[int] = None
    file_size: Optional[int] = None
    bitrate: Optional[float] = None
    replay_gain: Optional[str] = None
    date_modified: Optional[Union[float, str]] = None
    status: str = "Unmatched"
    lyric_id: Optional[int] = None
    actual_sample_rate: Optional[int] = None
    spectral_cutoff: Optional[float] = None
    legit: Optional[int] = None  # 1 = Genuine, 0 = Anomaly/Fake
    legit_reason: Optional[str] = None
    lyrics_text: Optional[str] = None
    lyric_path: Optional[str] = None
    match_score: Optional[float] = None
