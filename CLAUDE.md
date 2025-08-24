# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Unit Converter is a multi-interface application for converting between different units of measurement. It provides three ways to interact with the conversion functionality: a web application, desktop GUIs, and a command-line interface.

## Development Commands

### Running the Application

```bash
# Web application (Flask)
python app.py

# Command-line interface
python cli.py <value> <from_unit> <to_unit>
# Example: python cli.py 100 m ft

# Desktop GUI (Tkinter)
python gui.py

# Desktop GUI (Qt)
python gui_qt.py
```

### Setup and Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for Tailwind CSS)
npm install
```

## Architecture

### Core Components

1. **converter.py**: Contains the `UnitConverter` class with all conversion logic
   - Supports length, temperature, and currency conversions
   - Currency conversions use real-time rates via forex-python
   - Centralized conversion logic used by all interfaces

2. **app.py**: Flask web application
   - REST API endpoints: `/categories`, `/units`, `/convert`
   - Serves HTML interface with Tailwind CSS styling
   - Returns JSON responses for AJAX requests

3. **cli.py**: Command-line interface
   - Simple argument parsing for quick conversions
   - Usage: `python cli.py <value> <from_unit> <to_unit>`

4. **gui.py / gui_qt.py**: Desktop GUI applications
   - Two implementations: Tkinter (with ttkthemes) and PyQt5
   - Provides dropdown-based unit selection

### Supported Conversions

- **Length**: mm, cm, m, km, in, ft, yd, mi
- **Temperature**: celsius, fahrenheit, kelvin
- **Currency**: 36 international currencies (USD, EUR, JPY, GBP, etc.)

### API Structure

The Flask application provides these endpoints:
- `GET /` - Main web interface
- `GET /categories` - Returns available conversion categories as JSON
- `GET /units?category=<category>` - Returns units for a specific category
- `POST /convert` - Performs conversion (accepts form data: value, from_unit, to_unit)

## Technology Stack

- **Backend**: Python with Flask
- **Frontend**: HTML with Tailwind CSS v4.0.0
- **CSS Processing**: PostCSS with Autoprefixer
- **Currency Data**: forex-python library for real-time exchange rates
- **GUI Frameworks**: Tkinter with ttkthemes, PyQt5

## Deployment

The application is deployed to Azure Web Apps as `at-unit-converter` using GitHub Actions CI/CD pipeline (see `.github/workflows/main_at-unit-converter.yml`).

## Notes

- Volume conversions are planned but not yet implemented
- Dark mode functionality is work in progress
- No test suite currently exists
- Dependencies have been updated to address security vulnerabilities (Snyk fixes)