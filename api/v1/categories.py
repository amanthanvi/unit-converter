from http.server import BaseHTTPRequestHandler
from converter import UnitConverter
from api._common import ok, error, allow_options, get_origin

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        allow_options(self, origin=get_origin())

    def do_GET(self):
        try:
            conv = UnitConverter()
            cats = conv.get_categories()
            ok(self, cats, origin=get_origin())
        except Exception as e:
            error(self, 500, "internal_error", "Failed to fetch categories", details=str(e), origin=get_origin())
