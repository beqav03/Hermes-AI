import gc
import threading
import time

from brain.ollama_client import OllamaBrain
from config.settings import HIDE_DELAY_S, OLLAMA_MODEL, WHISPER_MODEL
from core.registry import SkillRegistry
from core.router import Router
from skills import files, browser, apps, media, window, system, screen
from ui.status_window import StatusWindow
from voice.recorder import VADRecorder
from voice.stt import WhisperSTT
from voice.tts import EdgeTTS
from voice.wake_word import WakeWordListener


def setup_router(status_cb) -> Router:
    registry = SkillRegistry()

    registry.register("open_folder",       files.open_folder,
        "Open a folder in File Explorer",
        {"path": "string — downloads, documents, desktop, pictures, music, videos or full path"})

    registry.register("open_browser",      browser.open_browser,
        "Open a web browser",
        {"browser": "string — chrome, firefox, edge"})

    registry.register("open_url",          browser.open_url,
        "Open a specific URL or website",
        {"url": "string — full URL or domain", "browser": "string — chrome, firefox, edge"})

    registry.register("search_google",     browser.search_google,
        "Search something on Google",
        {"query": "string — the search query"})

    registry.register("search_youtube",    browser.search_youtube,
        "Search something on YouTube",
        {"query": "string — the search query"})

    registry.register("close_browser",     browser.close_browser,
        "Close a browser or all browsers",
        {"browser": "string — chrome, firefox, edge, or 'all'"})

    registry.register("open_app",          apps.open_app,
        "Open any application by name",
        {"name": "string — app name e.g. notepad, spotify, discord, vscode, word, excel"})

    registry.register("close_app",         apps.close_app,
        "Close any running application by name",
        {"name": "string — app name"})

    registry.register("play_pause",        media.play_pause,
        "Play or pause currently playing media",
        {})

    registry.register("next_track",        media.next_track,
        "Skip to next track",
        {})

    registry.register("previous_track",    media.previous_track,
        "Go to previous track",
        {})

    registry.register("stop_media",        media.stop_media,
        "Stop playing media",
        {})

    registry.register("volume_up",         media.volume_up,
        "Increase system volume",
        {"amount": "integer — percent to raise, default 10"})

    registry.register("volume_down",       media.volume_down,
        "Decrease system volume",
        {"amount": "integer — percent to lower, default 10"})

    registry.register("set_volume",        media.set_volume,
        "Set volume to a specific level",
        {"level": "integer — 0 to 100"})

    registry.register("mute",              media.mute,
        "Mute system audio",
        {})

    registry.register("unmute",            media.unmute,
        "Unmute system audio",
        {})

    registry.register("minimize_window",   window.minimize_window,
        "Minimize a window by its title",
        {"name": "string — partial window title"})

    registry.register("maximize_window",   window.maximize_window,
        "Maximize a window by its title",
        {"name": "string — partial window title"})

    registry.register("close_window",      window.close_window,
        "Close a window by its title",
        {"name": "string — partial window title"})

    registry.register("focus_window",      window.focus_window,
        "Bring a window to foreground by its title",
        {"name": "string — partial window title"})

    registry.register("list_windows",      window.list_windows,
        "List all open windows",
        {})

    registry.register("minimize_all",      window.minimize_all,
        "Minimize all windows and show the desktop",
        {})

    registry.register("switch_window",     window.switch_window,
        "Switch to the next window (Alt+Tab)",
        {})

    registry.register("lock_screen",       system.lock_screen,
        "Lock the Windows screen",
        {})

    registry.register("shutdown",          system.shutdown,
        "Shut down the computer",
        {"delay": "integer — seconds before shutdown, default 0"})

    registry.register("restart",           system.restart,
        "Restart the computer",
        {"delay": "integer — seconds before restart, default 0"})

    registry.register("sleep",             system.sleep,
        "Put the computer to sleep",
        {})

    registry.register("take_screenshot",   system.take_screenshot,
        "Take a screenshot and save to Pictures folder",
        {"filename": "string — filename without extension, default 'screenshot'"})

    registry.register("press_keys",        system.press_keys,
        "Press a keyboard shortcut or key e.g. ctrl+c, enter, escape, win+d",
        {"keys": "string — key combination using + separator"})

    registry.register("type_text",         system.type_text,
        "Type text as if using the keyboard",
        {"text": "string — text to type"})

    registry.register("copy",              system.copy,
        "Copy selected content (Ctrl+C)",
        {})

    registry.register("paste",             system.paste,
        "Paste from clipboard (Ctrl+V)",
        {})

    registry.register("undo",              system.undo,
        "Undo last action (Ctrl+Z)",
        {})

    registry.register("click_text",        screen.click_text,
        "Find text on screen using OCR and click it",
        {"text": "string — visible text to click"})

    registry.register("scroll",            screen.scroll,
        "Scroll the current window up or down",
        {"direction": "string — up or down", "amount": "integer — number of scroll steps, default 3"})

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
                greeting = (
                    "Yes, how can I help you?"
                    if lang == "en"
                    else "დიახ, როგორ შემიძლია დაგეხმაროთ?"
                )
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