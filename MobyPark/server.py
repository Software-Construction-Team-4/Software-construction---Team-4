import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from session_manager import get_session



class RequestHandler(BaseHTTPRequestHandler):
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

    def do_GET(self):
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

        elif self.path.endswith("/history"):
            from handlers.history import do_GET as handle_get
            handle_get(self)
            return
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Route not found")
            return


server = HTTPServer(("localhost", 8000), RequestHandler)
print("Server running on http://localhost:8000")
server.serve_forever()
