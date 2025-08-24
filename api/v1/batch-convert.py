from http.server import BaseHTTPRequestHandler
from converter import UnitConverter
from api._common import ok, error, parse_body, allow_options, get_origin, begin


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        allow_options(self, origin=get_origin())

    def do_POST(self):
        begin(self)
        try:
            payload, perr = parse_body(self)
            if perr is not None:
                return error(self, 400, "bad_request", perr, origin=get_origin())

            value = (payload or {}).get("value")
            from_unit = (payload or {}).get("from_unit")
            to_units = (payload or {}).get("to_units") or []

            if (
                value is None
                or not from_unit
                or not isinstance(to_units, list)
                or len(to_units) == 0
            ):
                return error(
                    self,
                    400,
                    "missing_params",
                    "Required parameters are value, from_unit, to_units[list]",
                    origin=get_origin(),
                )

            try:
                value = float(value)
            except Exception:
                return error(
                    self, 400, "invalid_value", f"Invalid value: {value}", origin=get_origin()
                )

            conv = UnitConverter()
            results = conv.batch_convert(value, from_unit, to_units)
            ok(self, {"conversions": results}, origin=get_origin())
        except ValueError as e:
            error(self, 400, "validation_error", str(e), origin=get_origin())
        except Exception as e:
            error(
                self,
                500,
                "internal_error",
                "Batch conversion failed",
                details=str(e),
                origin=get_origin(),
            )
