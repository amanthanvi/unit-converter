# Testing Guide

This document describes how to verify that all components of the Unit Converter application are working correctly.

## Quick Test

Run the automated test suite:

```bash
python test_functionality.py
```

This will test:
- ✓ Core converter module
- ✓ CLI interface
- ✓ Flask web app
- ✓ GUI syntax validation

## Manual Testing

### 1. Web Application (Flask)

**Start the server:**
```bash
python app.py
```

**Access the app:**
Open http://localhost:5000 in your browser

**Test conversions:**
- Select a category (e.g., Length)
- Enter a value and choose units
- Verify the conversion result

**Test API endpoints:**
```bash
# Get categories
curl http://localhost:5000/categories

# Get units for a category
curl http://localhost:5000/units?category=length

# Perform conversion
curl -X POST http://localhost:5000/convert \
  -d "value=100&from_unit=m&to_unit=ft"
```

### 2. Command-Line Interface

```bash
# Length conversion
python cli.py 100 m ft

# Temperature conversion
python cli.py 32 fahrenheit celsius

# Weight conversion
python cli.py 5 kg lb
```

### 3. GUI Applications

**Note:** GUI applications require additional dependencies that are not included by default:

**For Tkinter GUI:**
```bash
# Install tkinter (system-specific)
# Ubuntu/Debian: sudo apt-get install python3-tk
# Then install ttkthemes:
pip install ttkthemes

# Run the GUI
python gui.py
```

**For Qt GUI:**
```bash
# Install PyQt5
pip install PyQt5

# Run the GUI
python gui_qt.py
```

## Build CSS (Development)

```bash
# Install Node.js dependencies
npm install

# Build CSS once
npm run build:css

# Watch mode (rebuilds on changes)
npm run watch:css
```

## Troubleshooting

### Import Errors
- Ensure all Python dependencies are installed: `pip install -r requirements.txt`
- For GUI apps, install optional dependencies as shown above

### CSS Not Loading
- Run `npm install` to install Node.js dependencies
- Build CSS with `npm run build:css`

### Port Already in Use
- Change the port in app.py or set the PORT environment variable:
  ```bash
  PORT=8080 python app.py
  ```

### Currency Conversion Fails
- The app requires internet connectivity to fetch real-time exchange rates
- Rates are cached for 1 hour to reduce API calls

## Success Criteria

All components are working if:
- ✅ Web app loads and performs conversions
- ✅ API endpoints return valid JSON responses
- ✅ CLI performs conversions correctly
- ✅ GUI files have valid syntax (can load without errors)
- ✅ CSS builds without errors
