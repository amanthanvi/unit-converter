from types import SimpleNamespace
from api._common import request_id


class StubHeaders(dict):
    def get(self, key, default=None):
        return super().get(key, default)


class StubHandler:
    def __init__(self, headers: dict):
        # Mimic handler with a headers mapping
        self.headers = StubHeaders(headers)


def test_request_id_sanitizes_crlf_and_colon():
    # Malicious header value containing CR, LF, and colon
    malicious = "abc:123\r\nInjected-Header: value"
    handler = StubHandler({"X-Request-Id": malicious})

    rid = request_id(handler)
    # Ensure CR, LF, and colon are removed and rest of content preserved
    assert "\r" not in rid
    assert "\n" not in rid
    assert ":" not in rid
    # Basic sanity: original letters remain in order without forbidden chars
    assert "abc123Injected-Headervalue" == rid.replace(" ", "")


def test_request_id_generates_uuid_when_missing():
    handler = StubHandler({})  # No X-Request-Id header
    rid = request_id(handler)
    # Expect a UUID-like string (contains hyphens and length ~36)
    assert isinstance(rid, str)
    assert "-" in rid
    assert len(rid) >= 32
