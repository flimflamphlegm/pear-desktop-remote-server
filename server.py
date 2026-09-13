import http.server
import json
import os
import socket
import subprocess
import time
import urllib.parse
import urllib.request

import config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Track last known good progress per track key
_last_good_progress = {}  # key -> {"elapsed": float, "duration": float}

def _track_key(info: dict) -> str:
    # Use title+artist+duration as a simple key
    return f"{info.get('title', '')}|{info.get('artist', '')}|{info.get('duration', 0)}"


def get_local_ip() -> str:
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  try:
    s.connect(("10.255.255.255", 1))
    return s.getsockname()[0]
  except Exception:
    return "127.0.0.1"
  finally:
    s.close()


def get_mac_volume() -> int:
  try:
    cmd = subprocess.run(
        ["osascript", "-e", "output volume of (get volume settings)"],
        capture_output=True,
        text=True,
        timeout=0.5,
    )
    return int(cmd.stdout.strip() or 50)
  except Exception:
    return 50


def set_mac_volume(volume: int):
  try:
    subprocess.run(["osascript", "-e", f"set volume output volume {volume}"])
  except Exception:
    pass


def pear_api_post(endpoint: str) -> bool:
  url = f"{config.PEAR_API_BASE}/{endpoint}"
  try:
    req = urllib.request.Request(
        url, data=b"", headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=config.API_TIMEOUT) as resp:
      return resp.status == 200
  except Exception as e:
    print(f"[API ERROR] POST /{endpoint} failed: {e}")
    return False


def get_song_info() -> dict:
    global _last_good_progress

    url = f"{config.PEAR_API_BASE}/song-info"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=config.API_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))

            title = data.get("title", "YouTube Music")
            artist = data.get("artist", "Now Playing")
            album = data.get("album", "")
            artwork = data.get("imageSrc", "") or data.get("cover", "")
            is_paused = data.get("isPaused", False)

            elapsed = data.get("elapsedSeconds", 0) or data.get("songProgress", 0)
            duration = data.get("songDuration", 0) or data.get("duration", 0)

            # Normalize types
            try:
                elapsed = float(elapsed)
            except (TypeError, ValueError):
                elapsed = 0.0

            try:
                duration = float(duration)
            except (TypeError, ValueError):
                duration = 0.0

            # Basic sanity
            if duration <= 0 or duration > 3 * 3600:  # > 3 hours likely bogus
                elapsed = 0.0
                duration = 0.0

            if duration > 0:
                if elapsed < 0:
                    elapsed = 0.0
                elif elapsed > duration:
                    elapsed = duration

            # Build a key for this track
            info = {
                "title": title,
                "artist": artist,
                "album": album,
                "artwork": artwork,
                "isPaused": is_paused,
                "elapsed": elapsed,
                "duration": duration,
            }
            key = _track_key(info)

            # Heuristic: if elapsed == duration but previously we were far from end,
            # treat this as invalid and keep last good elapsed.
            if key in _last_good_progress:
                last = _last_good_progress[key]
                last_elapsed = last["elapsed"]
                last_duration = last["duration"]

                # If duration changed significantly, treat as new track state; reset
                if abs(last_duration - duration) > 5:
                    _last_good_progress[key] = {"elapsed": elapsed, "duration": duration}
                else:
                    # Suspicious "at end" while we were not near end before
                    near_end_before = (last_duration - last_elapsed) < 5.0
                    now_at_end = (duration - elapsed) < 1.0

                    if now_at_end and not near_end_before:
                        # Don't trust this "at end"; keep last good elapsed
                        elapsed = last_elapsed
                    else:
                        # Looks consistent; update last good
                        _last_good_progress[key] = {"elapsed": elapsed, "duration": duration}
            else:
                # First time seeing this track state; store as baseline
                _last_good_progress[key] = {"elapsed": elapsed, "duration": duration}

            return {
                "title": title,
                "artist": artist,
                "album": album,
                "artwork": artwork,
                "isPaused": is_paused,
                "elapsed": elapsed,
                "duration": duration,
            }
    except Exception:
        pass

    return {
        "title": "YouTube Music",
        "artist": "Pear Desktop Session",
        "album": "",
        "artwork": "",
        "isPaused": True,
        "elapsed": 0,
        "duration": 0,
    }


def render_html_template() -> str:
  template_path = os.path.join(BASE_DIR, "index.html")
  with open(template_path, "r", encoding="utf-8") as f:
    html = f.read()

  replacements = {
      "{{BACKGROUND_COLOR}}": config.BACKGROUND_COLOR,
      "{{CARD_BACKGROUND}}": config.CARD_BACKGROUND,
      "{{CARD_MAX_WIDTH}}": config.CARD_MAX_WIDTH,
      "{{ARTWORK_MAX_HEIGHT}}": config.ARTWORK_MAX_HEIGHT,
      "{{TRACK_BAR_HEIGHT}}": config.TRACK_BAR_HEIGHT,
      "{{BUTTON_MIN_HEIGHT}}": config.BUTTON_MIN_HEIGHT,
      "{{ACCENT_COLOR}}": config.ACCENT_COLOR,
      "{{POLL_INTERVAL_MS}}": str(config.POLL_INTERVAL_MS),
  }

  for key, val in replacements.items():
    html = html.replace(key, val)

  return html


class PearRemoteHandler(http.server.BaseHTTPRequestHandler):

  def log_message(self, format, *args):
    pass

  def send_json(self, data: dict, status=200):
    self.send_response(status)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps(data).encode("utf-8"))

  def do_GET(self):
    url_path = urllib.parse.urlparse(self.path).path

    if url_path == "/favicon.ico":
      self.send_response(204)
      self.end_headers()
      return

    if url_path == "/api/status":
      info = get_song_info()
      info["volume"] = get_mac_volume()
      self.send_json(info)
      return

    if url_path.startswith("/control/"):
      action = url_path.split("/")[-1]
      self.handle_control(action)
      self.send_response(200)
      self.end_headers()
      self.wfile.write(b"OK")
      return

    self.send_response(200)
    self.send_header("Content-type", "text/html; charset=utf-8")
    self.end_headers()
    self.wfile.write(render_html_template().encode("utf-8"))

  def handle_control(self, action: str):
    if action == "playpause":
      pear_api_post("toggle-play")
    elif action in ["next", "prev"]:
      endpoint = "next" if action == "next" else "previous"
      info = get_song_info()
      pear_api_post(endpoint)
      if info["isPaused"]:
        time.sleep(0.15)
        pear_api_post("play")
    elif action in ["vol_up", "vol_down"]:
      current = get_mac_volume()
      delta = config.VOLUME_STEP if action == "vol_up" else -config.VOLUME_STEP
      new_vol = max(0, min(100, current + delta))
      set_mac_volume(new_vol)


if __name__ == "__main__":
    local_ip = get_local_ip()
    print("==================================================")
    print(f" Pear Remote Server running at: http://{local_ip}:{config.PORT}")
    print("==================================================")

    # Enable port reuse before binding to prevent [Errno 48] on restart
    http.server.HTTPServer.allow_reuse_address = True

    while True:
        server = None
        try:
            server = http.server.HTTPServer(
                (config.HOST, config.PORT), PearRemoteHandler
            )
            # This will run continuously until a sleep/wake network event breaks it
            server.serve_forever() 
        except KeyboardInterrupt:
            print("\nServer stopped manually.")
            if server:
                server.server_close()
            break  # Exit the loop entirely if you press Ctrl+C
        except Exception as e:
            # Catch OS/socket errors caused by Mac sleep cycle
            print(f"\n[Network Interruption] Server crashed: {e}")
            print("Waiting 5 seconds for network to recover before restarting...")
            if server:
                try:
                    server.server_close() # Free up the port
                except Exception:
                    pass
            time.sleep(5) # Give macOS time to re-establish the network interface