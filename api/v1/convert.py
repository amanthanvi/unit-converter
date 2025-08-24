import json
from http.server import BaseHTTPRequestHandler
from converter import UnitConverter
from api._common import ok, error, allow_options, parse_body, json_log


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            data = parse_body(self)
            value_raw = data.get("value")
            from_unit = data.get("from_unit")
            to_unit = data.get("to_unit")

            # Validate params
            missing = []
            if value_raw is None:
                missing.append("value")
            if not from_unit:
                missing.append("from_unit")
            if not to_unit:
                missing.append("to_unit")

            if missing:
                error(
                    self,
                    400,
                    "missing_params",
                    "Required parameters are missing",
                    details={"missing": missing},
                    methods=["POST", "OPTIONS"],
                )
                return

            # Validate unit types
            if not isinstance(from_unit, str) or not isinstance(to_unit, str):
                error(
                    self,
                    400,
                    "invalid_params",
                    "from_unit and to_unit must be strings",
                    methods=["POST", "OPTIONS"],
                )
                return

            # Coerce value (via str() to satisfy static typing)
            try:
                value_f = float(str(value_raw))
            except (TypeError, ValueError):
                error(
                    self,
                    400,
                    "invalid_value",
                    f"Invalid value: {value_raw}",
                    methods=["POST", "OPTIONS"],
                )
                return

            json_log("info", "v1.convert.request", from_unit=from_unit, to_unit=to_unit)

            converter = UnitConverter()
            result = converter.convert(value_f, from_unit, to_unit)

            ok(self, result, methods=["POST", "OPTIONS"])

        except ValueError as ve:
            # Conversion errors (e.g., invalid units)
            error(self, 400, "invalid_conversion", str(ve), methods=["POST", "OPTIONS"])
        except Exception as e:
            json_log("error", "v1.convert.error", message=str(e))
            error(
                self,
                500,
                "internal_error",
                "Conversion failed",
                methods=["POST", "OPTIONS"],
            )

    def do_OPTIONS(self):
        allow_options(self, methods=["POST", "OPTIONS"])
