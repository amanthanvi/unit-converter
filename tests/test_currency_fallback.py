import os
import json
import importlib
import types


# We will monkeypatch converter.CurrencyRates to raise, forcing fallback
def test_currency_fallback(monkeypatch, tmp_path):
    # Prepare a temporary fallback file with deterministic rates
    fallback = {
        "base": "USD",
        "date": "2024-01-01",
        "rates": {"EUR": 0.9, "GBP": 0.8, "JPY": 150.0},
    }
    fallback_path = tmp_path / "forex_fallback.json"
    fallback_path.write_text(json.dumps(fallback), encoding="utf-8")

    # Set env to point to the temp fallback and force fallback-only mode
    os.environ["FOREX_FALLBACK_JSON"] = str(fallback_path)
    os.environ["CURRENCY_FALLBACK_ONLY"] = "1"

    # Monkeypatch CurrencyRates to raise on init or usage
    class BrokenCR:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("network disabled")

    # Import converter and monkeypatch provider to force failure (no reload to preserve patch)
    import converter as conv_mod

    monkeypatch.setattr(conv_mod, "CurrencyRates", BrokenCR)

    conv = conv_mod.UnitConverter()
    # Convert 1 USD to EUR; fallback has EUR=0.9
    out = conv.convert(1.0, "USD", "EUR")
    assert out["result"] == 0.9
    assert isinstance(out["formatted"], str)

    # And EUR to USD should be ~1/0.9
    out2 = conv.convert(0.9, "EUR", "USD")
    # There might be formatting differences; compare numeric
    assert abs(out2["result"] - 1.0) < 1e-9
