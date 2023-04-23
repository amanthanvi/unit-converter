# cli.py

import sys
from converter import UnitConverter

def main():
    try:
        value = float(sys.argv[1])
        from_unit = sys.argv[2]
        to_unit = sys.argv[3]

        result = UnitConverter.convert(value, from_unit, to_unit)
        print(f"{value} {from_unit} = {result} {to_unit}")
    except IndexError:
        print("Usage: python cli.py <value> <from_unit> <to_unit>")
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
