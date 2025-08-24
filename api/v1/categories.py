import json
from http.server import BaseHTTPRequestHandler
from converter import UnitConverter
from api._common import with_json, allow_options


class handler(BaseHTTPRequestHandler):
    @with_json(use_query=True, methods=["GET", "OPTIONS"], event="v1.categories")
    def do_GET(self, data):
        converter = UnitConverter()
        categories = converter.get_categories()
        return categories

    def do_OPTIONS(self):
        allow_options(self, methods=["GET", "OPTIONS"])
