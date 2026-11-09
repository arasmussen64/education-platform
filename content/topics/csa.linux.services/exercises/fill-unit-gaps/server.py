#!/usr/bin/env python3
"""shop-api: the shop's tiny web API, a stand-in for a real service.

It answers on the port named by the PORT environment variable:
  /         a greeting
  /health   "ok"
  /crash    the service exits with an error, the way a real bug would

Every request is logged to standard output. systemd sends that to the
journal; the "<6>" and "<3>" prefixes tell the journal a line's priority
(6 is info, 3 is err), so `journalctl -p err` can pick out the errors.
"""

import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


def log(line: str, error: bool = False) -> None:
    prefix = "<3>" if error else "<6>"
    print(prefix + line, flush=True)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/":
            self.reply(200, "shop-api ok\n")
        elif self.path == "/health":
            self.reply(200, "ok\n")
        elif self.path == "/crash":
            self.reply(500, "crashing now\n")
            log("FATAL: crash requested by a client", error=True)
            sys.stdout.flush()
            os._exit(1)
        else:
            self.reply(404, "no such page\n")

    def reply(self, status: int, body: str) -> None:
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        self.wfile.flush()
        log(f"GET {self.path} {status}")

    def log_message(self, format: str, *args: object) -> None:
        # The default would print its own access log line; ours is enough.
        pass


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    if not 1 <= port <= 65535:
        log(f"PORT {port} is out of range (1-65535), refusing to start", error=True)
        sys.exit(1)
    log(f"shop-api listening on port {port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
