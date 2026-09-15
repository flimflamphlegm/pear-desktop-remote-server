"""HTTP routes for the remote UI and control API."""


from __future__ import annotations


import http.server
import json
import urllib.parse



from . import controls, macos_control, pear_client, templating, config



class PearRemoteHandler(http.server.BaseHTTPRequestHandler):
    """Serve the UI and expose status/control endpoints."""



    def log_message(self, format: str, *args: object) -> None:
        return



    def _send_body(self, body: bytes, content_type: str, status: int = 200, cache_control: str | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if cache_control:
            self.send_header("Cache-Control", cache_control)
        self.end_headers()
        self.wfile.write(body)



    def _send_json(self, data: dict, status: int = 200) -> None:
        self._send_body(json.dumps(data).encode("utf-8"), "application/json", status)



    def _send_text(self, text: str, status: int = 200) -> None:
        self._send_body(text.encode("utf-8"), "text/plain; charset=utf-8", status)



    def do_GET(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        elif path == "/api/status":
            info = pear_client.fetch_now_playing()
            # Only poll volume if not in minimal mode
            if not config.MINIMAL_MODE:
                info["volume"] = macos_control.get_system_volume()
            else:
                info["volume"] = 50  # Default value in minimal mode
            self._send_json(info)
        elif path == "/api/v1/shuffle":
            # GET /api/v1/shuffle - get shuffle state
            state = pear_client.get_shuffle_state()
            self._send_json({"state": state})
        elif path == "/api/v1/repeat-mode":
            # GET /api/v1/repeat-mode - get repeat mode
            mode = pear_client.get_repeat_mode()
            self._send_json({"mode": mode})
        elif path.startswith("/control/"):
            action = path.rsplit("/", 1)[-1]
            recognized = controls.dispatch(action)
            self._send_text("OK" if recognized else f"Unknown action: {action}", 200 if recognized else 400)
        else:
            self._send_body(templating.render_index_html().encode("utf-8"), "text/html; charset=utf-8")



    def do_POST(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        if path == "/api/v1/shuffle":
            # POST /api/v1/shuffle - toggle shuffle
            success = pear_client.toggle_shuffle()
            if success:
                self.send_response(204)
                self.end_headers()
            else:
                self._send_text("Failed to toggle shuffle", 500)
        elif path == "/api/v1/switch-repeat":
            # POST /api/v1/switch-repeat - switch repeat mode
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length > 0 else b"{}"
            try:
                data = json.loads(body.decode("utf-8"))
                iteration = int(data.get("iteration", 0))
            except (json.JSONDecodeError, ValueError, TypeError):
                iteration = 0
            success = pear_client.switch_repeat(iteration)
            if success:
                self.send_response(204)
                self.end_headers()
            else:
                self._send_text("Failed to switch repeat mode", 500)
        else:
            self.send_response(404)
            self.end_headers()
