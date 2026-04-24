import numpy as np
from faster_whisper import WhisperModel


class WhisperSTT:
    def __init__(self, model_size: str = "medium", device: str = "cpu"):
        self.model = WhisperModel(model_size, device=device, compute_type="int8")

    def transcribe(self, audio: np.ndarray) -> tuple[str, str]:
        if audio.size == 0:
            return "", "en"
        segments, info = self.model.transcribe(
            audio,
            beam_size=5,
            vad_filter=False,
            language=None,
        )
        text = " ".join(seg.text for seg in segments).strip()
        lang = info.language if info.language in ("en", "ka") else "en"
        return text, lang