import os
import subprocess

import psutil
import pygetwindow as gw


KNOWN_APPS = {
    "notepad":          "notepad.exe",
    "calculator":       "calc.exe",
    "paint":            "mspaint.exe",
    "word":             r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel":            r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint":       r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "vscode":           r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "vs code":          r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "spotify":          r"C:\Users\{user}\AppData\Roaming\Spotify\Spotify.exe",
    "discord":          r"C:\Users\{user}\AppData\Local\Discord\Update.exe",
    "telegram":         r"C:\Users\{user}\AppData\Roaming\Telegram Desktop\Telegram.exe",
    "explorer":         "explorer.exe",
    "file explorer":    "explorer.exe",
    "task manager":     "taskmgr.exe",
    "settings":         "ms-settings:",
    "control panel":    "control.exe",
    "cmd":              "cmd.exe",
    "command prompt":   "cmd.exe",
    "powershell":       "powershell.exe",
    "snipping tool":    "snippingtool.exe",
    "clock":            "ms-clock:",
    "calendar":         "outlookcal:",
}


def _resolve(app: str) -> str:
    user = os.environ.get("USERNAME", "")
    return app.replace("{user}", user)


def open_app(name: str) -> str:
    key = name.lower().strip()
    path = KNOWN_APPS.get(key)

    if path:
        path = _resolve(path)
        if path.startswith("ms-") or path.startswith("outlook"):
            os.startfile(path)
        else:
            subprocess.Popen(path, shell=True)
        return f"Opened {name}"

    subprocess.Popen(["powershell", "-Command", f"Start-Process '{name}'"], shell=True)
    return f"Tried to open {name}"


def close_app(name: str) -> str:
    key = name.lower().strip()
    process_map = {
        "notepad": "notepad.exe",
        "calculator": "calculator.exe",
        "paint": "mspaint.exe",
        "spotify": "spotify.exe",
        "discord": "discord.exe",
        "telegram": "telegram.exe",
        "vscode": "code.exe",
        "vs code": "code.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
    }

    target = process_map.get(key, name.lower() + ".exe")
    killed = []
    for proc in psutil.process_iter(["name", "pid"]):
        if (proc.info["name"] or "").lower() == target:
            try:
                proc.kill()
                killed.append(proc.info["name"])
            except psutil.NoSuchProcess:
                pass

    return f"Closed {name}" if killed else f"{name} was not running"