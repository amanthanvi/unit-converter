import json
import os
import uuid
import time
from urllib.parse import parse_qs, urlparse


def get_origin():
    return os.environ.get("ALLOW_ORIGIN", "*")


def _headers(origin=None):
    origin = origin or get_origin()
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-Request-Id",
    }


def allow_options(handler, origin=None):
    handler.send_response(200)
    for k, v in _headers(origin).items():
        handler.send_header(k, v)
    handler.end_headers()


def request_id(handler):
    try:
        rid = handler.headers.get("X-Request-Id")
    except Exception:
        rid = None
    return rid if rid else str(uuid.uuid4())


def begin(handler):
    """Call at the start of each request handler to start latency timer."""
    try:
        handler._start_ns = time.time_ns()
    except Exception:
        handler._start_ns = None


def _latency_ms(handler):
    try:
        if getattr(handler, "_start_ns", None) is None:
            return None
        return round((time.time_ns() - handler._start_ns) / 1_000_000.0, 2)
    except Exception:
        return None


def _log(handler, level, message, status=None):
    entry = {
        "ts": int(time.time() * 1000),
        "level": level,
        "request_id": request_id(handler),
        "method": getattr(handler, "command", None),
        "path": getattr(handler, "path", None),
        "status": status,
        "latency_ms": _latency_ms(handler),
        "message": message,
    }
    try:
        print(json.dumps(entry), flush=True)
    except Exception:
        pass


def ok(handler, data, status=200, origin=None):
    body = json.dumps({"ok": True, "data": data})
    handler.send_response(status)
    for k, v in _headers(origin).items():
        handler.send_header(k, v)
    rid = request_id(handler)
    handler.send_header("X-Request-Id", rid)
    handler.end_headers()
    handler.wfile.write(body.encode("utf-8"))
    _log(handler, "info", "request.ok", status=status)


def error(handler, status, code, message, details=None, origin=None):
    body = json.dumps(
        {"ok": False, "error": {"code": code, "message": message, "details": details}}
    )
    handler.send_response(status)
    for k, v in _headers(origin).items():
        handler.send_header(k, v)
    rid = request_id(handler)
    handler.send_header("X-Request-Id", rid)
    handler.end_headers()
    handler.wfile.write(body.encode("utf-8"))
    _log(handler, "error", f"request.error:{code}", status=status)


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
