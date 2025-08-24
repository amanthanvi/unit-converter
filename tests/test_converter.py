from converter import UnitConverter

def test_length_basic():
    c = UnitConverter()
    out = c.convert(1, "m", "cm")
    assert out["result"] == 100

def test_temperature_roundtrip():
    c = UnitConverter()
    v = c.convert(0, "celsius", "fahrenheit")["result"]
    back = c.convert(v, "fahrenheit", "celsius")["result"]
    assert abs(back - 0) < 1e-6

def test_invalid_units():
    c = UnitConverter()
    try:
        c.convert(1, "foo", "bar")
        assert False, "Expected exception"
    except ValueError:
        assert True
