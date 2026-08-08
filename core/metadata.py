import os
from pathlib import Path
from typing import Dict, Any, Optional
import mutagen
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4
from mutagen.easymp4 import EasyMP4
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE

class MetadataReader:
    @staticmethod
    def parse_filename_fallback(filename: str) -> Dict[str, Optional[str]]:
        """Parses artist and title from filename if they are separated by space-surrounded hyphens."""
        name_without_ext = Path(filename).stem
        parts = []
        if " - " in name_without_ext:
            parts = name_without_ext.split(" - ", 1)
        elif " -" in name_without_ext:
            parts = name_without_ext.split(" -", 1)
        elif "- " in name_without_ext:
            parts = name_without_ext.split("- ", 1)
        
        if len(parts) == 2:
            return {
                "artist": parts[0].strip(),
                "title": parts[1].strip()
            }
        return {
            "artist": None,
            "title": name_without_ext.strip()
        }

    @staticmethod
    def read_metadata(filepath: str) -> Dict[str, Any]:
        """Reads metadata from the audio file. Falls back to filename parsing if tags are missing."""
        path = Path(filepath)
        ext = path.suffix.lower()
        
        title = None
        artist = None
        album = None
        track = None
        duration = 0.0
        
        sample_rate = None
        bits_per_sample = None
        channels = None
        file_size = 0.0
        bitrate = None
        replay_gain = None
        date_modified = None

        try:
            file_size = os.path.getsize(filepath)
            mtime = os.path.getmtime(filepath)
            from datetime import datetime
            date_modified = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
        except Exception:
            pass

        try:
            if ext == '.flac':
                audio = FLAC(filepath)
                duration = audio.info.length
                sample_rate = audio.info.sample_rate
                bits_per_sample = audio.info.bits_per_sample
                channels = audio.info.channels
                if duration > 0:
                    bitrate = int((file_size * 8) / (duration * 1000))
                replay_gain = audio.get('replaygain_track_gain', [None])[0] or audio.get('REPLAYGAIN_TRACK_GAIN', [None])[0]
                
                title = audio.get('title', [None])[0]
                artist = audio.get('artist', [None])[0]
                album = audio.get('album', [None])[0]
                track = audio.get('tracknumber', [None])[0]

            elif ext == '.mp3':
                mp3 = MP3(filepath)
                duration = mp3.info.length
                sample_rate = mp3.info.sample_rate
                channels = mp3.info.channels
                bitrate = int(mp3.info.bitrate / 1000) if mp3.info.bitrate else None
                for tag in mp3.keys():
                    if tag.startswith("TXXX:replaygain_track_gain"):
                        replay_gain = mp3[tag].text[0]
                try:
                    tags = EasyID3(filepath)
                    title = tags.get('title', [None])[0]
                    artist = tags.get('artist', [None])[0]
                    album = tags.get('album', [None])[0]
                    track = tags.get('tracknumber', [None])[0]
                except Exception:
                    pass

            elif ext == '.m4a':
                mp4 = MP4(filepath)
                duration = mp4.info.length
                sample_rate = mp4.info.sample_rate
                channels = mp4.info.channels
                bitrate = int(mp4.info.bitrate / 1000) if mp4.info.bitrate else None
                if mp4.get('----:com.apple.iTunes:replaygain_track_gain'):
                    try:
                        replay_gain = mp4['----:com.apple.iTunes:replaygain_track_gain'][0].decode('utf-8', errors='ignore')
                    except Exception:
                        pass
                try:
                    tags = EasyMP4(filepath)
                    title = tags.get('title', [None])[0]
                    artist = tags.get('artist', [None])[0]
                    album = tags.get('album', [None])[0]
                    track = tags.get('tracknumber', [None])[0]
                except Exception:
                    pass

            elif ext == '.ogg':
                ogg = OggVorbis(filepath)
                duration = ogg.info.length
                sample_rate = ogg.info.sample_rate
                channels = ogg.info.channels
                bitrate = int(ogg.info.bitrate / 1000) if ogg.info.bitrate else None
                replay_gain = ogg.get('replaygain_track_gain', [None])[0] or ogg.get('REPLAYGAIN_TRACK_GAIN', [None])[0]
                title = ogg.get('title', [None])[0]
                artist = ogg.get('artist', [None])[0]
                album = ogg.get('album', [None])[0]
                track = ogg.get('tracknumber', [None])[0]

            elif ext == '.wav':
                wav = WAVE(filepath)
                duration = wav.info.length
                sample_rate = wav.info.sample_rate
                bits_per_sample = wav.info.bits_per_sample
                channels = wav.info.channels
                if duration > 0:
                    bitrate = int((file_size * 8) / (duration * 1000))
                if wav.tags:
                    title = wav.tags.get('TIT2').text[0] if wav.tags.get('TIT2') else None
                    artist = wav.tags.get('TPE1').text[0] if wav.tags.get('TPE1') else None
                    album = wav.tags.get('TALB').text[0] if wav.tags.get('TALB') else None
                    track = wav.tags.get('TRCK').text[0] if wav.tags.get('TRCK') else None

        except Exception:
            pass

        # Fallback to filename parsing if Title or Artist tags are missing
        fallback = MetadataReader.parse_filename_fallback(path.name)
        if not title:
            title = fallback["title"]
        if not artist:
            artist = fallback["artist"]

        return {
            "file_path": str(path.resolve()),
            "title": title or "",
            "artist": artist or "",
            "album": album or "",
            "track": track or "",
            "duration": float(duration),
            "sample_rate": sample_rate,
            "bits_per_sample": bits_per_sample,
            "channels": channels,
            "file_size": file_size,
            "bitrate": bitrate,
            "replay_gain": replay_gain,
            "date_modified": date_modified
        }
