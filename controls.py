"""Playback and volume actions."""

import time
from collections.abc import Callable

import config
import macos_control
import pear_client

_RESUME_AFTER_SKIP_DELAY_SECONDS = 0.15


def toggle_play_pause() -> None:
    pear_client.send_command("toggle-play")


def skip_track(direction: str) -> None:
    endpoint = "next" if direction == "next" else "previous"
    was_paused = pear_client.fetch_now_playing()["isPaused"]
    pear_client.send_command(endpoint)
    if was_paused:
        time.sleep(_RESUME_AFTER_SKIP_DELAY_SECONDS)
        pear_client.send_command("play")


def adjust_volume(direction: str) -> int:
    delta = config.VOLUME_STEP if direction == "vol_up" else -config.VOLUME_STEP
    return macos_control.adjust_system_volume(delta)


_ACTIONS: dict[str, Callable[[], object]] = {
    "playpause": toggle_play_pause,
    "next": lambda: skip_track("next"),
    "prev": lambda: skip_track("prev"),
    "vol_up": lambda: adjust_volume("vol_up"),
    "vol_down": lambda: adjust_volume("vol_down"),
}


def dispatch(action: str) -> bool:
    """Dispatch an action and return False for unknown actions."""
    handler = _ACTIONS.get(action)
    if handler is None:
        return False
    handler()
    return True
