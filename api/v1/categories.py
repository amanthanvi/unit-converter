import json
from http.server import BaseHTTPRequestHandler
from converter import UnitConverter
from api._common import ok, error, allow_options, json_log


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            json_log("info", "v1.categories.request", path=self.path)
            converter = UnitConverter()
            categories = converter.get_categories()
            ok(self, categories, methods=["GET", "OPTIONS"])
        except Exception as e:
            json_log("error", "v1.categories.error", path=self.path, message=str(e))
            error(self, 500, "internal_error", "Failed to fetch categories")

    def do_OPTIONS(self):
        allow_options(self, methods=["GET", "OPTIONS"])
