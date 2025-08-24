import json
from http.server import BaseHTTPRequestHandler
from converter import UnitConverter
from api._common import with_json, allow_options, json_log


class handler(BaseHTTPRequestHandler):
    @with_json(
        required=["value", "unit"],
        use_query=True,
        methods=["GET", "OPTIONS"],
        event="v1.quick_conversions",
    )
    def do_GET(self, data):
        value_raw = data.get("value")
        unit_str = str(data.get("unit"))
        try:
            value_f = float(str(value_raw))
        except (TypeError, ValueError):
            raise ValueError(f"Invalid value: {value_raw}")
        json_log("info", "v1.quick_conversions.request", unit=unit_str)
        converter = UnitConverter()
        conversions = converter.get_quick_conversions(value_f, unit_str)
        # Include currency rates metadata in envelope meta when applicable
        # Determine if the source unit is in the currency category
        category = None
        for cat_id, cat_data in converter.categories.items():
            if unit_str in cat_data.get("units", {}):
                category = cat_id
                break
        if category == "currency":
            meta = getattr(converter, "_currency_meta", None)
            resp = {"result": conversions}
            if isinstance(meta, dict):
                resp["meta"] = dict(meta)
            return resp
        return {"result": conversions}

    def do_OPTIONS(self):
        allow_options(self, methods=["GET", "OPTIONS"])
