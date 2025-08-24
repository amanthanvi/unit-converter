import os
import json
from converter import UnitConverter


def test_currency_fallback_usd_to_eur(monkeypatch):
    # Force fallback mode and point to repo fallback file
    monkeypatch.setenv("CURRENCY_FALLBACK_ONLY", "1")
    monkeypatch.setenv("FOREX_FALLBACK_JSON", "data/forex_fallback.json")

    uc = UnitConverter()
    amount = 100.0
    res = uc.convert(amount, "USD", "EUR")
    assert isinstance(res, dict)
    # Using fallback EUR ~ 0.92 (from data/forex_fallback.json)
    expected = amount * 0.92
    # Allow tiny float variance
    assert abs(res["result"] - expected) < 1e-6
    # formatted is a string
    assert isinstance(res["formatted"], str)


def test_currency_fallback_round_trip(monkeypatch):
    monkeypatch.setenv("CURRENCY_FALLBACK_ONLY", "1")
    monkeypatch.setenv("FOREX_FALLBACK_JSON", "data/forex_fallback.json")

    uc = UnitConverter()
    amount = 50.0
    # USD -> GBP using fallback ~ 0.78
    to_gbp = uc.convert(amount, "USD", "GBP")["result"]
    # GBP -> USD should invert
    back_to_usd = uc.convert(to_gbp, "GBP", "USD")["result"]
    assert abs(back_to_usd - amount) < 1e-6


def test_fallback_missing_file(monkeypatch, tmp_path):
    monkeypatch.setenv("CURRENCY_FALLBACK_ONLY", "1")
    monkeypatch.setenv("FOREX_FALLBACK_JSON", str(tmp_path / "nope.json"))
    uc = UnitConverter()
    try:
        uc._load_fallback_rates()
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_fallback_empty_file(monkeypatch, tmp_path):
    p = tmp_path / "empty.json"
    p.write_text("", encoding="utf-8")
    monkeypatch.setenv("CURRENCY_FALLBACK_ONLY", "1")
    monkeypatch.setenv("FOREX_FALLBACK_JSON", str(p))
    uc = UnitConverter()
    try:
        uc._load_fallback_rates()
        assert False, "Expected JSONDecodeError"
    except json.JSONDecodeError:
        pass


def test_fallback_invalid_json(monkeypatch, tmp_path):
    p = tmp_path / "invalid.json"
    p.write_text("not json", encoding="utf-8")
    monkeypatch.setenv("CURRENCY_FALLBACK_ONLY", "1")
    monkeypatch.setenv("FOREX_FALLBACK_JSON", str(p))
    uc = UnitConverter()
    try:
        uc._load_fallback_rates()
        assert False, "Expected JSONDecodeError"
    except json.JSONDecodeError:
        pass


def test_fallback_non_usd_base_normalizes(monkeypatch, tmp_path):
    data = {"base": "EUR", "rates": {"EUR": 1.0, "USD": 1.25, "GBP": 0.8}}
    p = tmp_path / "eur_base.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setenv("CURRENCY_FALLBACK_ONLY", "1")
    monkeypatch.setenv("FOREX_FALLBACK_JSON", str(p))

    uc = UnitConverter()
    # USD->EUR should be 0.8 (since USD per EUR is 1.25 => EUR per USD is 0.8)
    res = uc.convert(100.0, "USD", "EUR")
    assert abs(res["result"] - 80.0) < 1e-6
    # round-trip EUR->USD
    back = uc.convert(res["result"], "EUR", "USD")
    assert abs(back["result"] - 100.0) < 1e-6
