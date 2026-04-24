import re
import threading


class WakeWordListener:
    WAKE_PATTERNS = [
        re.compile(r"\bhermes\b", re.IGNORECASE),
        re.compile(r"\bhermies\b", re.IGNORECASE),
        re.compile(r"\bher\s*mess\b", re.IGNORECASE),
        re.compile(r"ჰერმეს"),
        re.compile(r"ერმეს"),
    ]

    def __init__(self, recorder, stt, on_wake):
        self.recorder = recorder
        self.stt = stt
        self.on_wake = on_wake
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _loop(self):
        while not self._stop.is_set():
            try:
                audio = self.recorder.record()
                if audio.size == 0:
                    continue
                text, lang = self.stt.transcribe(audio)
                command = self._extract_command(text)
                if command is not None:
                    self.on_wake(command, lang)
            except Exception as e:
                print(f"Wake listener error: {e}")

    def _extract_command(self, text: str):
        if not text:
            return None
        for pattern in self.WAKE_PATTERNS:
            match = pattern.search(text)
            if match:
                return text[match.end():].strip(" ,.!?:;-—")
        return None