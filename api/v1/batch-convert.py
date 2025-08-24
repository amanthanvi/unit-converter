import json
from http.server import BaseHTTPRequestHandler
from typing import List, Any
from converter import UnitConverter
from api._common import ok, error, allow_options, parse_body, json_log


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            data = parse_body(self)
            value_raw: Any = data.get("value")
            from_unit: Any = data.get("from_unit")
            to_units_raw: Any = data.get("to_units")

            # Validate presence
            missing = []
            if value_raw is None:
                missing.append("value")
            if not from_unit:
                missing.append("from_unit")
            if to_units_raw in (None, "", []):
                missing.append("to_units")
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
            if not isinstance(from_unit, str):
                error(
                    self,
                    400,
                    "invalid_params",
                    "from_unit must be a string",
                    methods=["POST", "OPTIONS"],
                )
                return

            # Normalize to_units to List[str]
            to_units: List[str] = []
            if isinstance(to_units_raw, list):
                to_units = [str(u) for u in to_units_raw]
            elif isinstance(to_units_raw, str):
                # Try JSON array string first, else CSV
                try:
                    parsed_units = json.loads(to_units_raw)
                    if isinstance(parsed_units, list):
                        to_units = [str(u) for u in parsed_units]
                    else:
                        to_units = [str(parsed_units)]
                except Exception:
                    to_units = [u.strip() for u in to_units_raw.split(",") if u.strip()]

            if not to_units:
                error(
                    self,
                    400,
                    "invalid_params",
                    "to_units must be a non-empty list of strings",
                    methods=["POST", "OPTIONS"],
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
                    methods=["POST", "OPTIONS"],
                )
                return

            json_log(
                "info",
                "v1.batch_convert.request",
                from_unit=from_unit,
                to_units=len(to_units),
            )

            converter = UnitConverter()
            conversions = converter.batch_convert(value_f, from_unit, to_units)

            ok(self, {"conversions": conversions}, methods=["POST", "OPTIONS"])

        except ValueError as ve:
            error(self, 400, "invalid_request", str(ve), methods=["POST", "OPTIONS"])
        except Exception as e:
            json_log("error", "v1.batch_convert.error", message=str(e))
            error(
                self,
                500,
                "internal_error",
                "Batch conversion failed",
                methods=["POST", "OPTIONS"],
            )

    def do_OPTIONS(self):
        allow_options(self, methods=["POST", "OPTIONS"])
