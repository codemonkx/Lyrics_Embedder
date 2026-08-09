from typing import Dict, Any
from PySide6.QtCore import QObject, Signal, Slot
from app.audio.verification import AudioVerificationEngine
from app.core.logging import logger

class AnalysisService(QObject):
    analysisCompleted = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(str, result=dict)
    def analyzeFile(self, file_path: str) -> Dict[str, Any]:
        try:
            analysis = AudioVerificationEngine.verify_file(file_path)
            res = analysis.model_dump()
            self.analysisCompleted.emit(res)
            return res
        except Exception as e:
            logger.error(f"AnalysisService error analyzing {file_path}: {e}")
            return {
                "file_path": file_path,
                "actual_sample_rate": 44100,
                "spectral_cutoff": 0.0,
                "legit": -1,
                "observation": f"Analysis Error: {e}",
                "interpretation": "Spectral inspection failed.",
                "confidence": 0.0,
                "reason": str(e)
            }
