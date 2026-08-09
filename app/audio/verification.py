from pathlib import Path
from typing import Dict, Any
from app.audio.decoder import AudioDecoder
from app.audio.fft import FFTAnalyzer
from app.models.analysis import AudioAnalysis
from app.metadata.reader import MetadataReader
from app.core.logging import logger

class AudioVerificationEngine:
    @classmethod
    def verify_file(cls, file_path: str) -> AudioAnalysis:
        p = Path(file_path)
        ext = p.suffix.lower()
        
        meta = MetadataReader.read_metadata(file_path)
        sample_rate = meta.get("sample_rate") or 44100

        # Decode PCM segment via FFmpeg
        sr, pcm_data, msg = AudioDecoder.decode_to_pcm(file_path)
        if sr is None or pcm_data is None:
            return AudioAnalysis(
                file_path=file_path,
                actual_sample_rate=sample_rate,
                spectral_cutoff=0.0,
                legit=-1,
                observation=f"Decoder Status: {msg}",
                interpretation="Spectral verification unavailable (FFmpeg missing or file inaccessible).",
                confidence=0.0,
                reason=msg
            )

        freqs_khz, mags_db, cutoff_hz, method = FFTAnalyzer.calculate_spectrum(sr, pcm_data)

        # Expected Nyquist cutoff for genuine audio
        expected_nyquist = sr / 2.0
        
        # Lossless threshold evaluation
        if ext in [".flac", ".wav", ".aiff", ".alac"]:
            if sr >= 88200 and cutoff_hz < 24000:
                legit = 0
                observation = f"Sharp high-frequency attenuation at {cutoff_hz/1000:.1f} kHz on a {sr/1000:.1f} kHz stream."
                interpretation = "Spectral profile is consistent with a lossy-derived source or upscaled transcode."
                confidence = 88.0
                reason = f"Cutoff at {cutoff_hz/1000:.1f} kHz below expected high-res Nyquist bandwidth."
            elif sr == 44100 and cutoff_hz < 18500:
                legit = 0
                observation = f"Brickwall frequency drop observed at {cutoff_hz/1000:.1f} kHz."
                interpretation = "Spectral profile is consistent with MP3/AAC lossy-compressed origin."
                confidence = 92.0
                reason = f"Cutoff at {cutoff_hz/1000:.1f} kHz (Lossless 44.1kHz typically extends to 20-22kHz)."
            else:
                legit = 1
                observation = f"Full frequency spectrum extending to {cutoff_hz/1000:.1f} kHz."
                interpretation = "Spectral profile consistent with genuine lossless source."
                confidence = 95.0
                reason = f"Full band response verified up to {cutoff_hz/1000:.1f} Hz."
        else:
            legit = 1
            observation = f"Lossy audio format ({ext.upper()}) cutoff at {cutoff_hz/1000:.1f} kHz."
            interpretation = f"Standard lossy container compression ({ext.upper()})."
            confidence = 100.0
            reason = f"Codec {ext.upper()} inherently applies lossy compression."

        return AudioAnalysis(
            file_path=file_path,
            actual_sample_rate=sr,
            spectral_cutoff=cutoff_hz,
            legit=legit,
            observation=observation,
            interpretation=interpretation,
            confidence=confidence,
            reason=reason
        )
