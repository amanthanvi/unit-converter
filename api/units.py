import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from converter import UnitConverter
from api._common import resolve_origin


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Handle GET request to get units for a specific category.
        """
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            category = query_params.get("category", [None])[0]

            if not category:
                origin = resolve_origin(self.headers.get("Origin"))
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": "Category parameter is required"}).encode(
                        "utf-8"
                    )
                )
                return

            # Initialize converter
            converter = UnitConverter()

            # Get units
            units = converter.get_units(category)

            if not units:
                origin = resolve_origin(self.headers.get("Origin"))
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": "Invalid category"}).encode("utf-8")
                )
                return

            # Send success response
            origin = resolve_origin(self.headers.get("Origin"))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header(
                "Access-Control-Allow-Headers",
                "Content-Type, Authorization, X-Request-Id",
            )
            self.send_header("Vary", "Origin")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(json.dumps(units).encode("utf-8"))

        except Exception as e:
            origin = resolve_origin(self.headers.get("Origin"))
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def do_OPTIONS(self):
        """Handle OPTIONS request for CORS"""
        origin = resolve_origin(self.headers.get("Origin"))
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers", "Content-Type, Authorization, X-Request-Id"
        )
        self.send_header("Vary", "Origin")
        self.end_headers()
