import os
import importlib


def test_currency_provider_success(monkeypatch):
    # Ensure we are not in fallback-only mode for this test
    os.environ.pop("CURRENCY_FALLBACK_ONLY", None)
    os.environ.pop("DISABLE_LIVE_FOREX", None)

    # Dummy provider that returns deterministic USD->CUR rates
    class DummyRates:
        MAP = {
            "EUR": 0.5,  # 1 USD = 0.5 EUR
            "GBP": 2.0,  # 1 USD = 2.0 GBP (intentionally unrealistic for testing)
        }

        def get_rate(self, base, currency):
            assert base == "USD"
            return self.MAP.get(currency, None)

    import converter as conv_mod

    # Monkeypatch the provider before instantiation so no network is touched
    monkeypatch.setattr(conv_mod, "CurrencyRates", DummyRates)

    importlib.reload(conv_mod)

    c = conv_mod.UnitConverter()

    # USD -> EUR using USD-based rates: 10 USD = 5 EUR
    out = c.convert(10.0, "USD", "EUR")
    assert out["result"] == 5.0
    assert isinstance(out["formatted"], str)

    # EUR -> USD: with USD->EUR = 0.5, 1 EUR = 2 USD
    out2 = c.convert(1.0, "EUR", "USD")
    assert abs(out2["result"] - 2.0) < 1e-9

    # USD -> GBP: 3 USD = 6 GBP
    out3 = c.convert(3.0, "USD", "GBP")
    assert abs(out3["result"] - 6.0) < 1e-9
