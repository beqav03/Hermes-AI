import time

import mss
import numpy as np
import pyautogui
import easyocr


pyautogui.FAILSAFE = False
_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["en", "ka"], gpu=False, verbose=False)
    return _reader


def click_text(text: str) -> str:
    with mss.mss() as sct:
        raw = sct.grab(sct.monitors[1])
        img = np.array(raw)[:, :, :3]

    reader = _get_reader()
    results = reader.readtext(img)
    target = text.lower()

    for (bbox, label, conf) in results:
        if target in label.lower() and conf > 0.4:
            xs = [p[0] for p in bbox]
            ys = [p[1] for p in bbox]
            cx = int(sum(xs) / len(xs))
            cy = int(sum(ys) / len(ys))
            pyautogui.click(cx, cy)
            return f"Clicked '{label}' at ({cx}, {cy})"

    return f"Text '{text}' not found on screen"


def move_mouse(x: int, y: int) -> str:
    pyautogui.moveTo(x, y, duration=0.3)
    return f"Moved mouse to ({x}, {y})"


def click_position(x: int, y: int) -> str:
    pyautogui.click(x, y)
    return f"Clicked at ({x}, {y})"


def scroll(direction: str, amount: int = 3) -> str:
    clicks = amount if direction == "up" else -amount
    pyautogui.scroll(clicks)
    return f"Scrolled {direction}"