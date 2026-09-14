"""HTTP routes for the remote UI and control API."""

from __future__ import annotations

import http.server
import json
import urllib.parse

import controls
import macos_control
import pear_client
import templating


class PearRemoteHandler(http.server.BaseHTTPRequestHandler):
    """Serve the UI and expose status/control endpoints."""

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_body(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
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
            info["volume"] = macos_control.get_system_volume()
            self._send_json(info)
        elif path.startswith("/control/"):
            action = path.rsplit("/", 1)[-1]
            self._send_text("OK" if controls.dispatch(action) else f"Unknown action: {action}", 200 if controls.dispatch(action) else 400)
        else:
            self._send_body(templating.render_index_html().encode("utf-8"), "text/html; charset=utf-8")
