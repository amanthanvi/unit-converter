import json
from http.server import BaseHTTPRequestHandler
from converter import UnitConverter
from api._common import ok, error, allow_options, query_params, json_log


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            qp = query_params(self)
            category = qp.get("category") or None
            if not category:
                error(
                    self,
                    400,
                    "missing_params",
                    "category is required",
                    details={"missing": ["category"]},
                )
                return

            json_log("info", "v1.units.request", path=self.path, category=category)
            converter = UnitConverter()
            units = converter.get_units(category)

            if not units:
                error(self, 404, "invalid_category", f"Unknown category: {category}")
                return

            ok(self, units, methods=["GET", "OPTIONS"])
        except Exception as e:
            json_log("error", "v1.units.error", path=self.path, message=str(e))
            error(self, 500, "internal_error", "Failed to fetch units")

    def do_OPTIONS(self):
        allow_options(self, methods=["GET", "OPTIONS"])
