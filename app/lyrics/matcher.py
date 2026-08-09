import re
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor
from rapidfuzz import fuzz

from app.metadata.reader import MetadataReader
from app.core.constants import DEFAULT_WEIGHTS
from app.core.logging import logger

STOP_WORDS = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}

def get_tokens(text: str) -> set:
    if not text:
        return set()
    words = re.findall(r'[a-z0-9]+', text.lower())
    return {w for w in words if len(w) > 1 and w not in STOP_WORDS}


class MatchingEngine:
    @staticmethod
    def string_similarity(s1: str, s2: str) -> float:
        if not s1.strip() and not s2.strip():
            return 100.0
        if not s1.strip() or not s2.strip():
            return 0.0
        return float(fuzz.token_set_ratio(s1.lower(), s2.lower()))

    @staticmethod
    def calculate_duration_score(song_duration: float, lyric_duration: float) -> float:
        if song_duration <= 0 or lyric_duration <= 0:
            return 50.0
        diff = abs(song_duration - lyric_duration)
        if diff <= 5: return 100.0
        elif diff <= 15: return 80.0
        elif diff <= 30: return 50.0
        elif diff <= 60: return 20.0
        return 0.0

    @classmethod
    def calculate_match_score(cls, song: Dict[str, Any], lyric: Dict[str, Any], custom_weights: Optional[Dict[str, float]] = None) -> Tuple[float, Dict[str, float]]:
        song_title = song.get("title", "")
        song_artist = song.get("artist", "")
        song_album = song.get("album", "")
        song_path = Path(song.get("file_path", ""))
        song_stem = song_path.stem

        lyric_path = Path(lyric.get("file_path", ""))
        lyric_stem = lyric_path.stem
        
        lyric_meta = lyric.get("metadata", {})
        lyric_title = lyric_meta.get("ti", "")
        lyric_artist = lyric_meta.get("ar", "")
        lyric_album = lyric_meta.get("al", "")

        fallback = MetadataReader.parse_filename_fallback(lyric_path.name)
        if not lyric_title: lyric_title = fallback["title"] or lyric_stem
        if not lyric_artist: lyric_artist = fallback["artist"] or ""

        track_prefix_re = re.compile(r'^\d+[\s\-_.]*')
        song_title_clean = track_prefix_re.sub('', song_title).strip()
        lyric_title_clean = track_prefix_re.sub('', lyric_title).strip()
        song_stem_clean = track_prefix_re.sub('', song_stem).strip()
        lyric_stem_clean = track_prefix_re.sub('', lyric_stem).strip()

        title_score = cls.string_similarity(song_title_clean, lyric_title_clean)
        artist_score = cls.string_similarity(song_artist, lyric_artist)
        album_score = cls.string_similarity(song_album, lyric_album)
        filename_score = cls.string_similarity(song_stem_clean, lyric_stem_clean)
        
        lyric_duration = lyric.get("last_timestamp", 0.0)
        duration_score = cls.calculate_duration_score(song.get("duration", 0.0), lyric_duration)
        
        dir_score = cls.string_similarity(song_path.parent.name, lyric_path.parent.name)

        weights = dict(custom_weights or DEFAULT_WEIGHTS)
        s = sum(weights.values())
        if s > 0:
            weights = {k: v / s for k, v in weights.items()}

        scores = {
            "title": title_score,
            "artist": artist_score if song_artist and lyric_artist else title_score * 0.8,
            "album": album_score if song_album and lyric_album else title_score * 0.7,
            "filename": filename_score,
            "duration": duration_score,
            "directory": dir_score
        }

        total_score = sum(scores[k] * weights.get(k, 0.0) for k in scores)
        return total_score, scores

    @classmethod
    def find_matches(cls, songs: List[Dict[str, Any]], lyrics: List[Dict[str, Any]], threshold: float = 60.0, custom_weights: Optional[Dict[str, float]] = None) -> List[Tuple[int, int, float]]:
        index = {}
        for lyric in lyrics:
            lyric_id = lyric.get("id")
            if lyric_id is None: continue
            
            lyric_meta = lyric.get("metadata", {})
            lyric_title = lyric_meta.get("ti", "")
            lyric_path = Path(lyric.get("file_path", ""))
            
            fallback = MetadataReader.parse_filename_fallback(lyric_path.name)
            title = lyric_title or fallback["title"] or lyric_path.stem
            
            tokens = get_tokens(title) | get_tokens(lyric_path.stem)
            for token in tokens:
                index.setdefault(token, []).append(lyric)

        def match_song(song: Dict[str, Any]) -> Optional[Tuple[int, int, float]]:
            song_id = song.get("id")
            if song_id is None: return None

            song_title = song.get("title", "")
            song_path = Path(song.get("file_path", ""))
            
            track_prefix_re = re.compile(r'^\d+[\s\-_.]*')
            song_title_clean = track_prefix_re.sub('', song_title).strip()
            song_stem_clean = track_prefix_re.sub('', song_path.stem).strip()
            
            song_tokens = get_tokens(song_title_clean) | get_tokens(song_stem_clean)
            
            candidates = {}
            for token in song_tokens:
                if token in index:
                    for candidate in index[token]:
                        candidates[candidate["id"]] = candidate
            
            candidate_pool = list(candidates.values()) if candidates else lyrics
            
            best_match_id = None
            best_score = 0.0
            
            for lyric in candidate_pool:
                lyric_id = lyric.get("id")
                if lyric_id is None: continue
                
                score, _ = cls.calculate_match_score(song, lyric, custom_weights)
                if score > best_score:
                    best_score = score
                    best_match_id = lyric_id
            
            if best_score >= threshold and best_match_id is not None:
                return (song_id, best_match_id, best_score)
            return None

        matches = []
        max_workers = min(32, (os.cpu_count() or 4) + 4)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(match_song, songs)
            
        for res in results:
            if res is not None:
                matches.append(res)
                
        return matches
