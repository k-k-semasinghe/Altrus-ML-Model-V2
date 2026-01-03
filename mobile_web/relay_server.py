from __future__ import annotations

import json
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer


class RelayHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/send":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
            target_host = data["target_host"]
            target_port = int(data["target_port"])
            payload = data["payload"]
        except (KeyError, ValueError, json.JSONDecodeError):
            self.send_response(400)
            self.end_headers()
            return

        message = json.dumps(payload).encode("utf-8")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(message, (target_host, target_port))

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")


def main() -> None:
    server = HTTPServer(("0.0.0.0", 8080), RelayHandler)
    print("Relay server listening on http://0.0.0.0:8080/send")
    server.serve_forever()


if __name__ == "__main__":
    main()
