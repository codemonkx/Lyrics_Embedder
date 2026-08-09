import os
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import scipy.io.wavfile as wavfile
import numpy as np

from app.core.logging import logger

class AudioDecoder:
    @staticmethod
    def is_ffmpeg_available() -> bool:
        """Returns True if ffmpeg executable is available in PATH."""
        return shutil.which("ffmpeg") is not None

    @classmethod
    def decode_to_pcm(cls, file_path: str, start_time: int = 30, duration: int = 10) -> Tuple[Optional[int], Optional[np.ndarray], str]:
        """
        Decodes a segment of an audio file to PCM WAV using FFmpeg.
        Returns: (sample_rate, pcm_data_array, status_message)
        """
        if not os.path.exists(file_path):
            return None, None, f"File does not exist: {file_path}"

        if not cls.is_ffmpeg_available():
            logger.warning("FFmpeg binary is not found in system PATH. Audio spectral decoding unavailable.")
            return None, None, "FFmpeg unavailable on host system."

        temp_wav = tempfile.mktemp(suffix=".wav")
        try:
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(start_time),
                '-t', str(duration),
                '-i', file_path,
                '-ac', '1',
                temp_wav
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            sample_rate, data = wavfile.read(temp_wav)
            if len(data) == 0:
                # Fallback to start_time = 0 if sample at 30s failed
                cmd[3] = '0'
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                sample_rate, data = wavfile.read(temp_wav)

            if len(data) > 0:
                return sample_rate, data, "OK"
            return None, None, "Failed to extract valid PCM audio samples."

        except Exception as e:
            logger.error(f"FFmpeg decoding failed for {file_path}: {e}")
            return None, None, f"Decoding error: {e}"

        finally:
            if os.path.exists(temp_wav):
                try:
                    os.unlink(temp_wav)
                except Exception:
                    pass
