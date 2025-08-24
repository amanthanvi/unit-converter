from forex_python.converter import CurrencyRates, RatesNotAvailableError
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import math


class UnitConverter:
    def __init__(self):
        self.categories = {
            "length": {
                "name": "Length",
                "icon": "📏",
                "units": {
                    "mm": {"name": "Millimeter", "factor": 0.001},
                    "cm": {"name": "Centimeter", "factor": 0.01},
                    "m": {"name": "Meter", "factor": 1},
                    "km": {"name": "Kilometer", "factor": 1000},
                    "in": {"name": "Inch", "factor": 0.0254},
                    "ft": {"name": "Foot", "factor": 0.3048},
                    "yd": {"name": "Yard", "factor": 0.9144},
                    "mi": {"name": "Mile", "factor": 1609.344},
                },
            },
            "weight": {
                "name": "Weight",
                "icon": "⚖️",
                "units": {
                    "mg": {"name": "Milligram", "factor": 0.000001},
                    "g": {"name": "Gram", "factor": 0.001},
                    "kg": {"name": "Kilogram", "factor": 1},
                    "ton": {"name": "Metric Ton", "factor": 1000},
                    "oz": {"name": "Ounce", "factor": 0.0283495},
                    "lb": {"name": "Pound", "factor": 0.453592},
                    "stone": {"name": "Stone", "factor": 6.35029},
                },
            },
            "temperature": {
                "name": "Temperature",
                "icon": "🌡️",
                "units": {
                    "celsius": {"name": "Celsius", "symbol": "°C"},
                    "fahrenheit": {"name": "Fahrenheit", "symbol": "°F"},
                    "kelvin": {"name": "Kelvin", "symbol": "K"},
                },
            },
            "volume": {
                "name": "Volume",
                "icon": "🧪",
                "units": {
                    "ml": {"name": "Milliliter", "factor": 0.001},
                    "l": {"name": "Liter", "factor": 1},
                    "gal": {"name": "US Gallon", "factor": 3.78541},
                    "qt": {"name": "US Quart", "factor": 0.946353},
                    "pt": {"name": "US Pint", "factor": 0.473176},
                    "cup": {"name": "US Cup", "factor": 0.236588},
                    "fl_oz": {"name": "US Fluid Ounce", "factor": 0.0295735},
                    "tbsp": {"name": "Tablespoon", "factor": 0.0147868},
                    "tsp": {"name": "Teaspoon", "factor": 0.00492892},
                },
            },
            "area": {
                "name": "Area",
                "icon": "📐",
                "units": {
                    "mm2": {"name": "Square Millimeter", "factor": 0.000001},
                    "cm2": {"name": "Square Centimeter", "factor": 0.0001},
                    "m2": {"name": "Square Meter", "factor": 1},
                    "km2": {"name": "Square Kilometer", "factor": 1000000},
                    "in2": {"name": "Square Inch", "factor": 0.00064516},
                    "ft2": {"name": "Square Foot", "factor": 0.092903},
                    "yd2": {"name": "Square Yard", "factor": 0.836127},
                    "acre": {"name": "Acre", "factor": 4046.86},
                    "hectare": {"name": "Hectare", "factor": 10000},
                },
            },
            "speed": {
                "name": "Speed",
                "icon": "🚀",
                "units": {
                    "mps": {"name": "Meters per Second", "factor": 1},
                    "kph": {"name": "Kilometers per Hour", "factor": 0.277778},
                    "mph": {"name": "Miles per Hour", "factor": 0.44704},
                    "knot": {"name": "Knot", "factor": 0.514444},
                    "mach": {"name": "Mach", "factor": 343},  # at sea level
                },
            },
            "time": {
                "name": "Time",
                "icon": "⏱️",
                "units": {
                    "ms": {"name": "Millisecond", "factor": 0.001},
                    "s": {"name": "Second", "factor": 1},
                    "min": {"name": "Minute", "factor": 60},
                    "hr": {"name": "Hour", "factor": 3600},
                    "day": {"name": "Day", "factor": 86400},
                    "week": {"name": "Week", "factor": 604800},
                    "month": {"name": "Month", "factor": 2629800},  # average
                    "year": {"name": "Year", "factor": 31557600},  # average
                },
            },
            "digital": {
                "name": "Digital Storage",
                "icon": "💾",
                "units": {
                    "bit": {"name": "Bit", "factor": 0.125},
                    "byte": {"name": "Byte", "factor": 1},
                    "kb": {"name": "Kilobyte", "factor": 1024},
                    "mb": {"name": "Megabyte", "factor": 1048576},
                    "gb": {"name": "Gigabyte", "factor": 1073741824},
                    "tb": {"name": "Terabyte", "factor": 1099511627776},
                    "pb": {"name": "Petabyte", "factor": 1125899906842624},
                },
            },
            "currency": {
                "name": "Currency",
                "icon": "💱",
                "units": self._get_currency_units(),
            },
        }

        # Cache for currency rates
        self._currency_cache = {}
        self._cache_timestamp = None
        self._cache_duration = timedelta(hours=1)

        # Real-world comparisons database
        self.comparisons = self._load_comparisons()

    def _get_currency_units(self) -> Dict[str, Dict[str, str]]:
        """Get currency units with full names"""
        currencies = {
            "USD": {"name": "US Dollar", "symbol": "$"},
            "EUR": {"name": "Euro", "symbol": "€"},
            "JPY": {"name": "Japanese Yen", "symbol": "¥"},
            "GBP": {"name": "British Pound", "symbol": "£"},
            "AUD": {"name": "Australian Dollar", "symbol": "A$"},
            "CAD": {"name": "Canadian Dollar", "symbol": "C$"},
            "CHF": {"name": "Swiss Franc", "symbol": "Fr"},
            "CNY": {"name": "Chinese Yuan", "symbol": "¥"},
            "SEK": {"name": "Swedish Krona", "symbol": "kr"},
            "NZD": {"name": "New Zealand Dollar", "symbol": "NZ$"},
            "MXN": {"name": "Mexican Peso", "symbol": "$"},
            "SGD": {"name": "Singapore Dollar", "symbol": "S$"},
            "HKD": {"name": "Hong Kong Dollar", "symbol": "HK$"},
            "NOK": {"name": "Norwegian Krone", "symbol": "kr"},
            "KRW": {"name": "South Korean Won", "symbol": "₩"},
            "TRY": {"name": "Turkish Lira", "symbol": "₺"},
            "RUB": {"name": "Russian Ruble", "symbol": "₽"},
            "INR": {"name": "Indian Rupee", "symbol": "₹"},
            "BRL": {"name": "Brazilian Real", "symbol": "R$"},
            "ZAR": {"name": "South African Rand", "symbol": "R"},
            "DKK": {"name": "Danish Krone", "symbol": "kr"},
            "PLN": {"name": "Polish Złoty", "symbol": "zł"},
            "THB": {"name": "Thai Baht", "symbol": "฿"},
            "IDR": {"name": "Indonesian Rupiah", "symbol": "Rp"},
            "HUF": {"name": "Hungarian Forint", "symbol": "Ft"},
            "CZK": {"name": "Czech Koruna", "symbol": "Kč"},
            "ILS": {"name": "Israeli Shekel", "symbol": "₪"},
            "CLP": {"name": "Chilean Peso", "symbol": "$"},
            "PHP": {"name": "Philippine Peso", "symbol": "₱"},
            "AED": {"name": "UAE Dirham", "symbol": "د.إ"},
            "COP": {"name": "Colombian Peso", "symbol": "$"},
            "SAR": {"name": "Saudi Riyal", "symbol": "﷼"},
            "MYR": {"name": "Malaysian Ringgit", "symbol": "RM"},
            "RON": {"name": "Romanian Leu", "symbol": "lei"},
            "BGN": {"name": "Bulgarian Lev", "symbol": "лв"},
            "HRK": {"name": "Croatian Kuna", "symbol": "kn"},
        }
        return currencies

    def _load_comparisons(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Load real-world comparisons for different units"""
        return {
            "length": {
                "m": [
                    {
                        "value": 1,
                        "description": "About the height of a kitchen counter",
                    },
                    {"value": 100, "description": "Length of a football field"},
                    {
                        "value": 828,
                        "description": "Height of Burj Khalifa, the tallest building",
                    },
                    {"value": 8848, "description": "Height of Mount Everest"},
                ],
                "km": [
                    {"value": 1, "description": "About a 12-minute walk"},
                    {"value": 42.195, "description": "Length of a marathon"},
                    {"value": 384400, "description": "Distance to the Moon"},
                ],
                "ft": [
                    {"value": 6, "description": "Average human height"},
                    {"value": 1250, "description": "Height of Empire State Building"},
                    {
                        "value": 36000,
                        "description": "Cruising altitude of commercial aircraft",
                    },
                ],
            },
            "weight": {
                "kg": [
                    {"value": 0.001, "description": "Weight of a paperclip"},
                    {"value": 0.5, "description": "Weight of a soccer ball"},
                    {"value": 70, "description": "Average human weight"},
                    {"value": 6000, "description": "Weight of an African elephant"},
                ],
                "lb": [
                    {"value": 0.5, "description": "Weight of a hamburger"},
                    {"value": 8, "description": "Weight of a newborn baby"},
                    {"value": 2000, "description": "Weight of a small car"},
                ],
            },
            "volume": {
                "l": [
                    {"value": 0.25, "description": "A cup of coffee"},
                    {"value": 2, "description": "Large soda bottle"},
                    {"value": 50, "description": "Average car fuel tank"},
                    {"value": 500000, "description": "Olympic swimming pool"},
                ]
            },
            "area": {
                "m2": [
                    {"value": 1, "description": "Small dining table"},
                    {"value": 50, "description": "Studio apartment"},
                    {"value": 100, "description": "Tennis court"},
                    {"value": 10000, "description": "Soccer field"},
                ]
            },
            "speed": {
                "kph": [
                    {"value": 5, "description": "Walking speed"},
                    {"value": 40, "description": "City driving speed"},
                    {"value": 300, "description": "High-speed train"},
                    {"value": 1225, "description": "Speed of sound"},
                ]
            },
        }

    def get_categories(self) -> List[Dict[str, str]]:
        """Get all available conversion categories"""
        return [
            {"id": cat_id, "name": cat_data["name"], "icon": cat_data.get("icon", "📊")}
            for cat_id, cat_data in self.categories.items()
        ]

    def get_units(self, category: str) -> List[Dict[str, str]]:
        """Get units for a specific category"""
        if category not in self.categories:
            return []
        return [
            {
                "id": unit_id,
                "name": unit_data["name"],
                "symbol": unit_data.get("symbol", unit_id),
            }
            for unit_id, unit_data in self.categories[category]["units"].items()
        ]

    def convert(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """Convert between units with additional context"""
        # Find the category
        category = None
        for cat_id, cat_data in self.categories.items():
            if from_unit in cat_data["units"] and to_unit in cat_data["units"]:
                category = cat_id
                break

        if not category:
            raise ValueError(f"Invalid unit conversion: {from_unit} to {to_unit}")

        # Perform conversion
        if category == "temperature":
            result = self._convert_temperature(value, from_unit, to_unit)
        elif category == "currency":
            result = self._convert_currency(value, from_unit, to_unit)
        else:
            result = self._convert_standard(value, from_unit, to_unit, category)

        # Get comparisons
        comparisons = self._get_relevant_comparisons(result, to_unit, category)

        # Historical context
        history = self._get_historical_context(from_unit, to_unit)

        resp = {
            "result": result,
            "formatted": self._format_result(result, to_unit, category),
            "comparisons": comparisons,
            "history": history,
            "category": category,
            "from_unit": self.categories[category]["units"][from_unit]["name"],
            "to_unit": self.categories[category]["units"][to_unit]["name"],
        }
        # Attach currency rates metadata when applicable
        if category == "currency":
            meta = getattr(self, "_currency_meta", None)
            if isinstance(meta, dict):
                resp["meta"] = dict(meta)
        return resp

    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert between temperature units with absolute zero validation"""
        # Convert to Celsius first
        if from_unit == "fahrenheit":
            celsius = (value - 32) * 5 / 9
        elif from_unit == "kelvin":
            # Kelvin cannot be negative
            if value < 0:
                raise ValueError("Temperature below absolute zero")
            celsius = value - 273.15
        else:
            celsius = value

        # Physical constraint: absolute zero
        if celsius < -273.15 - 1e-9:
            raise ValueError("Temperature below absolute zero")

        # Convert from Celsius to target
        if to_unit == "fahrenheit":
            return celsius * 9 / 5 + 32
        elif to_unit == "kelvin":
            return celsius + 273.15
        else:
            return celsius

    def _convert_currency(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert between currencies with caching and resilient fallbacks"""
        if from_unit == to_unit:
            return value

        now = datetime.now()
        rates = None

        # Environment toggles for resilience
        force_fallback = os.getenv("CURRENCY_FALLBACK_ONLY", "").strip() == "1"
        disable_live = os.getenv("DISABLE_LIVE_FOREX", "").strip() == "1"
        source = None

        # Use cache if fresh
        if (
            self._cache_timestamp
            and now - self._cache_timestamp < self._cache_duration
            and self._currency_cache
        ):
            rates = self._currency_cache
        else:
            if force_fallback or disable_live:
                rates = self._load_fallback_rates()
                self._currency_cache = rates
                self._cache_timestamp = now
                source = "fallback"
            else:
                # Try live fetch then fall back to static data on failure
                try:
                    cr = CurrencyRates()
                    rates = {}
                    # Get rates for common base currency (USD)
                    for currency in self.categories["currency"]["units"]:
                        if currency != "USD":
                            try:
                                rates[currency] = float(cr.get_rate("USD", currency))
                            except Exception:
                                # skip currency if not available
                                continue
                    rates["USD"] = 1.0
                    self._currency_cache = rates
                    self._cache_timestamp = now
                    source = "live"
                except Exception:
                    rates = self._load_fallback_rates()
                    self._currency_cache = rates
                    self._cache_timestamp = now
                    source = "fallback"

        # Record currency rate source metadata
        if source is None:
            prev = getattr(self, "_currency_meta", None)
            source = prev.get("rates_source") if isinstance(prev, dict) else "live"
        self._currency_meta = {
            "rates_source": source,
            "fallback_forced": force_fallback,
            "live_disabled": disable_live,
        }
        # Convert using USD as base
        if rates.get(from_unit) and rates.get(to_unit):
            usd_value = value / rates[from_unit]
            return usd_value * rates[to_unit]
        else:
            raise ValueError(
                f"Exchange rate not available for {from_unit} to {to_unit}"
            )

    def _load_fallback_rates(self) -> Dict[str, float]:
        """Load static fallback rates and normalize to USD base.

        Accepts either:
          - {"USD": 1.0, "EUR": 0.92, ...}
          - {"base": "EUR", "rates": {"USD": 1.25, "GBP": 0.8, ...}}
        Raises:
          - FileNotFoundError if file is missing
          - json.JSONDecodeError if JSON is invalid
          - ValueError if structure is unsupported or lacks required keys
        """
        path = (
            os.getenv("CURRENCY_FALLBACK_PATH")
            or os.getenv("FOREX_FALLBACK_JSON")
            or "data/forex_fallback.json"
        )

        # Let exceptions propagate for tests to assert exact failures
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        base = "USD"
        rates_src: Dict[str, Any] = {}

        if isinstance(data, dict) and "rates" in data:
            # structured format with base
            base = str(data.get("base", "USD")).upper()
            rates_map = data["rates"]
            if not isinstance(rates_map, dict):
                raise ValueError("Invalid rates structure in fallback JSON")
            rates_src = {str(k).upper(): rates_map[k] for k in rates_map}
        elif isinstance(data, dict):
            # flat map assumed USD base
            base = "USD"
            rates_src = {str(k).upper(): v for k, v in data.items()}
        else:
            raise ValueError("Unsupported fallback JSON structure")

        # Coerce to floats where possible
        tmp: Dict[str, Optional[float]] = {}
        for k, v in rates_src.items():
            try:
                tmp[k] = float(v)
            except (TypeError, ValueError):
                tmp[k] = None

        # Normalize to USD base so that rates[cur] == CUR per 1 USD
        # If base is USD, ensure USD=1.0 and drop invalids
        if base == "USD":
            # Normalize to USD=1.0, handling None safely
            usd_val = tmp.get("USD", 1.0)
            try:
                usd_val_f = float(usd_val)
            except (TypeError, ValueError):
                usd_val_f = 1.0
            if usd_val_f != 1.0:
                denom = usd_val_f
                tmp = {
                    cur: (None if rate is None else float(rate) / denom)
                    for cur, rate in tmp.items()
                }
            tmp["USD"] = 1.0
            # Drop invalid entries
            rates = {cur: rate for cur, rate in tmp.items() if rate is not None}
            return rates

        # Non-USD base: convert to USD-based using rates(cur)/rates(USD) where rates are per 1 base
        if base not in tmp:
            # If no explicit base rate present (common), assume base=1.0 in its own units
            tmp[base] = 1.0
        usd_per_base = tmp.get("USD")
        if usd_per_base in (None, 0.0):
            raise ValueError("Fallback JSON lacks usable USD rate for normalization")

        base_to_usd = 1.0 / float(
            usd_per_base
        )  # multiply base-denominated rates by this to get per USD
        normalized: Dict[str, float] = {"USD": 1.0}
        for cur, rate in tmp.items():
            if cur == "USD":
                continue
            if rate is None:
                continue
            # rate = CUR per 1 BASE; per USD = (CUR/BASE) / (USD/BASE) = CUR per USD
            normalized[cur] = float(rate) / float(usd_per_base)

        # Ensure EUR value consistency if base was EUR (sanity)
        return normalized

    def _convert_standard(
        self, value: float, from_unit: str, to_unit: str, category: str
    ) -> float:
        """Convert between standard units using factors"""
        from_factor = self.categories[category]["units"][from_unit]["factor"]
        to_factor = self.categories[category]["units"][to_unit]["factor"]
        return value * from_factor / to_factor

    def _format_result(self, value: float, unit: str, category: str) -> str:
        """Format the result with appropriate precision"""
        if category == "currency":
            return f"{value:,.2f}"
        elif value > 1000 or value < 0.01:
            return f"{value:.2e}"
        elif value > 100:
            return f"{value:,.0f}"
        elif value > 1:
            return f"{value:,.2f}"
        else:
            return f"{value:.6f}".rstrip("0").rstrip(".")

    def _get_relevant_comparisons(
        self, value: float, unit: str, category: str
    ) -> List[Dict[str, Any]]:
        """Get relevant real-world comparisons for the converted value"""
        comparisons = []

        if category in self.comparisons and unit in self.comparisons[category]:
            unit_comparisons = self.comparisons[category][unit]

            # Find closest comparisons
            for comp in unit_comparisons:
                ratio = value / comp["value"]
                if 0.1 <= ratio <= 10:  # Within an order of magnitude
                    comparisons.append(
                        {
                            "description": comp["description"],
                            "value": comp["value"],
                            "ratio": ratio,
                            "formatted": self._format_comparison_ratio(ratio),
                        }
                    )

            # Sort by how close the ratio is to 1
            comparisons.sort(key=lambda x: abs(1 - x["ratio"]))

        return comparisons[:3]  # Return top 3 most relevant

    def _format_comparison_ratio(self, ratio: float) -> str:
        """Format comparison ratio in a human-readable way"""
        if ratio < 0.1:
            return f"1/{int(1/ratio)}"
        elif ratio < 0.9:
            return f"{ratio:.1f}×"
        elif ratio < 1.1:
            return "about the same as"
        elif ratio < 10:
            return f"{ratio:.1f}×"
        else:
            return f"{int(ratio)}×"

    def _get_historical_context(self, from_unit: str, to_unit: str) -> Optional[str]:
        """Get historical context about the units"""
        contexts = {
            (
                "ft",
                "m",
            ): "The foot was originally based on the human foot length. The meter was defined as 1/10,000,000 of the distance from the equator to the North Pole.",
            (
                "mi",
                "km",
            ): "The mile comes from the Roman 'mille passus' (1000 paces). The kilometer is part of the metric system, created during the French Revolution.",
            (
                "lb",
                "kg",
            ): "The pound has ancient Roman origins. The kilogram was originally defined as the mass of 1 liter of water.",
            (
                "fahrenheit",
                "celsius",
            ): "Fahrenheit set 0°F as the freezing point of brine and 96°F as human body temperature. Celsius based his scale on water's freezing (0°C) and boiling (100°C) points.",
        }

        return contexts.get((from_unit, to_unit)) or contexts.get((to_unit, from_unit))

    def get_quick_conversions(self, value: float, unit: str) -> List[Dict[str, Any]]:
        """Get quick conversions to commonly used units in the same category"""
        category = None
        for cat_id, cat_data in self.categories.items():
            if unit in cat_data["units"]:
                category = cat_id
                break

        if not category:
            return []

        # Define common units for each category
        common_units = {
            "length": ["m", "ft", "km", "mi"],
            "weight": ["kg", "lb", "g", "oz"],
            "temperature": ["celsius", "fahrenheit", "kelvin"],
            "volume": ["l", "gal", "ml", "cup"],
            "area": ["m2", "ft2", "acre", "hectare"],
            "speed": ["kph", "mph", "mps"],
            "time": ["s", "min", "hr", "day"],
            "digital": ["mb", "gb", "tb"],
            "currency": ["USD", "EUR", "GBP", "JPY"],
        }

        results = []
        for target_unit in common_units.get(category, []):
            if (
                target_unit != unit
                and target_unit in self.categories[category]["units"]
            ):
                try:
                    conversion = self.convert(value, unit, target_unit)
                    results.append(
                        {
                            "unit": target_unit,
                            "name": self.categories[category]["units"][target_unit][
                                "name"
                            ],
                            "value": conversion["result"],
                            "formatted": conversion["formatted"],
                        }
                    )
                except:
                    pass

        return results

    def batch_convert(
        self, value: float, from_unit: str, to_units: List[str]
    ) -> List[Dict[str, Any]]:
        """Convert a value to multiple target units at once"""
        results = []

        for to_unit in to_units:
            try:
                conversion = self.convert(value, from_unit, to_unit)
                results.append(
                    {
                        "success": True,
                        "to_unit": to_unit,
                        "result": conversion["result"],
                        "formatted": conversion["formatted"],
                        "comparisons": conversion.get("comparisons", []),
                        "history": conversion.get("history"),
                    }
                )
            except Exception as e:
                results.append({"success": False, "to_unit": to_unit, "error": str(e)})

        return results

    def get_all_units_in_category(self, unit: str) -> List[str]:
        """Get all units in the same category as the given unit"""
        for cat_id, cat_data in self.categories.items():
            if unit in cat_data["units"]:
                return list(cat_data["units"].keys())
        return []
