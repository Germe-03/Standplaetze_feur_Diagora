import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from BusinessLogic.WebAppManager import WebAppManager


UI_ROOT = PROJECT_ROOT / "UI"
DB_PATH = str(PROJECT_ROOT / "Databank" / "StandplaetzeDatabank.db")
APP_MANAGER = WebAppManager(DB_PATH)
STATIC_CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}


class RequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict | list, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, filepath: Path, content_type: str) -> None:
        if not filepath.exists():
            self.send_error(404, "File not found")
            return
        data = filepath.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw) if raw else {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            if path == "/api/dashboard":
                month = parse_qs(parsed.query).get("month", [None])[0]
                self._send_json(APP_MANAGER.get_dashboard(month))
                return
            if path == "/api/bookings":
                self._send_json(APP_MANAGER.get_bookings())
                return
            if path == "/api/stands":
                month = parse_qs(parsed.query).get("month", [None])[0]
                self._send_json(APP_MANAGER.get_stands(month))
                return
            if path == "/api/meta":
                self._send_json(APP_MANAGER.get_meta())
                return
            if path == "/api/campaigns":
                self._send_json(APP_MANAGER.get_campaigns())
                return
            if path == "/api/users":
                self._send_json(APP_MANAGER.get_users())
                return
        except Exception as error:
            self._send_json({"error": str(error)}, status=400)
            return

        if path == "/" or path == "/index.html":
            self._send_file(UI_ROOT / "index.html", "text/html; charset=utf-8")
            return

        # Serve UI static files (css/js/html) without hardcoding every filename.
        relative = path.lstrip("/")
        if relative and ".." not in relative and "/" not in relative:
            candidate = UI_ROOT / relative
            content_type = STATIC_CONTENT_TYPES.get(candidate.suffix.lower())
            if content_type and candidate.exists() and candidate.is_file():
                self._send_file(candidate, content_type)
                return

        self.send_error(404, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        payload = self._read_json_body()
        try:
            if path == "/api/bookings/validate-limits":
                booking_id_raw = payload.get("booking_id")
                booking_id = int(booking_id_raw) if booking_id_raw not in (None, "") else None
                self._send_json(APP_MANAGER.validate_booking_limits_only(payload, booking_id=booking_id), status=200)
                return
            if path == "/api/bookings/validate":
                booking_id_raw = payload.get("booking_id")
                booking_id = int(booking_id_raw) if booking_id_raw not in (None, "") else None
                self._send_json(APP_MANAGER.validate_booking(payload, booking_id=booking_id), status=200)
                return
            if path == "/api/bookings":
                self._send_json(APP_MANAGER.create_booking(payload), status=201)
                return
            if path == "/api/campaigns":
                self._send_json(APP_MANAGER.create_campaign(payload), status=201)
                return
            if path == "/api/users":
                self._send_json(APP_MANAGER.create_user(payload), status=201)
                return
            if path == "/api/stands":
                self._send_json(APP_MANAGER.create_stand(payload), status=201)
                return
            self.send_error(404, "Not found")
        except Exception as error:
            self._send_json({"error": str(error)}, status=400)

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path
        payload = self._read_json_body()
        try:
            if path.startswith("/api/bookings/"):
                booking_id = int(path.split("/")[-1])
                self._send_json(APP_MANAGER.update_booking(booking_id, payload), status=200)
                return
            if path.startswith("/api/stands/"):
                location_id = int(path.split("/")[-1])
                self._send_json(APP_MANAGER.update_stand(location_id, payload), status=200)
                return
            if path.startswith("/api/campaigns/"):
                campaign_id = int(path.split("/")[-1])
                self._send_json(APP_MANAGER.update_campaign(campaign_id, payload), status=200)
                return
            if path.startswith("/api/users/"):
                user_id = int(path.split("/")[-1])
                self._send_json(APP_MANAGER.update_user(user_id, payload), status=200)
                return
            self.send_error(404, "Not found")
        except Exception as error:
            self._send_json({"error": str(error)}, status=400)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path.startswith("/api/bookings/"):
                booking_id = int(path.split("/")[-1])
                self._send_json(APP_MANAGER.delete_booking(booking_id), status=200)
                return
            if path.startswith("/api/stands/"):
                location_id = int(path.split("/")[-1])
                self._send_json(APP_MANAGER.delete_stand(location_id), status=200)
                return
            if path.startswith("/api/campaigns/"):
                campaign_id = int(path.split("/")[-1])
                self._send_json(APP_MANAGER.delete_campaign(campaign_id), status=200)
                return
            if path.startswith("/api/users/"):
                user_id = int(path.split("/")[-1])
                self._send_json(APP_MANAGER.delete_user(user_id), status=200)
                return
            self.send_error(404, "Not found")
        except Exception as error:
            self._send_json({"error": str(error)}, status=400)


def run_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    run_server(args.host, args.port)
