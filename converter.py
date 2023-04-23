# converter.py

from forex_python.converter import CurrencyRates

class UnitConverter:
    LENGTH_UNITS = {
        'mm': 0.001,
        'cm': 0.01,
        'm': 1,
        'km': 1000,
        'in': 0.0254,
        'ft': 0.3048,
        'yd': 0.9144,
        'mi': 1609.34
    }

    TEMPERATURE_UNITS = {
        'C': (lambda x: x, lambda x: x),
        'F': (lambda x: (x - 32) * (5 / 9), lambda x: x * (9 / 5) + 32),
        'K': (lambda x: x - 273.15, lambda x: x + 273.15)
    }

    CURRENCY_UNITS = [
        "USD", "EUR", "JPY", "GBP", "AUD", "CAD",
        "CHF", "CNY", "HKD", "NZD", "SEK", "KRW",
        "SGD", "NOK", "MXN", "INR", "RUB", "ZAR",
        "TRY", "BRL", "TWD", "DKK", "PLN", "THB",
        "IDR", "HUF", "CZK", "ILS", "CLP", "PHP",
        "AED", "COP", "SAR", "MYR", "RON", "ISK"
    ]

    CATEGORIES = {
        "Length": LENGTH_UNITS,
        "Temperature": TEMPERATURE_UNITS,
        "Currency": CURRENCY_UNITS
    }

    @classmethod
    def get_categories(cls):
        return list(cls.CATEGORIES.keys())

    @classmethod
    def get_units(cls, category):
        if category in cls.CATEGORIES:
            units = cls.CATEGORIES[category]
            return units if isinstance(units, list) else list(units.keys())
        raise ValueError("Unsupported category")

    @staticmethod
    def convert_length(value, from_unit, to_unit):
        return value * (UnitConverter.LENGTH_UNITS[from_unit] / UnitConverter.LENGTH_UNITS[to_unit])

    @staticmethod
    def convert_temperature(value, from_unit, to_unit):
        to_celsius = UnitConverter.TEMPERATURE_UNITS[from_unit][0]
        from_celsius = UnitConverter.TEMPERATURE_UNITS[to_unit][1]

        return from_celsius(to_celsius(value))

    @staticmethod
    def convert_currency(value, from_currency, to_currency):
        currency_converter = CurrencyRates()
        return currency_converter.convert(from_currency, to_currency, value)

    @classmethod
    def convert(cls, value, from_unit, to_unit):
        if from_unit in cls.LENGTH_UNITS and to_unit in cls.LENGTH_UNITS:
            return cls.convert_length(value, from_unit, to_unit)

        if from_unit in cls.TEMPERATURE_UNITS and to_unit in cls.TEMPERATURE_UNITS:
            return cls.convert_temperature(value, from_unit, to_unit)

        if from_unit in cls.CURRENCY_UNITS and to_unit in cls.CURRENCY_UNITS:
            return cls.convert_currency(value, from_unit, to_unit)

        raise ValueError(f"Unsupported conversion: {from_unit} to {to_unit}")
