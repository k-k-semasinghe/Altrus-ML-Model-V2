from __future__ import annotations

import json
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).parent


class RelayHandler(BaseHTTPRequestHandler):
    def _send_text(self, status: int, body: str, content_type: str = "text/plain") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            content = (ROOT / "index.html").read_text(encoding="utf-8")
            self._send_text(200, content, "text/html; charset=utf-8")
            return
        if self.path == "/send":
            self._send_text(200, "Relay expects POST requests to /send.")
            return
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        self._send_text(404, "Not found.")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/send":
            self._send_text(404, "Not found.")
            return

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
            target_host = data["target_host"]
            target_port = int(data["target_port"])
            payload = data["payload"]
        except (KeyError, ValueError, json.JSONDecodeError):
            self._send_text(400, "Invalid payload.")
            return

        message = json.dumps(payload).encode("utf-8")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(message, (target_host, target_port))

        self._send_text(200, "ok")


def main() -> None:
    server = HTTPServer(("0.0.0.0", 8080), RelayHandler)
    print("Relay server listening on http://0.0.0.0:8080/send")
    server.serve_forever()


if __name__ == "__main__":
    main()
