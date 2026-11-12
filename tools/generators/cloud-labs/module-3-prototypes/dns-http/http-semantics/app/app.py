# A tiny shop backend: each path sets the headers the scenario needs.
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import time, hashlib
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        p = self.path
        user = self.headers.get("Cookie", "session=anon").split("=")[-1]
        if p.startswith("/account"):
            body = f"account page for {user} at {time.time():.3f}\n"
        elif p.startswith("/assets/"):
            body = "console.log(1)\n"
        else:
            body = f"home at {time.time():.3f}\n"
        etag = "\"" + hashlib.sha256(body.encode()).hexdigest()[:16] + "\""
        if self.headers.get("If-None-Match") == etag:
            self.send_response(304); self.send_header("ETag", etag); self.end_headers(); return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain"); self.send_header("ETag", etag)
        self.end_headers(); self.wfile.write(body.encode())
    def log_message(self, *a): pass
ThreadingHTTPServer(("127.0.0.1", 8080), H).serve_forever()
