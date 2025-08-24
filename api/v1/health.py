import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from api._common import ok, error, allow_options, json_log


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            now = datetime.now(timezone.utc).isoformat()
            payload = {
                "status": "ok",
                "version": "v1",
                "time": now,
                "services": {"api": "ok"},
            }
            json_log("info", "v1.health.request", time=now)
            ok(self, payload, methods=["GET", "OPTIONS"])
        except Exception as e:
            json_log("error", "v1.health.error", message=str(e))
            error(
                self,
                500,
                "internal_error",
                "Health check failed",
                methods=["GET", "OPTIONS"],
            )

    def do_OPTIONS(self):
        allow_options(self, methods=["GET", "OPTIONS"])
