import gc

import numpy as np
from faster_whisper import WhisperModel

from config.settings import WHISPER_COMPUTE, WHISPER_DEVICE, WHISPER_MODEL


class WhisperSTT:
    def __init__(self):
        self._model: WhisperModel | None = None

    def _load(self):
        if self._model is None:
            print(f"[STT] Loading Whisper '{WHISPER_MODEL}' on {WHISPER_DEVICE}/{WHISPER_COMPUTE}...")
            self._model = WhisperModel(
                WHISPER_MODEL,
                device=WHISPER_DEVICE,
                compute_type=WHISPER_COMPUTE,
                num_workers=1,
                cpu_threads=4,
            )

    def transcribe(self, audio: np.ndarray) -> tuple[str, str]:
        if audio.size == 0:
            return "", "en"

        self._load()
        segments, info = self._model.transcribe(
            audio,
            beam_size=3,
            vad_filter=False,
            language=None,
            condition_on_previous_text=False,
        )

        text = " ".join(seg.text for seg in segments).strip()
        lang = info.language if info.language in ("en", "ka") else "en"

        del audio
        gc.collect()
        return text, lang

    def unload(self):
        if self._model is not None:
            del self._model
            self._model = None
            gc.collect()