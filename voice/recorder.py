import gc
from collections import deque

import numpy as np
import sounddevice as sd
import webrtcvad

from config.settings import (
    VAD_AGGRESSIVENESS,
    VAD_MAX_BUFFER_FRAMES,
    VAD_MAX_DURATION_S,
    VAD_MIN_SPEECH_MS,
    VAD_SILENCE_HANGOVER_MS,
)


class VADRecorder:
    SAMPLE_RATE = 16000
    FRAME_MS = 30
    FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000

    def __init__(self):
        self.vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
        self._silence_frames = VAD_SILENCE_HANGOVER_MS // self.FRAME_MS
        self._max_frames = VAD_MAX_DURATION_S * 1000 // self.FRAME_MS

    def record(self) -> np.ndarray:
        buf: deque = deque(maxlen=VAD_MAX_BUFFER_FRAMES)
        silence_count = 0
        speech_count = 0
        speech_started = False

        with sd.InputStream(
            samplerate=self.SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=self.FRAME_SAMPLES,
        ) as stream:
            for _ in range(int(self._max_frames)):
                block, _ = stream.read(self.FRAME_SAMPLES)
                frame = block[:, 0].copy()
                buf.append(frame)

                is_speech = self.vad.is_speech(frame.tobytes(), self.SAMPLE_RATE)

                if is_speech:
                    speech_started = True
                    speech_count += 1
                    silence_count = 0
                elif speech_started:
                    silence_count += 1
                    if silence_count >= self._silence_frames:
                        break

        if speech_count * self.FRAME_MS < VAD_MIN_SPEECH_MS:
            return np.zeros(0, dtype=np.float32)

        audio = np.concatenate(list(buf)).astype(np.float32) / 32768.0
        del buf
        gc.collect()
        return audio