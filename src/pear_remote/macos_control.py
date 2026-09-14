"""macOS system integration through osascript."""

import subprocess
import time

from . import config

_volume_cache: dict[str, float | int] = {"value": config.VOLUME_FALLBACK_PERCENT, "ts": 0.0}


def _read_volume_from_system() -> int:
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


def get_system_volume(force: bool = False) -> int:
    """Return the current macOS output volume, only re-checking the OS periodically."""
    now = time.monotonic()
    if not force and (now - _volume_cache["ts"]) < config.VOLUME_POLL_INTERVAL_SECONDS:
        return _volume_cache["value"]
    fresh_value = _read_volume_from_system()
    _volume_cache["value"] = fresh_value
    _volume_cache["ts"] = now
    return fresh_value


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
    _volume_cache["value"] = volume
    _volume_cache["ts"] = time.monotonic()


def adjust_system_volume(delta: int) -> int:
    """Adjust system volume by delta and return the resulting value."""
    new_volume = max(0, min(100, get_system_volume() + delta))
    set_system_volume(new_volume)
    return new_volume