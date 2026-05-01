import pygetwindow as gw
import pyautogui


pyautogui.FAILSAFE = False


def _find(name: str):
    name_lower = name.lower()
    for w in gw.getAllWindows():
        if name_lower in (w.title or "").lower():
            return w
    return None


def minimize_window(name: str) -> str:
    w = _find(name)
    if not w:
        return f"No window found matching '{name}'"
    w.minimize()
    return f"Minimized {w.title}"


def maximize_window(name: str) -> str:
    w = _find(name)
    if not w:
        return f"No window found matching '{name}'"
    w.maximize()
    return f"Maximized {w.title}"


def close_window(name: str) -> str:
    w = _find(name)
    if not w:
        return f"No window found matching '{name}'"
    w.close()
    return f"Closed window: {w.title}"


def focus_window(name: str) -> str:
    w = _find(name)
    if not w:
        return f"No window found matching '{name}'"
    try:
        w.activate()
    except Exception:
        w.minimize()
        w.restore()
    return f"Focused {w.title}"


def list_windows() -> str:
    titles = [w.title for w in gw.getAllWindows() if w.title.strip()]
    if not titles:
        return "No open windows"
    return "Open windows: " + ", ".join(titles[:10])


def minimize_all() -> str:
    pyautogui.hotkey("win", "d")
    return "Minimized all windows"


def restore_all() -> str:
    pyautogui.hotkey("win", "d")
    return "Restored all windows"


def switch_window() -> str:
    pyautogui.hotkey("alt", "tab")
    return "Switched window"