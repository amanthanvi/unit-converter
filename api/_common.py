import os
import json
import re
import uuid
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional, List
from functools import wraps


def resolve_origin(origin_header: Optional[str]) -> str:
    allowed = os.getenv("ALLOW_ORIGIN", "*").strip()
    if allowed == "*" or allowed == "":
        return "*"
    allowed_list = [x.strip() for x in allowed.split(",") if x.strip()]
    if origin_header and origin_header in allowed_list:
        return origin_header
    return allowed_list[0] if allowed_list else "null"


# RFC 7230 tchar set => token-safe header value
# Allowed: ! # $ % & ' * + - . ^ _ ` | ~ and ALPHA / DIGIT
_TCHAR_PATTERN = r"[^!#$%&'*+\-.^_`|~0-9A-Za-z]"


def _sanitize_token(value: str, max_len: int = 128) -> str:
    """Filter a string to an RFC 7230 token-safe value and cap length."""
    if not isinstance(value, str):
        try:
            value = str(value)
        except Exception:
            return ""
    # Remove any disallowed characters (including spaces and control chars)
    safe = re.sub(_TCHAR_PATTERN, "", value)
    return safe[:max_len]


def request_id(handler) -> str:
    """Return an RFC 7230–safe request id from headers or generate a new UUID."""
    try:
        rid = handler.headers.get("X-Request-Id")
    except Exception:
        rid = None
    if rid:
        rid = _sanitize_token(rid)
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
        "Access-Control-Expose-Headers": "X-Request-Id",
        "Vary": "Origin",
        "Cache-Control": "no-store",
    }


def allow_options(handler, methods: Optional[List[str]] = None) -> None:
    origin = resolve_origin(handler.headers.get("Origin"))
    headers = _base_headers(origin, methods)
    handler.send_response(200)
    for k, v in headers.items():
        handler.send_header(k, v)
    rid = _ensure_request_id(handler)
    handler.send_header("X-Request-Id", rid)
    handler.end_headers()
    json_log(
        "info",
        "response",
        request_id=rid,
        method=getattr(handler, "command", None),
        path=getattr(handler, "path", None),
        status=200,
    )


def _write_json(
    handler, status: int, headers: Dict[str, str], payload: Dict[str, Any]
) -> None:
    handler.send_response(status)
    for k, v in headers.items():
        handler.send_header(k, v)
    rid = _ensure_request_id(handler)
    handler.send_header("X-Request-Id", rid)
    handler.end_headers()
    # Attach request_id to meta
    if "meta" not in payload or not isinstance(payload["meta"], dict):
        payload["meta"] = {}
    payload["meta"]["request_id"] = rid
    handler.wfile.write(json.dumps(payload).encode("utf-8"))


def ok(
    handler,
    data: Any,
    origin: Optional[str] = None,
    status: int = 200,
    methods: Optional[List[str]] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    o = origin or resolve_origin(handler.headers.get("Origin"))
    headers = _base_headers(o, methods)

    # Build uniform envelope
    payload: Dict[str, Any] = {"ok": True}
    meta_block: Dict[str, Any] = {}

    # If the handler already returned a dict with conversion-style keys, lift them
    if isinstance(data, dict):
        # Extract meta from data if present
        if "meta" in data and isinstance(data["meta"], dict):
            meta_block.update(data["meta"])
            data = {k: v for k, v in data.items() if k != "meta"}
        payload.update(data)
    else:
        payload["result"] = data

    if meta:
        meta_block.update(meta)
    if meta_block:
        payload["meta"] = meta_block

    _write_json(handler, status, headers, payload)
    json_log(
        "info",
        "response",
        method=getattr(handler, "command", None),
        path=getattr(handler, "path", None),
        status=status,
    )


def error(
    handler,
    status: int,
    code: str,
    message: str,
    details: Optional[Any] = None,
    origin: Optional[str] = None,
    methods: Optional[List[str]] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    o = origin or resolve_origin(handler.headers.get("Origin"))
    headers = _base_headers(o, methods)
    payload: Dict[str, Any] = {
        "ok": False,
        "error": {"code": code, "message": message},
    }
    if details is not None:
        payload["error"]["details"] = details
    if meta:
        payload["meta"] = dict(meta)

    _write_json(handler, status, headers, payload)
    json_log(
        "error" if status >= 400 else "info",
        "response",
        method=getattr(handler, "command", None),
        path=getattr(handler, "path", None),
        status=status,
        code=code,
    )


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


def with_json(
    required: Optional[List[str]] = None,
    use_query: bool = False,
    methods: Optional[List[str]] = None,
    event: Optional[str] = None,
):
    """
    Decorator for BaseHTTPRequestHandler methods (do_GET/do_POST) that:
      - extracts input (query or body)
      - validates required fields
      - emits standardized ok()/error() envelopes with CORS and sanitized X-Request-Id
      - logs structured request/response events
    """
    req = required or []

    def decorator(func):
        @wraps(func)
        def wrapper(handler_self, *args, **kwargs):
            origin = resolve_origin(handler_self.headers.get("Origin"))
            # Extract data
            try:
                data = (
                    query_params(handler_self)
                    if use_query
                    else parse_body(handler_self)
                )
                if not isinstance(data, dict):
                    data = {}
            except Exception as e:
                json_log("error", f"{event or 'handler'}.parse_error", message=str(e))
                return error(
                    handler_self,
                    400,
                    "invalid_body",
                    "Failed to parse request body",
                    origin=origin,
                    methods=methods,
                )

            # Validate required fields
            missing = [k for k in req if data.get(k) in (None, "", [])]
            if missing:
                return error(
                    handler_self,
                    400,
                    "missing_params",
                    "Required parameters are missing",
                    details={"missing": missing},
                    origin=origin,
                    methods=methods,
                )

            # Process
            try:
                json_log(
                    "info",
                    f"{event or 'handler'}.request",
                    method=getattr(handler_self, "command", None),
                    path=getattr(handler_self, "path", None),
                )
                result = func(handler_self, data, *args, **kwargs)
                return ok(handler_self, result, origin=origin, methods=methods)
            except ValueError as ve:
                return error(
                    handler_self,
                    400,
                    "invalid_request",
                    str(ve),
                    origin=origin,
                    methods=methods,
                )
            except Exception as e:
                json_log("error", f"{event or 'handler'}.error", message=str(e))
                return error(
                    handler_self,
                    500,
                    "internal_error",
                    "Request failed",
                    origin=origin,
                    methods=methods,
                )

        return wrapper

    return decorator
