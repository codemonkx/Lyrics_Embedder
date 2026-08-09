from typing import Optional
from pydantic import BaseModel

class AudioAnalysis(BaseModel):
    file_path: str
    actual_sample_rate: int
    spectral_cutoff: float
    legit: int  # 1 = Genuine, 0 = Anomaly/Fake, -1 = Error
    observation: str
    interpretation: str
    confidence: float
    reason: str
