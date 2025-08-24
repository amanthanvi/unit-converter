import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from typing import List, Any
from converter import UnitConverter


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """
        Handle POST request to perform batch conversions.
        Expects JSON body: { "value": number, "from_unit": "unit", "to_units": ["unit1", "unit2", ...] }
        """
        try:
            # Read request body
            content_type = self.headers.get("Content-Type", "")
            try:
                content_length = int(self.headers.get("Content-Length", 0))
            except ValueError:
                content_length = 0
            body = (
                self.rfile.read(content_length).decode("utf-8")
                if content_length > 0
                else ""
            )

            value_raw: Any = None
            from_unit: Any = None
            to_units_raw: Any = None

            # Parse JSON if provided
            if "application/json" in content_type:
                try:
                    data = json.loads(body) if body else {}
                except json.JSONDecodeError:
                    data = {}
                value_raw = data.get("value")
                from_unit = data.get("from_unit")
                to_units_raw = data.get("to_units")
            else:
                # Fallback: parse URL-encoded
                parsed = parse_qs(body)
                value_raw = parsed.get("value", [None])[0]
                from_unit = parsed.get("from_unit", [None])[0]
                to_units_raw = parsed.get("to_units", [None])[0]

            # Normalize to_units to a list[str]
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

            # Validate required params presence
            if value_raw is None or not from_unit or len(to_units) == 0:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": "Missing required parameters"}).encode("utf-8")
                )
                return

            # Validate unit types
            if not isinstance(from_unit, str) or not all(
                isinstance(u, str) for u in to_units
            ):
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {
                            "error": "from_unit must be a string and to_units must be a list of strings"
                        }
                    ).encode("utf-8")
                )
                return

            # Coerce value to float
            try:
                value_f = float(str(value_raw))
            except (TypeError, ValueError):
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": f"Invalid value: {value_raw}"}).encode("utf-8")
                )
                return

            # Perform batch conversion
            converter = UnitConverter()
            conversions = converter.batch_convert(value_f, from_unit, to_units)

            # Respond
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(json.dumps({"conversions": conversions}).encode("utf-8"))

        except ValueError as e:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": "Batch conversion failed: " + str(e)}).encode(
                    "utf-8"
                )
            )

    def do_OPTIONS(self):
        """Handle OPTIONS request for CORS"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
