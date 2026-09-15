"""Client for the Pear Desktop local API."""


from __future__ import annotations


import json
import logging
import urllib.request



from . import config



LOGGER = logging.getLogger(__name__)
_last_good_progress: dict[str, dict[str, float]] = {}



_DEFAULT_SONG_INFO = {
    "title": "YouTube Music",
    "artist": "Pear Desktop Session",
    "album": "",
    "artwork": "",
    "isPaused": True,
    "elapsed": 0.0,
    "duration": 0.0,
}



def _track_signature(title: str, artist: str, duration: float) -> str:
    return f"{title}|{artist}|{duration}"



def _coerce_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0



def _sanitize_progress(elapsed: float, duration: float) -> tuple[float, float]:
    if duration <= 0 or duration > config.MAX_PLAUSIBLE_DURATION_SECONDS:
        return 0.0, 0.0
    return max(0.0, min(elapsed, duration)), duration



def _reconcile_progress(title: str, artist: str, elapsed: float, duration: float) -> float:
    key = _track_signature(title, artist, duration)
    previous = _last_good_progress.get(key)
    current = {"elapsed": elapsed, "duration": duration}
    if previous is None or abs(previous["duration"] - duration) > config.DURATION_CHANGE_THRESHOLD_SECONDS:
        _last_good_progress[key] = current
        return elapsed
    was_near_end = duration - previous["elapsed"] < config.NEAR_END_THRESHOLD_SECONDS
    is_now_at_end = duration - elapsed < config.AT_END_THRESHOLD_SECONDS
    if is_now_at_end and not was_near_end:
        return previous["elapsed"]
    _last_good_progress[key] = current
    return elapsed



def fetch_now_playing() -> dict:
    """Fetch and normalize current playback state."""
    try:
        request = urllib.request.Request(
            f"{config.PEAR_API_BASE}/song",
            headers={"User-Agent": "PearRemote/1.0"},
        )
        with urllib.request.urlopen(request, timeout=config.API_TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        LOGGER.debug("Unable to read Pear Desktop status: %s", error)
        return dict(_DEFAULT_SONG_INFO)



    title = data.get("title", "YouTube Music")
    artist = data.get("artist", "Now Playing")
    elapsed = _coerce_float(data.get("elapsedSeconds") or data.get("songProgress", 0))
    duration = _coerce_float(data.get("songDuration") or data.get("duration", 0))
    elapsed, duration = _sanitize_progress(elapsed, duration)
    if duration > 0:
        elapsed = _reconcile_progress(title, artist, elapsed, duration)



    return {
        "title": title,
        "artist": artist,
        "album": data.get("album", ""),
        "artwork": data.get("imageSrc", "") or data.get("cover", ""),
        "isPaused": bool(data.get("isPaused", False)),
        "elapsed": elapsed,
        "duration": duration,
    }



def send_command(endpoint: str) -> bool:
    """POST a playback command to Pear Desktop."""
    try:
        request = urllib.request.Request(
            f"{config.PEAR_API_BASE}/{endpoint}",
            data=b"",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=config.API_TIMEOUT) as response:
            return response.status == 200
    except OSError as error:
        LOGGER.warning("Pear API command %s failed: %s", endpoint, error)
        return False



def get_shuffle_state() -> bool:
    """Get current shuffle state from /api/v1/shuffle GET"""
    try:
        request = urllib.request.Request(
            f"{config.PEAR_API_BASE}/shuffle",
            headers={"User-Agent": "PearRemote/1.0"},
        )
        with urllib.request.urlopen(request, timeout=config.API_TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
            return bool(data.get("state", False))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        LOGGER.debug("Unable to read shuffle state: %s", error)
        return False



def toggle_shuffle() -> bool:
    """Toggle shuffle via /api/v1/shuffle POST"""
    try:
        request = urllib.request.Request(
            f"{config.PEAR_API_BASE}/shuffle",
            data=b"",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=config.API_TIMEOUT) as response:
            return response.status == 204
    except OSError as error:
        LOGGER.warning("Pear API shuffle toggle failed: %s", error)
        return False



def get_repeat_mode() -> str:
    """Get current repeat mode from /api/v1/repeat-mode GET (NONE, ALL, ONE)"""
    try:
        request = urllib.request.Request(
            f"{config.PEAR_API_BASE}/repeat-mode",
            headers={"User-Agent": "PearRemote/1.0"},
        )
        with urllib.request.urlopen(request, timeout=config.API_TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("mode", "NONE")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        LOGGER.debug("Unable to read repeat mode: %s", error)
        return "NONE"



def switch_repeat(iteration: int = 0) -> bool:
    """Switch repeat mode via /api/v1/switch-repeat POST"""
    try:
        request = urllib.request.Request(
            f"{config.PEAR_API_BASE}/switch-repeat",
            data=json.dumps({"iteration": iteration}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=config.API_TIMEOUT) as response:
            return response.status == 204
    except OSError as error:
        LOGGER.warning("Pear API switch repeat failed: %s", error)
        return False



def cycle_repeat_mode() -> bool:
    """Cycle through repeat modes: NONE -> ALL -> ONE -> NONE"""
    try:
        # Just call switch-repeat with iteration 0 to cycle to next mode
        request = urllib.request.Request(
            f"{config.PEAR_API_BASE}/switch-repeat",
            data=json.dumps({"iteration": 0}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=config.API_TIMEOUT) as response:
            return response.status == 204
    except OSError as error:
        LOGGER.warning("Pear API cycle repeat failed: %s", error)
        return False
