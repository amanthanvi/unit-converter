import os
import json
from http.server import BaseHTTPRequestHandler
from converter import UnitConverter
from api._common import with_json, allow_options


class handler(BaseHTTPRequestHandler):
    @with_json(
        required=["value", "from_unit", "to_unit"],
        use_query=False,
        methods=["POST", "OPTIONS"],
        event="v1.convert",
    )
    def do_POST(self, data):
        value_raw = data.get("value")
        from_unit = data.get("from_unit")
        to_unit = data.get("to_unit")

        # Coerce numeric value
        try:
            value_f = float(str(value_raw))
        except (TypeError, ValueError):
            raise ValueError(f"Invalid value: {value_raw}")

        converter = UnitConverter()
        result = converter.convert(value_f, from_unit, to_unit)

        # Meta: indicate currency fallback usage when forced/disabled live
        meta = {}
        try:
            if isinstance(result, dict) and result.get("category") == "currency":
                forced = os.getenv("CURRENCY_FALLBACK_ONLY", "").strip() == "1"
                disabled = os.getenv("DISABLE_LIVE_FOREX", "").strip() == "1"
                meta["currency"] = {
                    "source": "fallback" if (forced or disabled) else "live"
                }
        except Exception:
            pass

        resp = dict(result)
        if meta:
            resp["meta"] = meta
        return resp

    def do_OPTIONS(self):
        allow_options(self, methods=["POST", "OPTIONS"])
