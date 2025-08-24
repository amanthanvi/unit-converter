import os
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
