import pyautogui
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import ctypes


pyautogui.FAILSAFE = False


def _get_volume_interface():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))


def play_pause() -> str:
    pyautogui.press("playpause")
    return "Toggled play/pause"


def next_track() -> str:
    pyautogui.press("nexttrack")
    return "Skipped to next track"


def previous_track() -> str:
    pyautogui.press("prevtrack")
    return "Went to previous track"


def stop_media() -> str:
    pyautogui.press("stop")
    return "Stopped media"


def volume_up(amount: int = 10) -> str:
    vol = _get_volume_interface()
    current = vol.GetMasterVolumeLevelScalar()
    new = min(1.0, current + amount / 100)
    vol.SetMasterVolumeLevelScalar(new, None)
    return f"Volume set to {int(new * 100)}%"


def volume_down(amount: int = 10) -> str:
    vol = _get_volume_interface()
    current = vol.GetMasterVolumeLevelScalar()
    new = max(0.0, current - amount / 100)
    vol.SetMasterVolumeLevelScalar(new, None)
    return f"Volume set to {int(new * 100)}%"


def set_volume(level: int) -> str:
    vol = _get_volume_interface()
    clamped = max(0, min(100, level))
    vol.SetMasterVolumeLevelScalar(clamped / 100, None)
    return f"Volume set to {clamped}%"


def mute() -> str:
    vol = _get_volume_interface()
    vol.SetMute(1, None)
    return "Muted"


def unmute() -> str:
    vol = _get_volume_interface()
    vol.SetMute(0, None)
    return "Unmuted"