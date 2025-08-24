import math
import pytest
from converter import UnitConverter


def test_length_zero_stays_zero():
    uc = UnitConverter()
    res = uc.convert(0.0, "m", "ft")
    assert res["result"] == 0.0
    assert isinstance(res["formatted"], str)


def test_length_large_value():
    uc = UnitConverter()
    res = uc.convert(1_000_000_000.0, "m", "km")
    assert math.isclose(res["result"], 1_000_000.0, rel_tol=1e-9)


def test_temperature_absolute_zero_celsius_bounded():
    uc = UnitConverter()
    # Exactly absolute zero in Celsius -> Kelvin 0
    res0 = uc.convert(-273.15, "celsius", "kelvin")
    assert math.isclose(res0["result"], 0.0, abs_tol=1e-9)
    # Below absolute zero should raise
    with pytest.raises(ValueError):
        uc.convert(-273.16, "celsius", "kelvin")


def test_temperature_absolute_zero_fahrenheit_bounded():
    uc = UnitConverter()
    # Exactly absolute zero in Fahrenheit -> Kelvin 0
    res0 = uc.convert(-459.67, "fahrenheit", "kelvin")
    assert math.isclose(res0["result"], 0.0, abs_tol=1e-6)
    # Below absolute zero should raise
    with pytest.raises(ValueError):
        uc.convert(-459.68, "fahrenheit", "kelvin")


def test_temperature_negative_kelvin_raises():
    uc = UnitConverter()
    with pytest.raises(ValueError):
        uc.convert(-1.0, "kelvin", "celsius")


def test_temperature_roundtrip_c_f():
    uc = UnitConverter()
    start = 100.0
    f = uc.convert(start, "celsius", "fahrenheit")["result"]
    back = uc.convert(f, "fahrenheit", "celsius")["result"]
    assert math.isclose(back, start, rel_tol=1e-12, abs_tol=1e-9)


def test_temperature_minus_40_equality():
    uc = UnitConverter()
    f = uc.convert(-40.0, "celsius", "fahrenheit")["result"]
    assert math.isclose(f, -40.0, abs_tol=1e-12)
    c = uc.convert(-40.0, "fahrenheit", "celsius")["result"]
    assert math.isclose(c, -40.0, abs_tol=1e-12)


def test_temperature_large_magnitude():
    uc = UnitConverter()
    res = uc.convert(1_000_000.0, "kelvin", "celsius")
    # Large but finite
    assert math.isfinite(res["result"])
