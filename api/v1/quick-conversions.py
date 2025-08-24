from http.server import BaseHTTPRequestHandler
from converter import UnitConverter
from api._common import ok, error, allow_options, get_origin, query_params

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        allow_options(self, origin=get_origin())

    def do_GET(self):
        try:
            qp = query_params(self)
            value_str = qp.get("value")
            unit = qp.get("unit")

            if value_str is None or not unit:
                return error(self, 400, "missing_params", "Required parameters are value and unit", origin=get_origin())

            try:
                value = float(value_str)
            except Exception:
                return error(self, 400, "invalid_value", f"Invalid value: {value_str}", origin=get_origin())

            conv = UnitConverter()
            conversions = conv.get_quick_conversions(value, unit)
            ok(self, conversions, origin=get_origin())
        except ValueError as e:
            error(self, 400, "validation_error", str(e), origin=get_origin())
        except Exception as e:
            error(self, 500, "internal_error", "Failed to get quick conversions", details=str(e), origin=get_origin())
