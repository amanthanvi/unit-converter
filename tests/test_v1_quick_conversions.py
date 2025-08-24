import io
import os
import re
import json
import importlib.util
from typing import Dict


def _load_module(rel_path: str):
    # Load a Python file as a module by path (works for files with hyphens in name)
    spec = importlib.util.spec_from_file_location("mod_under_test", rel_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


class StubHandler:
    def __init__(self, path: str, headers: Dict[str, str] | None = None):
        self.path = path
        self.command = "GET"
        self.headers = headers or {"Origin": "http://localhost"}
        self._headers_sent: Dict[str, str] = {}
        self._status = None
        self.rfile = io.BytesIO(b"")
        self.wfile = io.BytesIO()

    # Methods consumed by api/_common.ok() and error()
    def send_response(self, code: int):
        self._status = code

    def send_header(self, key: str, val: str):
        self._headers_sent[key] = val

    def end_headers(self):
        pass


def _tchar_safe(token: str) -> bool:
    # RFC7230 token chars: ! # $ % & ' * + - . ^ _ ` | ~ and ALPHA / DIGIT
    return re.search(r"[^!#$%&'*+\-.^_`|~0-9A-Za-z]", token) is None


def test_v1_quick_conversions_envelope_and_currency_meta(monkeypatch):
    # Ensure fallback currency mode for deterministic assertions
    monkeypatch.setenv("CURRENCY_FALLBACK_ONLY", "1")
    monkeypatch.setenv("FOREX_FALLBACK_JSON", "data/forex_fallback.json")

    mod = _load_module(os.path.join("api", "v1", "quick-conversions.py"))
    # Acquire the do_GET function from the class, will act as a descriptor expecting "self"
    do_get = mod.handler.do_GET

    # Build a stub request targeting the v1 endpoint with currency category
    path = "/api/v1/quick-conversions?value=100&unit=USD"
    # Use real ampersand, not HTML escaped
    path = "/api/v1/quick-conversions?value=100&unit=USD"
    h = StubHandler(path)

    # Invoke handler
    do_get(h)  # type: ignore[misc]

    # Validate status and headers
    assert h._status == 200
    # CORS expose must include X-Request-Id
    assert "Access-Control-Expose-Headers" in h._headers_sent
    assert "X-Request-Id" in h._headers_sent["Access-Control-Expose-Headers"]
    assert "X-Request-Id" in h._headers_sent

    # Parse body
    payload = json.loads(h.wfile.getvalue().decode("utf-8"))
    assert payload.get("ok") is True

    # Envelope: result is a list of quick conversions
    result = payload.get("result")
    assert isinstance(result, list)
    assert len(result) > 0
    sample = result[0]
    # Each item should have expected fields
    assert "unit" in sample and "name" in sample and "formatted" in sample

    # Meta present with request_id and currency provenance
    meta = payload.get("meta", {})
    assert isinstance(meta, dict)
    # request_id present and RFC7230-safe
    rid = meta.get("request_id")
    assert isinstance(rid, str) and len(rid) > 0
    assert _tchar_safe(rid)
    # rates_source and timestamp present (fallback mode)
    assert meta.get("rates_source") == "fallback"
    assert meta.get("fallback_forced") is True
    # Timestamp-ish field present
    assert isinstance(meta.get("rates_timestamp"), str)

    # X-Request-Id header equals payload meta.request_id
    assert h._headers_sent.get("X-Request-Id") == rid
