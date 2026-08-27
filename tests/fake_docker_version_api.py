from __future__ import annotations

import socketserver
import sys
from pathlib import Path


class Handler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        request_line = self.rfile.readline().decode("ascii", errors="replace").strip()
        while True:
            line = self.rfile.readline()
            if line in {b"", b"\r\n", b"\n"}:
                break

        parts = request_line.split()
        path = parts[1] if len(parts) >= 2 else ""
        if path == "/version":
            body = b'{"ApiVersion":"1.44","MinAPIVersion":"1.24","Version":"26.0.0"}'
            status = b"200 OK"
            content_type = b"application/json"
        elif path == "/_ping":
            body = b"OK"
            status = b"200 OK"
            content_type = b"text/plain"
        else:
            body = b"not found"
            status = b"404 Not Found"
            content_type = b"text/plain"

        self.wfile.write(b"HTTP/1.1 " + status + b"\r\n")
        self.wfile.write(b"Content-Type: " + content_type + b"\r\n")
        self.wfile.write(f"Content-Length: {len(body)}\r\n".encode())
        self.wfile.write(b"Connection: close\r\n\r\n")
        self.wfile.write(body)


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: fake_docker_version_api.py SOCKET_PATH")
    socket_path = Path(sys.argv[1])
    socket_path.unlink(missing_ok=True)
    with Server(str(socket_path), Handler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
