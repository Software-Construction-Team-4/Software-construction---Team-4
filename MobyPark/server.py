import json
import os
import time
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


class RequestHandler(BaseHTTPRequestHandler):
    def _discord_send(self, content: str):
        if not DISCORD_WEBHOOK_URL:
            return
        try:
            data = json.dumps({"content": content}).encode("utf-8")
            req = urllib.request.Request(
                DISCORD_WEBHOOK_URL,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=3).read()
        except Exception:
            pass

    def log_message(self, format, *args):
        return
    
    def handle_one_request(self):
        self._start_time = time.time()
        super().handle_one_request()

    def send_response(self, code, message=None):
        self._status_code = code
        return super().send_response(code, message)

    def end_headers(self):
        try:
            status = getattr(self, "_status_code", "unknown")
            method = getattr(self, "command", "unknown")
            path = getattr(self, "path", "unknown")
            client_ip = self.client_address[0] if self.client_address else "unknown"
            duration_ms = int((time.time() - getattr(self, "_start_time", time.time())) * 1000)

            self._discord_send(
                f"📥 {method} {path} | {status} | {duration_ms}ms | ip={client_ip}"
            )
        except Exception:
            pass

        return super().end_headers()

    def do_POST(self):
        if self.path == "/register":
            from handlers.user import do_POST as handle_post
            handle_post(self)
            return
        elif self.path == "/login":
            from handlers.user import do_POST as handle_post
            handle_post(self)
            return
        elif self.path.startswith("/parking-lots"):
            from handlers.parkingLots import do_POST as parking_post
            parking_post(self)
            return
        elif self.path == "/reservations":
            from handlers.reservations import do_POST as handle_post
            handle_post(self)
            return
        elif self.path == "/vehicles":
            from handlers.vehicles import do_POST as handle_post
            handle_post(self)
            return
        elif self.path.startswith("/vehicles/"):
            from handlers.vehicles import do_POST as handle_post
            handle_post(self)
            return
        elif self.path.startswith("/payments"):
            from handlers.payments import do_POST as handle_post
            handle_post(self)
            return

        self.send_response(404)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"error":"Route not found"}')

    def do_PUT(self):
        if self.path.startswith("/parking-lots/"):
            from handlers.parkingLots import do_PUT as parking_put
            parking_put(self)
            return
        elif self.path == "/profile":
            from handlers.user import do_PUT as handle_put
            handle_put(self)
            return
        elif self.path.startswith("/reservations/"):
            from handlers.reservations import do_PUT as handle_put
            handle_put(self)
            return
        elif self.path.startswith("/vehicles/"):
            from handlers.vehicles import do_PUT as handle_put
            handle_put(self)
            return
        elif self.path.startswith("/payments/"):
            from handlers.payments import do_PUT as handle_put
            handle_put(self)
            return

        self.send_response(404)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"error":"Route not found"}')

    def do_DELETE(self):
        if self.path.startswith("/parking-lots/"):
            from handlers.parkingLots import do_DELETE as parking_delete
            parking_delete(self)
            return
        elif self.path.startswith("/reservations/"):
            from handlers.reservations import do_DELETE as handle_delete
            handle_delete(self)
            return
        elif self.path.startswith("/vehicles/"):
            from handlers.vehicles import do_DELETE as handle_delete
            handle_delete(self)
            return

        self.send_response(404)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"error":"Route not found"}')

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return

        if self.path == "/profile":
            from handlers.user import do_GET as handle_get
            handle_get(self)
            return
        elif self.path == "/logout":
            from handlers.user import do_GET as handle_get
            handle_get(self)
            return
        elif self.path == "/parking-lots" or self.path.startswith("/parking-lots/"):
            from handlers.parkingLots import do_GET as parking_get
            parking_get(self)
            return
        elif self.path.startswith("/reservations/"):
            from handlers.reservations import do_GET as handle_get
            handle_get(self)
            return
        elif self.path.startswith("/payments"):
            from handlers.payments import do_GET as handle_get
            handle_get(self)
            return
        elif self.path.startswith("/billing/"):
            from handlers.payments import do_GET_test as handle_get1
            handle_get1(self)
            return
        elif self.path == "/billing":
            from handlers.payments import do_GET as handle_get
            handle_get(self)
            return
        elif self.path.startswith("/vehicles"):
            from handlers.vehicles import do_GET as handle_get
            handle_get(self)
            return
        elif self.path.startswith("/history"):
            from handlers.history import do_GET as handle_get
            handle_get(self)
            return

        self.send_response(404)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"error":"Route not found"}')


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), RequestHandler)
    print("Server running on http://0.0.0.0:8000")
    server.serve_forever()
