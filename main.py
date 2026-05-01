import gc
import threading
import time
import psutil, os

from brain.ollama_client import OllamaBrain
from config.settings import HIDE_DELAY_S, OLLAMA_MODEL, WHISPER_MODEL
from core.registry import SkillRegistry
from core.router import Router
from skills import files
from ui.status_window import StatusWindow
from voice.recorder import VADRecorder
from voice.stt import WhisperSTT
from voice.tts import EdgeTTS
from voice.wake_word import WakeWordListener

used = psutil.Process(os.getpid()).memory_info().rss / (1024**3)
print(f"[RAM] Hermes using {used:.2f} GB")

def setup_router(status_cb) -> Router:
    registry = SkillRegistry()
    registry.register(
        name="open_folder",
        handler=files.open_folder,
        description="Open a folder in Windows File Explorer",
        params={
            "path": "string — one of: downloads, documents, desktop, pictures, music, videos — or a full path"
        },
    )
    brain = OllamaBrain()
    return Router(registry, brain, status_cb=status_cb)


class HermesApp:
    def __init__(self):
        self.stop_event = threading.Event()
        self.status = StatusWindow(on_close=self.stop_event.set)
        self.router = setup_router(self.status.set)

        print(f"[Init] Whisper: {WHISPER_MODEL}  LLM: {OLLAMA_MODEL}")
        self.recorder = VADRecorder()
        self.stt = WhisperSTT()
        self.tts = EdgeTTS()

        self.wake = WakeWordListener(
            recorder=self.recorder,
            stt=self.stt,
            on_wake=self._on_wake,
        )

    def _on_wake(self, initial_command: str, lang: str):
        self.status.reset()
        self.status.show_centered()

        try:
            if initial_command:
                self._process(initial_command, lang)
            else:
                self.status.set("SPEAKING")
                greeting = "Yes, how can I help you?" if lang == "en" else "დიახ, როგორ შემიძლია დაგეხმაროთ?"
                self.tts.speak(greeting, lang=lang)
                self.status.set("LISTENING")
                audio = self.recorder.record()
                if audio.size == 0:
                    self._finish()
                    return
                text, lang2 = self.stt.transcribe(audio)
                self._process(text, lang2)
        except Exception as e:
            print(f"Pipeline error: {e}")
            self.status.set("ERROR")
            time.sleep(HIDE_DELAY_S)
            self.status.hide()
        finally:
            gc.collect()

    def _process(self, text: str, lang: str):
        self.status.set_transcript(text)
        print(f"[{lang}] {text}")

        if not text.strip():
            self._finish()
            return

        self.status.set("THINKING")
        reply = self.router.handle(text)
        self.status.set_reply(reply)
        print(f"→ {reply}")

        self.status.set("SPEAKING")
        self.tts.speak(reply, lang=lang)
        self._finish()

    def _finish(self):
        self.status.set("IDLE")
        time.sleep(HIDE_DELAY_S)
        self.status.hide()

    def run(self):
        self.wake.start()
        print('Hermes is listening. Say "Hermes" followed by your command.\n')
        try:
            self.status.run()
        finally:
            self.stop_event.set()
            self.wake.stop()
            self.stt.unload()
            gc.collect()


if __name__ == "__main__":
    HermesApp().run()