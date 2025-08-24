import json
from http.server import BaseHTTPRequestHandler
from converter import UnitConverter
from api._common import resolve_origin


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request for categories"""
        try:
            # Initialize converter
            converter = UnitConverter()

            # Get categories
            categories = converter.get_categories()

            # Send response
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
            self.wfile.write(json.dumps(categories).encode("utf-8"))

        except Exception as e:
            # Send error response
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
