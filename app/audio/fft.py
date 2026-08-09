from typing import Tuple, Dict, Any
import numpy as np

class FFTAnalyzer:
    @staticmethod
    def calculate_spectrum(sample_rate: int, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float, str]:
        """
        Calculates FFT magnitude spectrum and estimates cutoff frequency.
        Returns: (frequencies_kHz, magnitudes_dB, cutoff_frequency_Hz, detection_method)
        """
        n = len(data)
        if n == 0 or sample_rate <= 0:
            return np.array([]), np.array([]), 0.0, "Empty Data"

        fft_result = np.fft.rfft(data)
        frequencies = np.fft.rfftfreq(n, d=1.0 / sample_rate)
        magnitudes = np.abs(fft_result)
        magnitudes = np.clip(magnitudes, 1e-10, None)
        magnitudes_db = 20 * np.log10(magnitudes)
        magnitudes_db -= np.max(magnitudes_db)  # Normalize peak to 0 dB

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

        threshold_db = -55.0
        if brickwall_idx != -1:
            cutoff = float(bands[brickwall_idx] + band_size)
            method = f"Brickwall Drop (-{max_drop:.1f}dB)"
        else:
            active_freqs = frequencies[magnitudes_db > threshold_db]
            cutoff = float(np.max(active_freqs)) if len(active_freqs) > 0 else 0.0
            method = "Threshold Limit (-55dB)"

        return frequencies / 1000.0, magnitudes_db, cutoff, method
