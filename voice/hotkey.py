import keyboard


class Hotkey:
    def __init__(self, combo: str, callback):
        self.combo = combo
        self.callback = callback
        self._handle = None

    def start(self):
        self._handle = keyboard.add_hotkey(self.combo, self.callback)

    def stop(self):
        if self._handle is not None:
            try:
                keyboard.remove_hotkey(self._handle)
            except (KeyError, ValueError):
                pass
            self._handle = None