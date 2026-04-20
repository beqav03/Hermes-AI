import os
from pathlib import Path


KNOWN = {
    "downloads": Path.home() / "Downloads",
    "documents": Path.home() / "Documents",
    "desktop": Path.home() / "Desktop",
    "pictures": Path.home() / "Pictures",
    "music": Path.home() / "Music",
    "videos": Path.home() / "Videos",
}


def open_folder(path: str) -> str:
    key = (path or "").lower().strip()
    target = KNOWN.get(key, Path(path).expanduser())
    if not target.exists():
        return f"Folder not found: {target}"
    os.startfile(str(target))
    return f"Opened {target}"