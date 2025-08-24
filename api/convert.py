import json
import cgi
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from converter import UnitConverter
from api._common import resolve_origin


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """
        Handle POST request to convert units.
        """
        try:
            # Get content type
            content_type = self.headers.get("Content-Type", "")

            # Initialize variables
            value = None
            from_unit = None
            to_unit = None

            if "multipart/form-data" in content_type:
                # Parse multipart form data
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={"REQUEST_METHOD": "POST"},
                )
                value = form.getvalue("value")
                from_unit = form.getvalue("from_unit")
                to_unit = form.getvalue("to_unit")
            else:
                # Read request body
                content_length = int(self.headers.get("Content-Length", 0))
                body = (
                    self.rfile.read(content_length).decode("utf-8")
                    if content_length > 0
                    else ""
                )

                # Try to parse as JSON first
                if "application/json" in content_type:
                    try:
                        data = json.loads(body)
                        value = data.get("value")
                        from_unit = data.get("from_unit")
                        to_unit = data.get("to_unit")
                    except (json.JSONDecodeError, ValueError):
                        pass
                else:
                    # Fall back to URL-encoded form data parsing
                    parsed_data = parse_qs(body)
                    value = (
                        parsed_data.get("value", [None])[0]
                        if "value" in parsed_data
                        else None
                    )
                    from_unit = (
                        parsed_data.get("from_unit", [None])[0]
                        if "from_unit" in parsed_data
                        else None
                    )
                    to_unit = (
                        parsed_data.get("to_unit", [None])[0]
                        if "to_unit" in parsed_data
                        else None
                    )

            if not all([value is not None, from_unit, to_unit]):
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {
                            "error": f"Missing required parameters. Got value={value}, from_unit={from_unit}, to_unit={to_unit}"
                        }
                    ).encode("utf-8")
                )
                return

            # Convert value to float
            try:
                value = float(value)
            except (TypeError, ValueError):
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": f"Invalid value: {value}"}).encode("utf-8")
                )
                return

            # Initialize converter
            converter = UnitConverter()

            # Perform conversion
            result = converter.convert(value, from_unit, to_unit)

            # Send success response
            origin = resolve_origin(self.headers.get("Origin"))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header(
                "Access-Control-Allow-Headers",
                "Content-Type, Authorization, X-Request-Id",
            )
            self.send_header("Vary", "Origin")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))

        except ValueError as e:
            origin = resolve_origin(self.headers.get("Origin"))
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

        except Exception as e:
            origin = resolve_origin(self.headers.get("Origin"))
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": "Conversion failed: " + str(e)}).encode("utf-8")
            )

    def do_OPTIONS(self):
        """Handle OPTIONS request for CORS"""
        origin = resolve_origin(self.headers.get("Origin"))
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers", "Content-Type, Authorization, X-Request-Id"
        )
        self.send_header("Vary", "Origin")
        self.end_headers()
