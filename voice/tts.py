import asyncio
import os
import tempfile
import threading

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
import edge_tts


class EdgeTTS:
    VOICES = {
        "en": "en-US-AriaNeural",
        "ka": "ka-GE-EkaNeural",
    }

    def __init__(self):
        pygame.mixer.init()
        self._lock = threading.Lock()

    def speak(self, text: str, lang: str = "en"):
        if not text.strip():
            return
        voice = self.VOICES.get(lang, self.VOICES["en"])
        audio = asyncio.run(self._synthesize(text, voice))

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(audio)
                tmp_path = f.name
            with self._lock:
                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(50)
                pygame.mixer.music.unload()
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    async def _synthesize(self, text: str, voice: str) -> bytes:
        communicate = edge_tts.Communicate(text, voice)
        buf = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buf.extend(chunk["data"])
        return bytes(buf)