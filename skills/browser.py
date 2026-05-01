import subprocess
import urllib.parse
import webbrowser

import psutil
import pygetwindow as gw


BROWSERS = {
    "chrome":  r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "edge":    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
}

DEFAULT_BROWSER = "chrome"


def _open_exe(path: str, *args):
    subprocess.Popen([path, *args])


def open_browser(browser: str = DEFAULT_BROWSER) -> str:
    exe = BROWSERS.get(browser.lower(), BROWSERS[DEFAULT_BROWSER])
    _open_exe(exe)
    return f"Opened {browser}"


def open_url(url: str, browser: str = DEFAULT_BROWSER) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opened {url}"


def search_google(query: str, browser: str = DEFAULT_BROWSER) -> str:
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded}"
    webbrowser.open(url)
    return f"Searched Google for: {query}"


def search_youtube(query: str) -> str:
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={encoded}"
    webbrowser.open(url)
    return f"Searched YouTube for: {query}"


def close_browser(browser: str = "all") -> str:
    targets = list(BROWSERS.keys()) if browser == "all" else [browser.lower()]
    killed = []
    for proc in psutil.process_iter(["name", "pid"]):
        pname = (proc.info["name"] or "").lower()
        for t in targets:
            if t in pname or (t == "chrome" and "chrome" in pname):
                try:
                    proc.kill()
                    if t not in killed:
                        killed.append(t)
                except psutil.NoSuchProcess:
                    pass
    return f"Closed {', '.join(killed)}" if killed else "No browser was open"