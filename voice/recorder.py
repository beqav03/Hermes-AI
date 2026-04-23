import numpy as np
import sounddevice as sd
import webrtcvad


class VADRecorder:
    SAMPLE_RATE = 16000
    FRAME_MS = 30
    FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000
    SILENCE_HANGOVER_MS = 1500
    MAX_DURATION_S = 30
    MIN_SPEECH_MS = 300

    def __init__(self, aggressiveness: int = 2):
        self.vad = webrtcvad.Vad(aggressiveness)

    def record(self) -> np.ndarray:
        frames = []
        silence_frames = 0
        speech_frames = 0
        max_silence = self.SILENCE_HANGOVER_MS // self.FRAME_MS
        max_total = self.MAX_DURATION_S * 1000 // self.FRAME_MS
        speech_started = False

        with sd.InputStream(
            samplerate=self.SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=self.FRAME_SAMPLES,
        ) as stream:
            for _ in range(int(max_total)):
                block, _ = stream.read(self.FRAME_SAMPLES)
                mono = block[:, 0]
                frames.append(mono)
                is_speech = self.vad.is_speech(mono.tobytes(), self.SAMPLE_RATE)

                if is_speech:
                    speech_started = True
                    speech_frames += 1
                    silence_frames = 0
                elif speech_started:
                    silence_frames += 1
                    if silence_frames >= max_silence:
                        break

        if speech_frames * self.FRAME_MS < self.MIN_SPEECH_MS:
            return np.zeros(0, dtype=np.float32)

        audio = np.concatenate(frames).astype(np.float32) / 32768.0
        return audio