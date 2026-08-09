from pydantic import BaseModel

class LibraryStats(BaseModel):
    total_songs: int = 0
    matched_songs: int = 0
    embedded_songs: int = 0
    unmatched_songs: int = 0
    total_lyrics: int = 0
    suspicious_songs: int = 0
