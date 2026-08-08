import os
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import mutagen
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE
from core.backup import BackupManager
from core.verifier import AudioVerifier

class Embedder:
    def __init__(self, backup_manager: Optional[BackupManager] = None):
        self.backup_manager = backup_manager or BackupManager()

    def read_embedded_lyrics(self, filepath: str) -> str:
        """Reads embedded lyrics from the audio file. Returns empty string if none found."""
        ext = Path(filepath).suffix.lower()
        try:
            if ext == '.flac':
                audio = FLAC(filepath)
                val = audio.get('lyrics')
                if val:
                    return val[0]
                # Try uppercase just in case
                val = audio.get('LYRICS')
                if val:
                    return val[0]
            elif ext == '.mp3':
                audio = MP3(filepath)
                if audio.tags:
                    for key in audio.tags.keys():
                        if key.startswith('USLT'):
                            return audio.tags[key].text
            elif ext == '.m4a':
                audio = MP4(filepath)
                val = audio.get('\xa9lyr')
                if val:
                    return val[0]
            elif ext == '.ogg':
                audio = OggVorbis(filepath)
                val = audio.get('lyrics')
                if val:
                    return val[0]
                val = audio.get('LYRICS')
                if val:
                    return val[0]
            elif ext == '.wav':
                audio = WAVE(filepath)
                if audio.tags:
                    for key in audio.tags.keys():
                        if key.startswith('USLT'):
                            return audio.tags[key].text
        except Exception:
            pass
        return ""

    def embed_lyrics(self, filepath: str, lyrics_text: str, keep_backup: bool = True, legit_info: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Embeds lyrics into the audio file. Creates a backup beforehand.
        Verifies the write by reading back the tags. Rollback on failure.
        Returns (success_bool, message_str).
        """
        # Create backup first
        backup_path = self.backup_manager.create_backup(filepath)
        if not backup_path:
            return False, "Failed to create file backup."

        ext = Path(filepath).suffix.lower()
        success = False
        error_msg = ""

        try:
            if ext == '.flac':
                audio = FLAC(filepath)
                # Set both standard uppercase Vorbis comment keys for lyrics
                audio['LYRICS'] = lyrics_text
                audio['UNSYNCEDLYRICS'] = lyrics_text
                audio.save()
                success = True
            elif ext == '.mp3':
                audio = MP3(filepath)
                if audio.tags is not None:
                    uslt_keys = [k for k in audio.tags.keys() if k.startswith('USLT')]
                    for k in uslt_keys:
                        audio.tags.pop(k)
                else:
                    try:
                        audio.add_tags()
                    except Exception:
                        audio.tags = ID3()
                audio.tags.add(USLT(encoding=3, lang='eng', desc='', text=lyrics_text))
                audio.save()
                success = True
            elif ext == '.m4a':
                audio = MP4(filepath)
                audio['\xa9lyr'] = [lyrics_text]
                audio.save()
                success = True
            elif ext == '.ogg':
                audio = OggVorbis(filepath)
                audio['LYRICS'] = lyrics_text
                audio['UNSYNCEDLYRICS'] = lyrics_text
                audio.save()
                success = True
            elif ext == '.wav':
                audio = WAVE(filepath)
                if audio.tags is not None:
                    uslt_keys = [k for k in audio.tags.keys() if k.startswith('USLT')]
                    for k in uslt_keys:
                        audio.tags.pop(k)
                else:
                    try:
                        audio.add_tags()
                    except Exception:
                        audio.tags = ID3()
                audio.tags.add(USLT(encoding=3, lang='eng', desc='', text=lyrics_text))
                audio.save()
                success = True
            else:
                error_msg = f"Unsupported audio format: {ext}"
        except Exception as e:
            error_msg = str(e)

        if success:
            # Write legitimacy tags if available
            if legit_info and legit_info.get("actual_sample_rate"):
                AudioVerifier.write_legitimacy_tags(filepath, legit_info)

            # Verification step: read back lyrics and compare
            read_back = self.read_embedded_lyrics(filepath)
            if read_back.replace('\r\n', '\n').strip() == lyrics_text.replace('\r\n', '\n').strip():
                if not keep_backup:
                    self.backup_manager.remove_backup(backup_path)
                return True, "Embedded and verified successfully."
            else:
                error_msg = "Verification failed (read back text mismatch)."

        # Rollback on failure
        self.backup_manager.restore_backup(filepath, backup_path)
        if not keep_backup:
            self.backup_manager.remove_backup(backup_path)
        return False, f"Embedding failed: {error_msg}. Restored from backup."
