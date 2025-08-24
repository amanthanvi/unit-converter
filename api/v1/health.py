from http.server import BaseHTTPRequestHandler
from api._common import ok, allow_options, get_origin

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        allow_options(self, origin=get_origin())
    def do_GET(self):
        ok(self, {"status": "ok"}, origin=get_origin())
