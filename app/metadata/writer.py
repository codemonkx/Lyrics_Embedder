import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import mutagen
from mutagen.id3 import ID3, USLT, TXXX
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis

from app.core.logging import logger

class MetadataWriter:
    @staticmethod
    def embed_lyrics(file_path: str, lyrics_text: str, legit_info: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        ext = Path(file_path).suffix.lower()
        try:
            audio = mutagen.File(file_path)
            if audio is None:
                return False, f"Unsupported audio format: {ext}"

            # MP3 Tagging
            if ext == ".mp3":
                if audio.tags is None:
                    audio.add_tags()
                audio.tags.add(USLT(encoding=3, lang="eng", desc="", text=lyrics_text))
                if legit_info:
                    if legit_info.get("spectral_cutoff"):
                        audio.tags.add(TXXX(encoding=3, desc="LYRICFORGE_CUTOFF_HZ", text=str(legit_info["spectral_cutoff"])))
                    if legit_info.get("legit") is not None:
                        audio.tags.add(TXXX(encoding=3, desc="LYRICFORGE_LEGIT", text=str(legit_info["legit"])))
                audio.save()
                return True, "Successfully embedded lyrics into MP3 ID3 USLT tag."

            # FLAC / OGG Tagging
            elif ext in [".flac", ".ogg"]:
                audio["lyrics"] = lyrics_text
                audio["unsyncedlyrics"] = lyrics_text
                if legit_info:
                    if legit_info.get("spectral_cutoff"):
                        audio["lyricforge_cutoff_hz"] = str(legit_info["spectral_cutoff"])
                    if legit_info.get("legit") is not None:
                        audio["lyricforge_legit"] = str(legit_info["legit"])
                audio.save()
                return True, f"Successfully embedded lyrics into {ext.upper()} Vorbis Comments."

            # M4A Tagging
            elif ext in [".m4a", ".mp4"]:
                audio["\xa9lyr"] = lyrics_text
                audio.save()
                return True, "Successfully embedded lyrics into M4A QuickTime atom."

            return False, f"Unsupported extension for lyrics embedding: {ext}"

        except Exception as e:
            logger.error(f"Failed to embed lyrics in {file_path}: {e}")
            return False, str(e)
