import math
import os
from converter import UnitConverter


def test_length_conversion_m_to_ft():
    uc = UnitConverter()
    res = uc.convert(1.0, "m", "ft")
    assert isinstance(res, dict)
    val = res["result"]
    assert math.isclose(val, 3.280839895, rel_tol=1e-6)


def test_temperature_c_to_f():
    uc = UnitConverter()
    res = uc.convert(0.0, "celsius", "fahrenheit")
    assert res["result"] == 32.0


def test_invalid_units_raises():
    uc = UnitConverter()
    try:
        uc.convert(1.0, "meter", "lightyear")
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "Invalid unit conversion" in str(e)


def test_batch_convert_basic():
    uc = UnitConverter()
    conversions = uc.batch_convert(10.0, "m", ["ft", "km"])
    # At least two results, both success True
    assert len(conversions) == 2
    assert all(isinstance(c, dict) for c in conversions)
    assert any(c["to_unit"] == "ft" and c["success"] for c in conversions)
    assert any(c["to_unit"] == "km" and c["success"] for c in conversions)
