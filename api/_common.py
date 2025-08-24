import os
import json
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional, List
import uuid


def resolve_origin(origin_header: Optional[str]) -> str:
    allowed = os.getenv("ALLOW_ORIGIN", "*").strip()
    if allowed == "*" or allowed == "":
        return "*"
    allowed_list = [x.strip() for x in allowed.split(",") if x.strip()]
    if origin_header and origin_header in allowed_list:
        return origin_header
    return allowed_list[0] if allowed_list else "null"


def request_id(handler) -> str:
    """Return a sanitized request id from headers or generate a new UUID.
    Strips CR, LF, and colon to prevent HTTP response splitting."""
    try:
        rid = handler.headers.get("X-Request-Id")
    except Exception:
        rid = None
    if rid:
        rid = rid.replace("\r", "").replace("\n", "").replace(":", "")
    return rid if rid else str(uuid.uuid4())


def _ensure_request_id(handler) -> str:
    rid = getattr(handler, "_request_id", None)
    if not rid:
        rid = request_id(handler)
        setattr(handler, "_request_id", rid)
    return rid


def _base_headers(origin: str, methods: Optional[List[str]] = None) -> Dict[str, str]:
    allow_methods = ", ".join(methods or ["GET", "POST", "OPTIONS"])
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": allow_methods,
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Request-Id",
        "Vary": "Origin",
        "Cache-Control": "no-store",
    }


def allow_options(handler, methods: Optional[List[str]] = None) -> None:
    origin = resolve_origin(handler.headers.get("Origin"))
    headers = _base_headers(origin, methods)
    handler.send_response(200)
    for k, v in headers.items():
        handler.send_header(k, v)
    handler.send_header("X-Request-Id", _ensure_request_id(handler))
    handler.end_headers()


def ok(
    handler,
    data: Any,
    origin: Optional[str] = None,
    status: int = 200,
    methods: Optional[List[str]] = None,
) -> None:
    o = origin or resolve_origin(handler.headers.get("Origin"))
    headers = _base_headers(o, methods)
    handler.send_response(status)
    for k, v in headers.items():
        handler.send_header(k, v)
    handler.send_header("X-Request-Id", _ensure_request_id(handler))
    handler.end_headers()
    handler.wfile.write(json.dumps({"ok": True, "data": data}).encode("utf-8"))


def error(
    handler,
    status: int,
    code: str,
    message: str,
    details: Optional[Any] = None,
    origin: Optional[str] = None,
    methods: Optional[List[str]] = None,
) -> None:
    o = origin or resolve_origin(handler.headers.get("Origin"))
    headers = _base_headers(o, methods)
    handler.send_response(status)
    for k, v in headers.items():
        handler.send_header(k, v)
    handler.send_header("X-Request-Id", _ensure_request_id(handler))
    handler.end_headers()
    payload = {"ok": False, "error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    handler.wfile.write(json.dumps(payload).encode("utf-8"))


def parse_body(handler) -> Dict[str, Any]:
    content_type = handler.headers.get("Content-Type") or ""
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        length = 0
    body_bytes = handler.rfile.read(length) if length > 0 else b""
    body_text = body_bytes.decode("utf-8") if body_bytes else ""
    if "application/json" in content_type:
        try:
            data = json.loads(body_text) if body_text else {}
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}
    # urlencoded fallback
    parsed = parse_qs(body_text) if body_text else {}
    return {k: (v[0] if isinstance(v, list) and v else v) for k, v in parsed.items()}


def query_params(handler) -> Dict[str, Any]:
    parsed = urlparse(handler.path)
    q = parse_qs(parsed.query)
    return {k: (v[0] if isinstance(v, list) and v else v) for k, v in q.items()}


def require_params(data: Dict[str, Any], required: List[str]) -> Optional[str]:
    missing = [k for k in required if data.get(k) in (None, "", [])]
    return ",".join(missing) if missing else None


def json_log(level: str, event: str, **fields: Any) -> None:
    rec = {"level": level, "event": event}
    rec.update(fields)
    try:
        print(json.dumps(rec), flush=True)
    except Exception:
        pass
