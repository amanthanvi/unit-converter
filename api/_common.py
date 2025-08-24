import json
import os
import uuid
from urllib.parse import parse_qs, urlparse

def get_origin():
    return os.environ.get("ALLOW_ORIGIN", "*")

def _headers(origin=None):
    origin = origin or get_origin()
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-Request-Id"
    }

def allow_options(handler, origin=None):
    handler.send_response(200)
    for k, v in _headers(origin).items():
        handler.send_header(k, v)
    handler.end_headers()

def request_id(handler):
    rid = handler.headers.get("X-Request-Id")
    return rid if rid else str(uuid.uuid4())

def ok(handler, data, status=200, origin=None):
    body = json.dumps({"ok": True, "data": data})
    handler.send_response(status)
    for k, v in _headers(origin).items():
        handler.send_header(k, v)
    handler.send_header("X-Request-Id", request_id(handler))
    handler.end_headers()
    handler.wfile.write(body.encode("utf-8"))

def error(handler, status, code, message, details=None, origin=None):
    body = json.dumps({"ok": False, "error": {"code": code, "message": message, "details": details}})
    handler.send_response(status)
    for k, v in _headers(origin).items():
        handler.send_header(k, v)
    handler.send_header("X-Request-Id", request_id(handler))
    handler.end_headers()
    handler.wfile.write(body.encode("utf-8"))

def parse_body(handler):
    ctype = handler.headers.get("Content-Type", "")
    clen = int(handler.headers.get("Content-Length", "0") or 0)
    raw = handler.rfile.read(clen).decode("utf-8") if clen > 0 else ""
    if "application/json" in ctype:
        try:
            return json.loads(raw), None
        except Exception as e:
            return None, f"Invalid JSON payload: {e}"
    elif "application/x-www-form-urlencoded" in ctype or raw:
        try:
            data = parse_qs(raw)
            return {k: v[0] for k, v in data.items()}, None
        except Exception as e:
            return None, f"Invalid form payload: {e}"
    else:
        return {}, None

def query_params(handler):
    parsed = urlparse(handler.path)
    q = parse_qs(parsed.query)
    return {k: v[0] for k, v in q.items()}
