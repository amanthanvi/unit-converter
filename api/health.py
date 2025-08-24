import json
from http.server import BaseHTTPRequestHandler
from api._common import ok, error, allow_options, resolve_origin


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Standardized minimal payload; envelope handled by ok(...)
            payload = {"status": "ok"}
            ok(self, payload, methods=["GET", "OPTIONS"])
        except Exception as e:
            error(
                self,
                500,
                "internal_error",
                "Health check failed",
                methods=["GET", "OPTIONS"],
            )

    def do_OPTIONS(self):
        allow_options(self, methods=["GET", "OPTIONS"])
