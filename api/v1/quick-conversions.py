import json
from http.server import BaseHTTPRequestHandler
from converter import UnitConverter
from api._common import ok, error, allow_options, query_params, json_log


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            qp = query_params(self)
            value_raw = qp.get("value")
            unit = qp.get("unit")

            # Validate params
            missing = []
            if value_raw is None:
                missing.append("value")
            if not unit:
                missing.append("unit")
            if missing:
                error(
                    self,
                    400,
                    "missing_params",
                    "Required parameters are missing",
                    details={"missing": missing},
                    methods=["GET", "OPTIONS"],
                )
                return

            # Coerce value
            try:
                value_f = float(str(value_raw))
            except (TypeError, ValueError):
                error(
                    self,
                    400,
                    "invalid_value",
                    f"Invalid value: {value_raw}",
                    methods=["GET", "OPTIONS"],
                )
                return

            # Ensure unit is a string for static typing and downstream usage
            unit_str: str = str(unit)

            json_log("info", "v1.quick_conversions.request", unit=unit_str)

            converter = UnitConverter()
            conversions = converter.get_quick_conversions(value_f, unit_str)

            ok(self, conversions, methods=["GET", "OPTIONS"])

        except ValueError as ve:
            error(self, 400, "invalid_request", str(ve), methods=["GET", "OPTIONS"])
        except Exception as e:
            json_log("error", "v1.quick_conversions.error", message=str(e))
            error(
                self,
                500,
                "internal_error",
                "Failed to get quick conversions",
                methods=["GET", "OPTIONS"],
            )

    def do_OPTIONS(self):
        allow_options(self, methods=["GET", "OPTIONS"])
