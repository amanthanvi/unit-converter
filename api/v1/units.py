import json
from http.server import BaseHTTPRequestHandler
from converter import UnitConverter
from api._common import with_json, allow_options


class handler(BaseHTTPRequestHandler):
    @with_json(
        required=["category"],
        use_query=True,
        methods=["GET", "OPTIONS"],
        event="v1.units",
    )
    def do_GET(self, data):
        category = data.get("category")
        converter = UnitConverter()
        units = converter.get_units(category)
        if not units:
            raise ValueError(f"Unknown category: {category}")
        return units

    def do_OPTIONS(self):
        allow_options(self, methods=["GET", "OPTIONS"])
