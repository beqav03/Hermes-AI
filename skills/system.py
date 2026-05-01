import os
import subprocess
import ctypes

import pyautogui


pyautogui.FAILSAFE = False


def lock_screen() -> str:
    ctypes.windll.user32.LockWorkStation()
    return "Screen locked"


def shutdown(delay: int = 0) -> str:
    os.system(f"shutdown /s /t {delay}")
    return f"Shutting down in {delay} seconds"


def restart(delay: int = 0) -> str:
    os.system(f"shutdown /r /t {delay}")
    return f"Restarting in {delay} seconds"


def sleep() -> str:
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    return "Going to sleep"


def take_screenshot(filename: str = "screenshot") -> str:
    from pathlib import Path
    import pyautogui
    path = Path.home() / "Pictures" / f"{filename}.png"
    pyautogui.screenshot(str(path))
    return f"Screenshot saved to {path}"


def type_text(text: str) -> str:
    pyautogui.write(text, interval=0.04)
    return f"Typed: {text}"


def press_keys(keys: str) -> str:
    parts = [k.strip() for k in keys.lower().split("+")]
    if len(parts) == 1:
        pyautogui.press(parts[0])
    else:
        pyautogui.hotkey(*parts)
    return f"Pressed {keys}"


def copy() -> str:
    pyautogui.hotkey("ctrl", "c")
    return "Copied"


def paste() -> str:
    pyautogui.hotkey("ctrl", "v")
    return "Pasted"


def undo() -> str:
    pyautogui.hotkey("ctrl", "z")
    return "Undid last action"