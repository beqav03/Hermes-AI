import threading

from brain.ollama_client import OllamaBrain
from core.registry import SkillRegistry
from core.router import Router
from skills import files
from ui.status_window import StatusWindow


def setup(status_cb) -> Router:
    registry = SkillRegistry()
    registry.register(
        name="open_folder",
        handler=files.open_folder,
        description="Open a folder in Windows File Explorer",
        params={
            "path": "string — one of: downloads, documents, desktop, pictures, music, videos — or a full path like C:/Users/..."
        },
    )
    brain = OllamaBrain(model="qwen2.5:7b-instruct")
    return Router(registry, brain, status_cb=status_cb)


def worker(router: Router, status: StatusWindow, stop_event: threading.Event):
    print("Hermes ready. Type 'exit' to quit.\n")
    while not stop_event.is_set():
        status.set("IDLE")
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text.lower() in ("exit", "quit"):
            break
        if not text:
            continue
        try:
            print(router.handle(text))
        except Exception as e:
            status.set("ERROR")
            print(f"Error: {e}")
    stop_event.set()
    try:
        status.root.after(0, status.root.destroy)
    except Exception:
        pass


def main():
    stop_event = threading.Event()
    status = StatusWindow(on_close=stop_event.set)
    router = setup(status.set)
    threading.Thread(
        target=worker, args=(router, status, stop_event), daemon=True
    ).start()
    status.run()


if __name__ == "__main__":
    main()