import io
import os
import re
import json
import importlib.util
from typing import Dict


def _load_module(rel_path: str):
    spec = importlib.util.spec_from_file_location("mod_under_test", rel_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def _tchar_safe(token: str) -> bool:
    # RFC7230 token chars: ! # $ % & ' * + - . ^ _ ` | ~ and ALPHA / DIGIT
    return re.search(r"[^!#$%&'*+\-.^_`|~0-9A-Za-z]", token) is None


class StubHeaders(dict):
    def get(self, key, default=None):
        return super().get(key, default)


class StubHandler:
    def __init__(
        self,
        method: str,
        path: str,
        headers: Dict[str, str] | None = None,
        body: bytes = b"",
    ):
        self.path = path
        self.command = method
        self.headers = StubHeaders(headers or {"Origin": "http://localhost"})
        self._headers_sent: Dict[str, str] = {}
        self._status = None
        self.rfile = io.BytesIO(body)
        self.wfile = io.BytesIO()

    def send_response(self, code: int):
        self._status = code

    def send_header(self, key: str, val: str):
        self._headers_sent[key] = val

    def end_headers(self):
        pass


def test_v1_convert_currency_meta_and_request_id(monkeypatch):
    # Deterministic fallback data
    monkeypatch.setenv("CURRENCY_FALLBACK_ONLY", "1")
    monkeypatch.setenv("FOREX_FALLBACK_JSON", "data/forex_fallback.json")

    mod = _load_module(os.path.join("api", "v1", "convert.py"))
    do_post = mod.handler.do_POST  # type: ignore[attr-defined]

    payload = {"value": 100, "from_unit": "USD", "to_unit": "EUR"}
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Origin": "http://localhost",
        "Content-Type": "application/json",
        "Content-Length": str(len(body)),
        "X-Request-Id": "client-Req_123",  # RFC7230-safe already
    }
    h = StubHandler("POST", "/api/v1/convert", headers=headers, body=body)

    do_post(h)  # type: ignore[misc]

    assert h._status == 200
    assert "X-Request-Id" in h._headers_sent
    assert "Access-Control-Expose-Headers" in h._headers_sent
    assert "X-Request-Id" in h._headers_sent["Access-Control-Expose-Headers"]

    payload_out = json.loads(h.wfile.getvalue().decode("utf-8"))
    assert payload_out.get("ok") is True

    # Envelope: data object with result/formatted fields
    data = payload_out.get("data")
    assert isinstance(data, dict)
    assert "result" in data and "formatted" in data

    # Meta and request id
    meta = payload_out.get("meta", {})
    rid = meta.get("request_id")
    assert isinstance(rid, str) and len(rid) > 0
    assert _tchar_safe(rid)
    assert h._headers_sent.get("X-Request-Id") == rid

    # Currency provenance nested under meta.currency in fallback mode
    currency_meta = meta.get("currency") or {}
    assert isinstance(currency_meta, dict)
    assert currency_meta.get("rates_source") == "fallback"
    assert currency_meta.get("fallback_forced") is True
    assert isinstance(currency_meta.get("rates_timestamp"), str)


def test_v1_convert_error_envelope_invalid_units(monkeypatch):
    # Ensure deterministic environment (not strictly needed here)
    monkeypatch.setenv("CURRENCY_FALLBACK_ONLY", "1")
    monkeypatch.setenv("FOREX_FALLBACK_JSON", "data/forex_fallback.json")

    mod = _load_module(os.path.join("api", "v1", "convert.py"))
    do_post = mod.handler.do_POST  # type: ignore[attr-defined]

    payload = {"value": 10, "from_unit": "bogus", "to_unit": "m"}
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Origin": "http://localhost",
        "Content-Type": "application/json",
        "Content-Length": str(len(body)),
    }
    h = StubHandler("POST", "/api/v1/convert", headers=headers, body=body)

    do_post(h)  # type: ignore[misc]

    assert h._status == 400
    out = json.loads(h.wfile.getvalue().decode("utf-8"))
    assert out.get("ok") is False
    err = out.get("error") or {}
    assert isinstance(err, dict)
    assert "code" in err and "message" in err
    # Meta and X-Request-Id still present on errors
    meta = out.get("meta", {})
    rid = meta.get("request_id")
    assert isinstance(rid, str) and len(rid) > 0
    assert _tchar_safe(rid)
    assert h._headers_sent.get("X-Request-Id") == rid


def test_v1_convert_options_preflight_headers():
    mod = _load_module(os.path.join("api", "v1", "convert.py"))
    do_options = mod.handler.do_OPTIONS  # type: ignore[attr-defined]
    h = StubHandler(
        "OPTIONS", "/api/v1/convert", headers={"Origin": "http://localhost"}
    )
    do_options(h)  # type: ignore[misc]

    assert h._status == 200
    # CORS headers
    assert h._headers_sent.get("Access-Control-Allow-Origin") in (
        "*",
        "http://localhost",
    )
    assert "GET" in h._headers_sent.get("Access-Control-Allow-Methods", "")
    assert "POST" in h._headers_sent.get("Access-Control-Allow-Methods", "")
    assert "OPTIONS" in h._headers_sent.get("Access-Control-Allow-Methods", "")
    # Expose X-Request-Id and header present
    assert "X-Request-Id" in h._headers_sent.get("Access-Control-Expose-Headers", "")
    assert "X-Request-Id" in h._headers_sent
    # Vary Origin and no-store
    assert h._headers_sent.get("Vary") == "Origin"
    assert h._headers_sent.get("Cache-Control") == "no-store"
