"""macOS system integration through osascript."""

import subprocess

from . import config


def get_system_volume() -> int:
    """Return the current macOS output volume, or a safe fallback."""
    try:
        result = subprocess.run(
            ["osascript", "-e", "output volume of (get volume settings)"],
            capture_output=True,
            text=True,
            timeout=config.OSASCRIPT_TIMEOUT_SECONDS,
            check=False,
        )
        return max(0, min(100, int(result.stdout.strip() or config.VOLUME_FALLBACK_PERCENT)))
    except (OSError, ValueError, subprocess.SubprocessError):
        return config.VOLUME_FALLBACK_PERCENT


def set_system_volume(volume: int) -> None:
    """Set macOS output volume, ignoring failures."""
    volume = max(0, min(100, int(volume)))
    try:
        subprocess.run(
            ["osascript", "-e", f"set volume output volume {volume}"],
            timeout=config.OSASCRIPT_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        pass


def adjust_system_volume(delta: int) -> int:
    """Adjust system volume by delta and return the resulting value."""
    new_volume = max(0, min(100, get_system_volume() + delta))
    set_system_volume(new_volume)
    return new_volume
