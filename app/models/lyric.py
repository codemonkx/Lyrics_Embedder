from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class LyricLine(BaseModel):
    timestamp: float
    text: str
    time_tag: str

class Lyric(BaseModel):
    id: Optional[int] = None
    file_path: str
    type: str  # "LRC" or "TTML"
    last_timestamp: float = 0.0
    plain_text_preview: str = ""
    lines: List[LyricLine] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=dict)

class LyricMatch(BaseModel):
    song_id: int
    lyric_id: int
    score: float
    field_scores: Dict[str, float] = Field(default_factory=dict)
