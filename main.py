import queue
import threading

from brain.ollama_client import OllamaBrain
from core.registry import SkillRegistry
from core.router import Router
from skills import files
from ui.status_window import StatusWindow
from voice.hotkey import Hotkey
from voice.recorder import VADRecorder
from voice.stt import WhisperSTT
from voice.tts import EdgeTTS


HOTKEY = "ctrl+alt+h"
WHISPER_MODEL = "medium"


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
    brain = OllamaBrain(model="qwen2.5:7b-instruct")
    return Router(registry, brain, status_cb=status_cb)


def voice_worker(router, status, recorder, stt, tts, trigger_q, stop_event):
    while not stop_event.is_set():
        try:
            trigger_q.get(timeout=0.5)
        except queue.Empty:
            continue

        while not trigger_q.empty():
            try:
                trigger_q.get_nowait()
            except queue.Empty:
                break

        try:
            status.set("LISTENING")
            audio = recorder.record()

            if audio.size == 0:
                status.set("IDLE")
                continue

            status.set("THINKING")
            text, lang = stt.transcribe(audio)
            status.set_transcript(text)
            print(f"[{lang}] {text}")

            if not text.strip():
                status.set("IDLE")
                continue

            reply = router.handle(text)
            status.set_reply(reply)
            print(f"→ {reply}")

            status.set("SPEAKING")
            tts.speak(reply, lang=lang)
            status.set("IDLE")
        except Exception as e:
            print(f"Voice pipeline error: {e}")
            status.set("ERROR")


def main():
    stop_event = threading.Event()
    status = StatusWindow(on_close=stop_event.set)
    router = setup_router(status.set)

    print(f"Loading Whisper '{WHISPER_MODEL}' (first run downloads ~1.5 GB)...")
    recorder = VADRecorder()
    stt = WhisperSTT(model_size=WHISPER_MODEL)
    tts = EdgeTTS()

    trigger_q = queue.Queue()
    hotkey = Hotkey(HOTKEY, lambda: trigger_q.put(True))
    hotkey.start()

    print(f"Hermes ready. Press {HOTKEY.upper()} and speak.\n")

    threading.Thread(
        target=voice_worker,
        args=(router, status, recorder, stt, tts, trigger_q, stop_event),
        daemon=True,
    ).start()

    try:
        status.run()
    finally:
        stop_event.set()
        hotkey.stop()


if __name__ == "__main__":
    main()