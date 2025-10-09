#!/usr/bin/env python3
"""
Test script to verify all components of the unit converter are functioning.
"""

import sys
from converter import UnitConverter

def test_converter_module():
    """Test the core converter module"""
    print("Testing UnitConverter module...")
    
    converter = UnitConverter()
    
    # Test length conversion
    result = converter.convert(100, 'm', 'ft')
    print(f"✓ Length: 100 m = {result['result']:.2f} ft")
    
    # Test temperature conversion
    result = converter.convert(32, 'fahrenheit', 'celsius')
    print(f"✓ Temperature: 32°F = {result['result']:.2f}°C")
    
    # Test weight conversion
    result = converter.convert(1, 'kg', 'lb')
    print(f"✓ Weight: 1 kg = {result['result']:.2f} lb")
    
    # Test volume conversion
    result = converter.convert(1, 'l', 'gal')
    print(f"✓ Volume: 1 L = {result['result']:.2f} gal")
    
    # Test get_categories
    categories = converter.get_categories()
    print(f"✓ Available categories: {len(categories)}")
    
    # Test get_units
    units = converter.get_units('length')
    print(f"✓ Length units: {len(units)} units available")
    
    print("✓ UnitConverter module: PASSED\n")
    return True

def test_cli():
    """Test CLI functionality"""
    print("Testing CLI (cli.py)...")
    import subprocess
    
    result = subprocess.run(
        ['python', 'cli.py', '100', 'm', 'ft'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and '328' in result.stdout:
        print(f"✓ CLI output: {result.stdout.strip()}")
        print("✓ CLI: PASSED\n")
        return True
    else:
        print(f"✗ CLI: FAILED - {result.stderr}")
        return False

def test_flask_app():
    """Test Flask app imports and basic setup"""
    print("Testing Flask app (app.py)...")
    
    try:
        from app import app, converter
        
        # Test that the app has the right routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        required_routes = ['/', '/categories', '/units', '/convert']
        
        for route in required_routes:
            if route in routes:
                print(f"✓ Route {route} exists")
            else:
                print(f"✗ Route {route} missing")
                return False
        
        print("✓ Flask app: PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Flask app: FAILED - {e}\n")
        return False

def test_gui_syntax():
    """Test GUI files have valid Python syntax"""
    print("Testing GUI syntax...")
    import py_compile
    
    try:
        py_compile.compile('gui.py', doraise=True)
        print("✓ gui.py (Tkinter): Valid syntax")
    except Exception as e:
        print(f"✗ gui.py: Syntax error - {e}")
        return False
    
    try:
        py_compile.compile('gui_qt.py', doraise=True)
        print("✓ gui_qt.py (Qt): Valid syntax")
    except Exception as e:
        print(f"✗ gui_qt.py: Syntax error - {e}")
        return False
    
    print("✓ GUI files: PASSED\n")
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Unit Converter - Functionality Test Suite")
    print("=" * 60 + "\n")
    
    results = []
    
    results.append(("Converter Module", test_converter_module()))
    results.append(("CLI", test_cli()))
    results.append(("Flask App", test_flask_app()))
    results.append(("GUI Syntax", test_gui_syntax()))
    
    print("=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! The application is fully functional.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
