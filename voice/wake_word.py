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
        self._busy = threading.Lock()
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

                if self._busy.locked():
                    continue

                text, lang = self.stt.transcribe(audio)
                command = self._extract_command(text)
                if command is not None:
                    threading.Thread(
                        target=self._dispatch,
                        args=(command, lang),
                        daemon=True,
                    ).start()
            except Exception as e:
                print(f"Wake listener error: {e}")

    def _dispatch(self, command: str, lang: str):
        if not self._busy.acquire(blocking=False):
            return
        try:
            self.on_wake(command, lang)
        finally:
            self._busy.release()

    def _extract_command(self, text: str):
        if not text:
            return None
        for pattern in self.WAKE_PATTERNS:
            match = pattern.search(text)
            if match:
                return text[match.end():].strip(" ,.!?:;-—")
        return None