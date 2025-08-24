from http.server import BaseHTTPRequestHandler
import json
from api._common import allow_options, get_origin

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        allow_options(self, origin=get_origin())
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", get_origin())
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "data": {"status": "ok"}}).encode("utf-8"))
