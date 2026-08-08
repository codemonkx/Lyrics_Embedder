import os
import subprocess
import tempfile
import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path
from typing import Dict, Any, Tuple
import mutagen
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE

class AudioVerifier:
    @staticmethod
    def verify_file(filepath: str) -> Dict[str, Any]:
        """
        Runs spectral analysis on an audio file.
        Decodes three 3-second segments (at 25%, 50%, and 75% of track duration) to mono WAV,
        computes FFT on each valid segment, checks for RMS power, finds the cutoff frequency,
        and takes the maximum cutoff to determine if it is a fake upscale or transcode.
        """
        if not os.path.exists(filepath):
            return {
                "actual_sample_rate": 0,
                "spectral_cutoff": 0.0,
                "legit": False,
                "reason": "File not found on disk."
            }

        # Step 1: Detect technical metadata (duration and sample rate)
        ext = Path(filepath).suffix.lower()
        duration = 0.0
        sample_rate = 0
        try:
            if ext == '.flac':
                audio = FLAC(filepath)
                duration = audio.info.length
                sample_rate = audio.info.sample_rate
            elif ext == '.mp3':
                audio = MP3(filepath)
                duration = audio.info.length
                sample_rate = audio.info.sample_rate
            elif ext == '.m4a':
                audio = MP4(filepath)
                duration = audio.info.length
                sample_rate = audio.info.sample_rate
            elif ext == '.ogg':
                audio = OggVorbis(filepath)
                duration = audio.info.length
                sample_rate = audio.info.sample_rate
            elif ext == '.wav':
                audio = WAVE(filepath)
                duration = audio.info.length
                sample_rate = audio.info.sample_rate
        except Exception:
            pass

        # If headers couldn't be parsed or duration is invalid, default
        if duration <= 0:
            duration = 180.0
        
        # Try to read WAV files directly to avoid dependency on ffmpeg for WAV files
        wav_data = None
        if ext == '.wav':
            try:
                s_rate, raw_data = wavfile.read(filepath)
                if len(raw_data) > 0:
                    sample_rate = s_rate
                    duration = len(raw_data) / sample_rate
                    # Convert to float32 normalized mono
                    if len(raw_data.shape) > 1:
                        # Stereo or multi-channel: average across channels to make it mono
                        raw_data = np.mean(raw_data, axis=1)
                    
                    if raw_data.dtype == np.int16:
                        wav_data = raw_data.astype(np.float32) / 32768.0
                    elif raw_data.dtype == np.int32:
                        wav_data = raw_data.astype(np.float32) / 2147483648.0
                    elif raw_data.dtype == np.uint8:
                        wav_data = (raw_data.astype(np.float32) - 128.0) / 128.0
                    elif np.issubdtype(raw_data.dtype, np.floating):
                        wav_data = raw_data.astype(np.float32)
                    else:
                        wav_data = raw_data.astype(np.float32)
            except Exception:
                pass

        # Decide seek timestamps to sample
        if duration > 15.0:
            seeks = [duration * 0.25, duration * 0.50, duration * 0.75]
        else:
            seeks = [0.0]

        valid_slices = []

        for seek in seeks:
            if wav_data is not None:
                try:
                    start_idx = int(seek * sample_rate)
                    num_samples = int(3 * sample_rate)
                    data_norm = wav_data[start_idx : start_idx + num_samples]
                    if len(data_norm) == 0:
                        continue
                    
                    # Compute RMS energy
                    rms = np.sqrt(np.mean(data_norm ** 2))
                    rms_db = 20 * np.log10(max(rms, 1e-10))
                    
                    # Skip silent/very quiet slices (threshold: -50 dBFS)
                    if rms_db < -50.0:
                        continue
                        
                    n = len(data_norm)
                    fft_result = np.fft.rfft(data_norm)
                    frequencies = np.fft.rfftfreq(n, d=1.0/sample_rate)
                    
                    # Convert to decibels relative to peak magnitude
                    magnitudes = np.abs(fft_result)
                    magnitudes = np.clip(magnitudes, 1e-10, None)
                    magnitudes_db = 20 * np.log10(magnitudes)
                    magnitudes_db -= np.max(magnitudes_db)
                    
                    # Group frequencies into 250 Hz bands to calculate slopes (differences)
                    band_size = 250
                    max_freq = sample_rate / 2.0
                    bands = np.arange(1000, max_freq, band_size)
                    
                    band_means = []
                    for b in bands:
                        mask = (frequencies >= b) & (frequencies < b + band_size)
                        if np.any(mask):
                            band_means.append(np.mean(magnitudes_db[mask]))
                        else:
                            band_means.append(-100.0)
                    band_means = np.array(band_means)
                    
                    # Find sliding differences (slopes)
                    diffs = band_means[1:] - band_means[:-1]
                    
                    # Brickwall detection: look for a drop of more than 12dB between bands above 10kHz
                    brickwall_idx = -1
                    max_drop = 0.0
                    for i in range(len(diffs)):
                        freq = bands[i]
                        if freq >= 10000:
                            if diffs[i] < -12.0:
                                if abs(diffs[i]) > max_drop:
                                    max_drop = abs(diffs[i])
                                    brickwall_idx = i
                    
                    if brickwall_idx != -1:
                        cutoff = float(bands[brickwall_idx] + band_size)
                        has_brickwall = True
                        brickwall_drop = max_drop
                    else:
                        # Fallback to absolute threshold if no sharp brickwall drop
                        threshold_db = -55.0
                        active_freqs = frequencies[magnitudes_db > threshold_db]
                        cutoff = float(np.max(active_freqs)) if len(active_freqs) > 0 else 0.0
                        has_brickwall = False
                        brickwall_drop = 0.0
                    
                    valid_slices.append({
                        "cutoff": cutoff,
                        "has_brickwall": has_brickwall,
                        "brickwall_drop": brickwall_drop,
                        "rms_db": rms_db
                    })
                except Exception:
                    pass
            else:
                temp_wav = tempfile.mktemp(suffix=".wav")
                try:
                    cmd = [
                        'ffmpeg', '-y',
                        '-ss', f'{seek:.2f}',
                        '-t', '3',
                        '-i', filepath,
                        '-ac', '1',  # Mono
                        temp_wav
                    ]
                    
                    # Execute FFmpeg silently
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    
                    if not os.path.exists(temp_wav):
                        continue
                        
                    s_rate, data = wavfile.read(temp_wav)
                    if len(data) == 0:
                        continue
                    
                    if sample_rate == 0:
                        sample_rate = s_rate
                    
                    # Normalize audio data
                    if data.dtype == np.int16:
                        data_norm = data.astype(np.float32) / 32768.0
                    elif data.dtype == np.int32:
                        data_norm = data.astype(np.float32) / 2147483648.0
                    elif data.dtype == np.uint8:
                        data_norm = (data.astype(np.float32) - 128.0) / 128.0
                    elif np.issubdtype(data.dtype, np.floating):
                        data_norm = data.astype(np.float32)
                    else:
                        data_norm = data.astype(np.float32)
                    
                    # Compute RMS energy
                    rms = np.sqrt(np.mean(data_norm ** 2))
                    rms_db = 20 * np.log10(max(rms, 1e-10))
                    
                    # Skip silent/very quiet slices (threshold: -50 dBFS)
                    if rms_db < -50.0:
                        continue
                        
                    n = len(data_norm)
                    fft_result = np.fft.rfft(data_norm)
                    frequencies = np.fft.rfftfreq(n, d=1.0/sample_rate)
                    
                    # Convert to decibels relative to peak magnitude
                    magnitudes = np.abs(fft_result)
                    magnitudes = np.clip(magnitudes, 1e-10, None)
                    magnitudes_db = 20 * np.log10(magnitudes)
                    magnitudes_db -= np.max(magnitudes_db)
                    
                    # Group frequencies into 250 Hz bands to calculate slopes (differences)
                    band_size = 250
                    max_freq = sample_rate / 2.0
                    bands = np.arange(1000, max_freq, band_size)
                    
                    band_means = []
                    for b in bands:
                        mask = (frequencies >= b) & (frequencies < b + band_size)
                        if np.any(mask):
                            band_means.append(np.mean(magnitudes_db[mask]))
                        else:
                            band_means.append(-100.0)
                    band_means = np.array(band_means)
                    
                    # Find sliding differences (slopes)
                    diffs = band_means[1:] - band_means[:-1]
                    
                    # Brickwall detection: look for a drop of more than 12dB between bands above 10kHz
                    brickwall_idx = -1
                    max_drop = 0.0
                    for i in range(len(diffs)):
                        freq = bands[i]
                        if freq >= 10000:
                            if diffs[i] < -12.0:
                                if abs(diffs[i]) > max_drop:
                                    max_drop = abs(diffs[i])
                                    brickwall_idx = i
                    
                    if brickwall_idx != -1:
                        cutoff = float(bands[brickwall_idx] + band_size)
                        has_brickwall = True
                        brickwall_drop = max_drop
                    else:
                        # Fallback to absolute threshold if no sharp brickwall drop
                        threshold_db = -55.0
                        active_freqs = frequencies[magnitudes_db > threshold_db]
                        cutoff = float(np.max(active_freqs)) if len(active_freqs) > 0 else 0.0
                        has_brickwall = False
                        brickwall_drop = 0.0
                    
                    valid_slices.append({
                        "cutoff": cutoff,
                        "has_brickwall": has_brickwall,
                        "brickwall_drop": brickwall_drop,
                        "rms_db": rms_db
                    })
                except Exception:
                    pass
                finally:
                    if os.path.exists(temp_wav):
                        try:
                            os.unlink(temp_wav)
                        except Exception:
                            pass

        # Fallback if all seek slices were below RMS threshold
        if not valid_slices:
            if wav_data is not None:
                try:
                    num_samples = int(10 * sample_rate)
                    data_norm = wav_data[0 : num_samples]
                    if len(data_norm) > 0:
                        n = len(data_norm)
                        fft_result = np.fft.rfft(data_norm)
                        frequencies = np.fft.rfftfreq(n, d=1.0/sample_rate)
                        
                        magnitudes = np.abs(fft_result)
                        magnitudes = np.clip(magnitudes, 1e-10, None)
                        magnitudes_db = 20 * np.log10(magnitudes)
                        magnitudes_db -= np.max(magnitudes_db)
                        
                        band_size = 250
                        max_freq = sample_rate / 2.0
                        bands = np.arange(1000, max_freq, band_size)
                        
                        band_means = []
                        for b in bands:
                            mask = (frequencies >= b) & (frequencies < b + band_size)
                            if np.any(mask):
                                band_means.append(np.mean(magnitudes_db[mask]))
                            else:
                                band_means.append(-100.0)
                        band_means = np.array(band_means)
                        diffs = band_means[1:] - band_means[:-1]
                        
                        brickwall_idx = -1
                        max_drop = 0.0
                        for i in range(len(diffs)):
                            freq = bands[i]
                            if freq >= 10000:
                                if diffs[i] < -12.0:
                                    if abs(diffs[i]) > max_drop:
                                        max_drop = abs(diffs[i])
                                        brickwall_idx = i
                                        
                        if brickwall_idx != -1:
                            cutoff = float(bands[brickwall_idx] + band_size)
                            has_brickwall = True
                            brickwall_drop = max_drop
                        else:
                            threshold_db = -55.0
                            active_freqs = frequencies[magnitudes_db > threshold_db]
                            cutoff = float(np.max(active_freqs)) if len(active_freqs) > 0 else 0.0
                            has_brickwall = False
                            brickwall_drop = 0.0
                            
                        valid_slices.append({
                            "cutoff": cutoff,
                            "has_brickwall": has_brickwall,
                            "brickwall_drop": brickwall_drop,
                            "rms_db": -99.0
                        })
                except Exception:
                    pass
            else:
                temp_wav = tempfile.mktemp(suffix=".wav")
                try:
                    cmd = [
                        'ffmpeg', '-y',
                        '-ss', '0',
                        '-t', '10',
                        '-i', filepath,
                        '-ac', '1',
                        temp_wav
                    ]
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    if os.path.exists(temp_wav):
                        s_rate, data = wavfile.read(temp_wav)
                        if len(data) > 0:
                            if sample_rate == 0:
                                sample_rate = s_rate
                            
                            if data.dtype == np.int16:
                                data_norm = data.astype(np.float32) / 32768.0
                            elif data.dtype == np.int32:
                                data_norm = data.astype(np.float32) / 2147483648.0
                            elif data.dtype == np.uint8:
                                data_norm = (data.astype(np.float32) - 128.0) / 128.0
                            else:
                                data_norm = data.astype(np.float32)
                                
                            n = len(data_norm)
                            fft_result = np.fft.rfft(data_norm)
                            frequencies = np.fft.rfftfreq(n, d=1.0/sample_rate)
                            
                            magnitudes = np.abs(fft_result)
                            magnitudes = np.clip(magnitudes, 1e-10, None)
                            magnitudes_db = 20 * np.log10(magnitudes)
                            magnitudes_db -= np.max(magnitudes_db)
                            
                            band_size = 250
                            max_freq = sample_rate / 2.0
                            bands = np.arange(1000, max_freq, band_size)
                            
                            band_means = []
                            for b in bands:
                                mask = (frequencies >= b) & (frequencies < b + band_size)
                                if np.any(mask):
                                    band_means.append(np.mean(magnitudes_db[mask]))
                                else:
                                    band_means.append(-100.0)
                            band_means = np.array(band_means)
                            diffs = band_means[1:] - band_means[:-1]
                            
                            brickwall_idx = -1
                            max_drop = 0.0
                            for i in range(len(diffs)):
                                freq = bands[i]
                                if freq >= 10000:
                                    if diffs[i] < -12.0:
                                        if abs(diffs[i]) > max_drop:
                                            max_drop = abs(diffs[i])
                                            brickwall_idx = i
                                            
                            if brickwall_idx != -1:
                                cutoff = float(bands[brickwall_idx] + band_size)
                                has_brickwall = True
                                brickwall_drop = max_drop
                            else:
                                threshold_db = -55.0
                                active_freqs = frequencies[magnitudes_db > threshold_db]
                                cutoff = float(np.max(active_freqs)) if len(active_freqs) > 0 else 0.0
                                has_brickwall = False
                                brickwall_drop = 0.0
                                
                            valid_slices.append({
                                "cutoff": cutoff,
                                "has_brickwall": has_brickwall,
                                "brickwall_drop": brickwall_drop,
                                "rms_db": -99.0
                            })
                except Exception:
                    pass
                finally:
                    if os.path.exists(temp_wav):
                        try:
                            os.unlink(temp_wav)
                        except Exception:
                            pass

        if not valid_slices:
            return AudioVerifier._read_technical_headers_only(filepath, "No audio content extracted.")

        # Select the slice with the highest cutoff frequency
        best_slice = max(valid_slices, key=lambda x: x["cutoff"])
        cutoff = best_slice["cutoff"]
        has_brickwall = best_slice["has_brickwall"]
        brickwall_drop = best_slice["brickwall_drop"]
        
        if sample_rate == 0:
            sample_rate = 44100

        # Evaluate integrity based on cutoff frequency
        legit = True
        method_desc = f"Brickwall drop: {brickwall_drop:.1f} dB drop at {cutoff/1000:.1f} kHz" if has_brickwall else f"Absolute threshold limit at {cutoff/1000:.1f} kHz"
        reason = f"Lossless spectrum matches technical format ({method_desc})."
        
        # 1. High-Res Upscale check
        if sample_rate >= 88200:
            if has_brickwall and cutoff <= 25000.0:
                legit = False
                reason = f"Fake Upscale: Stream claims {sample_rate/1000:.1f}kHz sample rate, but audio spectrum cuts off at {cutoff/1000:.1f}kHz ({method_desc})."
            elif not has_brickwall and cutoff <= 22100.0:
                legit = False
                reason = f"Fake Upscale: Stream claims {sample_rate/1000:.1f}kHz sample rate, but audio spectrum cuts off at {cutoff/1000:.1f}kHz ({method_desc})."
        # 2. CD-Quality Lossy Transcode check
        elif sample_rate >= 44100:
            if has_brickwall:
                max_cutoff_for_fake = 20700.0 if sample_rate < 47000 else 22500.0
                if cutoff <= max_cutoff_for_fake:
                    legit = False
                    reason = f"Lossy Transcode: Stream is CD quality ({sample_rate/1000:.1f}kHz), but frequency cuts off at {cutoff/1000:.1f}kHz ({method_desc})."
            else:
                if cutoff <= 16000.0:
                    legit = False
                    reason = f"Lossy Transcode: Stream is CD quality ({sample_rate/1000:.1f}kHz), but frequency cuts off at {cutoff/1000:.1f}kHz ({method_desc})."
        else:
            reason = f"Low sample rate format ({sample_rate/1000:.1f}kHz), skipping upscale/transcode analysis."
            
        return {
            "actual_sample_rate": int(sample_rate),
            "spectral_cutoff": cutoff,
            "legit": legit,
            "reason": reason
        }

    @staticmethod
    def _read_technical_headers_only(filepath: str, error_context: str) -> Dict[str, Any]:
        """Fallback method that reads stream metadata headers directly using mutagen."""
        ext = Path(filepath).suffix.lower()
        try:
            if ext == '.flac':
                audio = FLAC(filepath)
                return {
                    "actual_sample_rate": int(audio.info.sample_rate),
                    "spectral_cutoff": 0.0,
                    "legit": True,
                    "reason": f"Headers OK. (Spectral check skipped: {error_context})"
                }
            elif ext == '.mp3':
                audio = MP3(filepath)
                return {
                    "actual_sample_rate": int(audio.info.sample_rate),
                    "spectral_cutoff": 0.0,
                    "legit": True,
                    "reason": f"Headers OK. (Spectral check skipped: {error_context})"
                }
            elif ext == '.m4a':
                audio = MP4(filepath)
                return {
                    "actual_sample_rate": int(audio.info.sample_rate),
                    "spectral_cutoff": 0.0,
                    "legit": True,
                    "reason": f"Headers OK. (Spectral check skipped: {error_context})"
                }
            elif ext == '.wav':
                audio = WAVE(filepath)
                return {
                    "actual_sample_rate": int(audio.info.sample_rate),
                    "spectral_cutoff": 0.0,
                    "legit": True,
                    "reason": f"Headers OK. (Spectral check skipped: {error_context})"
                }
        except Exception as e:
            pass
            
        return {
            "actual_sample_rate": 0,
            "spectral_cutoff": 0.0,
            "legit": False,
            "reason": f"Analysis failed: {error_context}"
        }

    @staticmethod
    def write_legitimacy_tags(filepath: str, result: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Embeds the spectral analysis findings (AUDIO_LEGIT, SPECTRAL_LIMIT, etc.)
        directly inside the file's metadata tags.
        """
        if not result.get("actual_sample_rate"):
            return False, "No analysis data to write."

        ext = Path(filepath).suffix.lower()
        try:
            if ext == '.flac':
                audio = FLAC(filepath)
                audio['AUDIO_LEGIT'] = 'True' if result['legit'] else 'False'
                audio['SPECTRAL_LIMIT'] = f"{result['spectral_cutoff']/1000:.1f} kHz"
                audio['AUDIO_INTEGRITY_DETAILS'] = result['reason']
                audio.save()
                return True, "Integrity tags embedded successfully."
            elif ext == '.ogg':
                audio = OggVorbis(filepath)
                audio['AUDIO_LEGIT'] = 'True' if result['legit'] else 'False'
                audio['SPECTRAL_LIMIT'] = f"{result['spectral_cutoff']/1000:.1f} kHz"
                audio['AUDIO_INTEGRITY_DETAILS'] = result['reason']
                audio.save()
                return True, "Integrity tags embedded successfully."
            elif ext == '.m4a':
                # MP4/AAC doesn't officially support custom comments cleanly, but we can write a comment atom
                audio = MP4(filepath)
                summary = f"AUDIO_LEGIT={'True' if result['legit'] else 'False'}; LIMIT={result['spectral_cutoff']/1000:.1f}kHz; {result['reason']}"
                audio['\xa9cmt'] = [summary]
                audio.save()
                return True, "Integrity comments embedded successfully."
            elif ext == '.wav':
                audio = WAVE(filepath)
                if audio.tags is None:
                    try:
                        audio.add_tags()
                    except Exception:
                        from mutagen.id3 import ID3
                        audio.tags = ID3()
                from mutagen.id3 import TXXX
                audio.tags.add(TXXX(encoding=3, desc='AUDIO_LEGIT', text=['True' if result['legit'] else 'False']))
                audio.tags.add(TXXX(encoding=3, desc='SPECTRAL_LIMIT', text=[f"{result['spectral_cutoff']/1000:.1f} kHz"]))
                audio.tags.add(TXXX(encoding=3, desc='AUDIO_INTEGRITY_DETAILS', text=[result['reason']]))
                audio.save()
                return True, "Integrity TXXX frames embedded successfully."
            elif ext == '.mp3':
                from mutagen.id3 import ID3, TXXX
                try:
                    tags = ID3(filepath)
                except Exception:
                    tags = ID3()
                
                tags.add(TXXX(encoding=3, desc='AUDIO_LEGIT', text=['True' if result['legit'] else 'False']))
                tags.add(TXXX(encoding=3, desc='SPECTRAL_LIMIT', text=[f"{result['spectral_cutoff']/1000:.1f} kHz"]))
                tags.add(TXXX(encoding=3, desc='AUDIO_INTEGRITY_DETAILS', text=[result['reason']]))
                tags.save(filepath)
                return True, "Integrity TXXX frames embedded successfully."
                
            return False, f"Unsupported format for integrity tags: {ext}"
        except Exception as e:
            return False, f"Tag write error: {str(e)}"
