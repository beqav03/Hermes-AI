import psutil


def _auto_whisper_model() -> str:
    gb = psutil.virtual_memory().total / (1024 ** 3)
    if gb >= 16:
        return "medium"
    if gb >= 8:
        return "small"
    return "tiny"


WHISPER_MODEL = _auto_whisper_model()

OLLAMA_MODEL = "qwen2.5:3b"
OLLAMA_TIMEOUT = 30

VAD_AGGRESSIVENESS = 3
VAD_SILENCE_HANGOVER_MS = 1500
VAD_MAX_DURATION_S = 30
VAD_MIN_SPEECH_MS = 300
VAD_MAX_BUFFER_FRAMES = 1500

HIDE_DELAY_S = 1.2

WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE = "int8"
ENABLE_SCREEN_OCR = True
