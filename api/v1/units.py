from http.server import BaseHTTPRequestHandler
from converter import UnitConverter
from api._common import ok, error, allow_options, get_origin, query_params, begin


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        allow_options(self, origin=get_origin())

    def do_GET(self):
        begin(self)
        try:
            qp = query_params(self)
            category = qp.get("category")
            if not category:
                return error(
                    self,
                    400,
                    "missing_params",
                    "Query parameter category is required",
                    origin=get_origin(),
                )

            conv = UnitConverter()
            units = conv.get_units(category)
            if not units:
                return error(self, 404, "invalid_category", "Invalid category", origin=get_origin())

            ok(self, units, origin=get_origin())
        except Exception as e:
            error(
                self,
                500,
                "internal_error",
                "Failed to fetch units",
                details=str(e),
                origin=get_origin(),
            )
