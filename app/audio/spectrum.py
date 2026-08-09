import io
import urllib.parse
import matplotlib
matplotlib.use("Agg")  # Non-GUI backend for fast in-memory rendering
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtCore import QSize

from app.audio.decoder import AudioDecoder
from app.audio.fft import FFTAnalyzer
from app.core.logging import logger

class SpectrumImageProvider(QQuickImageProvider):
    """
    QML Image Provider ("image://spectrum/file_path") bridge rendering
    PyQtGraph / FFT spectrum plots into QML Image widgets seamlessly.
    """
    _cache = {}

    def __init__(self):
        super().__init__(QQuickImageProvider.Pixmap)

    def requestPixmap(self, id: str, size: QSize, requestedSize: QSize) -> QPixmap:
        # Decode URL-encoded characters (e.g. %3A -> ':', %5C -> '\', %2F -> '/')
        raw_path = urllib.parse.unquote(id)
        file_path = str(Path(raw_path).resolve())
        
        # Check in-memory cache
        if file_path in self._cache:
            return self._cache[file_path]

        w = requestedSize.width() if requestedSize.width() > 0 else 600
        h = requestedSize.height() if requestedSize.height() > 0 else 300

        pixmap = self.generate_spectrum_pixmap(file_path, w, h)
        self._cache[file_path] = pixmap
        return pixmap

    @classmethod
    def generate_spectrum_pixmap(cls, file_path: str, width: int = 600, height: int = 300) -> QPixmap:
        sr, pcm_data, msg = AudioDecoder.decode_to_pcm(file_path)
        
        fig, ax = plt.subplots(figsize=(width / 100.0, height / 100.0), dpi=100)
        fig.patch.set_facecolor('#0B0C0E')
        ax.set_facecolor('#121417')

        if sr is not None and pcm_data is not None and len(pcm_data) > 0:
            freqs_khz, mags_db, cutoff_hz, method = FFTAnalyzer.calculate_spectrum(sr, pcm_data)
            
            ax.plot(freqs_khz, mags_db, color='#FF002B', alpha=0.85, linewidth=1.2)
            ax.axhline(y=-55.0, color='#62666D', linestyle='--', alpha=0.6, linewidth=1.0)
            ax.axvline(x=cutoff_hz / 1000.0, color='#34D399', linestyle='-.', linewidth=1.5)
            
            ax.set_title(f"Spectral Profile: Cutoff at {cutoff_hz/1000:.1f} kHz ({method})", fontsize=9, color='#F2F2F2', fontweight='bold')
            ax.set_xlabel("Frequency (kHz)", fontsize=8, color='#92969D')
            ax.set_ylabel("Magnitude (dB)", fontsize=8, color='#92969D')
            ax.set_xlim(0, sr / 2000.0)
            ax.set_ylim(-100, 5)
        else:
            ax.text(0.5, 0.5, f"Spectrum Unavailable\n({msg})", color='#92969D', ha='center', va='center', fontsize=9)
            ax.set_xlim(0, 22)
            ax.set_ylim(-100, 0)

        ax.spines['bottom'].set_color('#272A2F')
        ax.spines['top'].set_color('#272A2F')
        ax.spines['left'].set_color('#272A2F')
        ax.spines['right'].set_color('#272A2F')
        ax.tick_params(colors='#92969D', labelsize=8)
        ax.grid(True, color='#181B1F', linestyle=':', alpha=0.8)

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor='#0B0C0E', dpi=100)
        plt.close(fig)
        buf.seek(0)

        qimg = QImage.fromData(buf.getvalue())
        buf.close()
        return QPixmap.fromImage(qimg)
