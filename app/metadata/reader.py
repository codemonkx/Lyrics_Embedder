import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
import mutagen
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, USLT
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis

from app.core.logging import logger

class MetadataReader:
    @staticmethod
    def parse_filename_fallback(filename: str) -> Dict[str, Optional[str]]:
        stem = Path(filename).stem
        track_prefix_re = re.compile(r'^\d+[\s\-_.]*')
        clean_stem = track_prefix_re.sub('', stem).strip()
        
        parts = clean_stem.split(" - ")
        if len(parts) >= 2:
            return {"artist": parts[0].strip(), "title": " - ".join(parts[1:]).strip()}
        return {"artist": None, "title": clean_stem}

    @classmethod
    def read_metadata(cls, file_path: str) -> Dict[str, Any]:
        p = Path(file_path)
        stat = p.stat()
        file_size = stat.st_size
        date_modified = stat.st_mtime

        data = {
            "file_path": str(p.resolve()),
            "title": "",
            "artist": "",
            "album": "",
            "duration": 0.0,
            "sample_rate": None,
            "bits_per_sample": None,
            "channels": None,
            "file_size": file_size,
            "bitrate": None,
            "replay_gain": None,
            "date_modified": date_modified
        }

        try:
            audio = mutagen.File(file_path)
            if audio is not None and audio.info is not None:
                data["duration"] = getattr(audio.info, "length", 0.0) or 0.0
                data["sample_rate"] = getattr(audio.info, "sample_rate", None)
                data["bits_per_sample"] = getattr(audio.info, "bits_per_sample", None)
                data["channels"] = getattr(audio.info, "channels", None)
                
                bitrate = getattr(audio.info, "bitrate", None)
                if bitrate:
                    data["bitrate"] = bitrate / 1000.0 if bitrate > 5000 else float(bitrate)

                # Mutagen Tags Parsing
                if hasattr(audio, "tags") and audio.tags:
                    tags = audio.tags
                    if isinstance(tags, ID3):
                        data["title"] = str(tags.get("TIT2", [""])[0]) if "TIT2" in tags else ""
                        data["artist"] = str(tags.get("TPE1", [""])[0]) if "TPE1" in tags else ""
                        data["album"] = str(tags.get("TALB", [""])[0]) if "TALB" in tags else ""
                    elif isinstance(audio, (FLAC, OggVorbis)):
                        data["title"] = tags.get("title", [""])[0] if "title" in tags else ""
                        data["artist"] = tags.get("artist", [""])[0] if "artist" in tags else ""
                        data["album"] = tags.get("album", [""])[0] if "album" in tags else ""
                    elif isinstance(audio, MP4):
                        data["title"] = tags.get("\xa9nam", [""])[0] if "\xa9nam" in tags else ""
                        data["artist"] = tags.get("\xa9ART", [""])[0] if "\xa9ART" in tags else ""
                        data["album"] = tags.get("\xa9alb", [""])[0] if "\xa9alb" in tags else ""
        except Exception as e:
            logger.warning(f"Error reading metadata from {file_path}: {e}")

        # Fallback to filename parsing if title is empty
        if not data["title"]:
            fallback = cls.parse_filename_fallback(p.name)
            data["title"] = fallback["title"] or p.stem
            if not data["artist"] and fallback["artist"]:
                data["artist"] = fallback["artist"]

        return data
