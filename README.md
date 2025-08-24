# Unit Converter Pro
An Intelligent, Educational Unit Conversion Tool with Real-World Context

## Description

Unit Converter Pro is a completely redesigned unit conversion application that goes beyond simple conversions. It provides educational insights, real-world comparisons, and beautiful visualizations to make unit conversion more meaningful and engaging. The application offers multiple interfaces including a modern web app, desktop GUIs, and a CLI, catering to various user preferences and use cases.

### What Makes It Special

Unlike typical unit converters, this application:
- **Provides Context**: See how your conversions relate to real-world objects (e.g., "100 meters is about the length of a football field")
- **Teaches History**: Learn the fascinating origins of different units
- **Visualizes Data**: Interactive charts show the relationship between units
- **Remembers Your Work**: Full conversion history with favorites
- **Works Offline**: Progressive Web App with service worker caching
- **Respects Your Preferences**: Beautiful dark mode, keyboard shortcuts, and customizable interface

## Key Features

### 🎯 Core Functionality
- **9 Unit Categories**: Length, Weight, Temperature, Volume, Area, Speed, Time, Digital Storage, and Currency
- **80+ Units**: Comprehensive coverage of metric, imperial, and other unit systems
- **Real-Time Currency**: Live exchange rates for 36 major world currencies
- **Instant Conversion**: Real-time conversion as you type
- **Quick Conversions**: One-click access to common unit conversions
- **Batch Operations**: Convert to multiple units simultaneously

### 🎨 Enhanced User Experience
- **Modern UI**: Completely redesigned with Tailwind CSS 3.x
- **Smooth Animations**: Delightful micro-interactions and transitions
- **Dark Mode**: Eye-friendly dark theme with system preference detection
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Keyboard Shortcuts**: Power user features for efficiency
- **Copy to Clipboard**: One-click result copying

### 📚 Educational Features
- **Real-World Comparisons**: Understand measurements through everyday examples
- **Historical Context**: Learn the origins and evolution of units
- **Visual Comparisons**: Interactive charts powered by Chart.js
- **Conversion History**: Track and learn from past conversions
- **Favorites System**: Save frequently used conversions for quick access

### 🔧 Technical Features
- **Progressive Web App**: Install as a native app on any device
- **Offline Support**: Works without internet (except currency conversions)
- **API Architecture**: RESTful API ready for Vercel deployment
- **Modular Design**: Clean separation of concerns
- **Extensible**: Easy to add new units and categories

## Supported Conversions

### 📏 Length
- Metric: Millimeter (mm), Centimeter (cm), Meter (m), Kilometer (km)
- Imperial: Inch (in), Foot (ft), Yard (yd), Mile (mi)

### ⚖️ Weight
- Metric: Milligram (mg), Gram (g), Kilogram (kg), Metric Ton (ton)
- Imperial: Ounce (oz), Pound (lb), Stone (stone)

### 🌡️ Temperature
- Celsius (°C), Fahrenheit (°F), Kelvin (K)

### 🧪 Volume
- Metric: Milliliter (ml), Liter (l)
- US Units: Gallon (gal), Quart (qt), Pint (pt), Cup (cup), Fluid Ounce (fl_oz)
- Cooking: Tablespoon (tbsp), Teaspoon (tsp)

### 📐 Area
- Metric: Square Millimeter (mm²), Square Centimeter (cm²), Square Meter (m²), Square Kilometer (km²)
- Imperial: Square Inch (in²), Square Foot (ft²), Square Yard (yd²)
- Land: Acre, Hectare

### 🚀 Speed
- Meters per Second (m/s), Kilometers per Hour (km/h)
- Miles per Hour (mph), Knot, Mach

### ⏱️ Time
- Millisecond (ms), Second (s), Minute (min), Hour (hr)
- Day, Week, Month, Year

### 💾 Digital Storage
- Bit, Byte, Kilobyte (KB), Megabyte (MB)
- Gigabyte (GB), Terabyte (TB), Petabyte (PB)

### 💱 Currency
- 36 major world currencies with real-time exchange rates
- Cached rates for better performance

## Getting Started

### Requirements
- Python 3.8+
- Node.js 14+ (for building Tailwind CSS)
- pip (Python package manager)
- npm (Node package manager)

### Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/unit-converter.git
cd unit-converter
```

2. **Install dependencies:**
```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
npm install
```

3. **Build CSS:**
```bash
npm run build:css
```

4. **Run the application:**
```bash
# Development mode (with hot reload)
npm run dev

# Or production mode
python app.py
```

5. **Open in browser:**
Navigate to `http://localhost:5000`

## Usage

### Web Application
The web application provides the full feature set with a modern, responsive interface:

1. Select a category (e.g., Length, Weight, Currency)
2. Enter a value in the "From" field
3. Select source and target units
4. See instant results with:
   - Converted value
   - Real-world comparisons
   - Historical context
   - Visual chart
   - Quick conversions to other common units

### Desktop Applications

#### Tkinter GUI:
```bash
python gui.py
```
Simple, lightweight desktop interface.

#### Qt GUI:
```bash
python gui_qt.py
```
More advanced desktop interface with additional features.

### Command Line Interface
Perfect for quick conversions:
```bash
python cli.py <value> <from_unit> <to_unit>

# Examples:
python cli.py 100 m ft      # Convert 100 meters to feet
python cli.py 72 fahrenheit celsius  # Convert temperature
python cli.py 50 USD EUR    # Convert currency
```

## Keyboard Shortcuts

- `Ctrl/Cmd + S`: Swap units
- `Ctrl/Cmd + C`: Copy result to clipboard
- `Ctrl/Cmd + H`: Toggle conversion history
- `Ctrl/Cmd + D`: Toggle dark mode
- `Ctrl/Cmd + B`: Show batch conversion (all units)
- `Ctrl/Cmd + Shift + S`: Share conversion

## Deployment

### Deploy to Vercel (Recommended)

This application is optimized for deployment on Vercel with serverless functions.

#### Via Vercel Dashboard:
1. Push your code to GitHub
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "New Project"
4. Import your GitHub repository
5. Vercel will auto-detect the configuration
6. Click "Deploy"

#### Via Vercel CLI:
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Follow the prompts
```

Your app will be available at `https://your-project-name.vercel.app`

### Architecture

```
/
├── api/                    # Serverless functions
│   ├── categories.py      # GET /api/categories
│   ├── units.py          # GET /api/units
│   ├── convert.py        # POST /api/convert
│   └── quick-conversions.py
├── static/               # Static assets
│   ├── css/             # Compiled Tailwind CSS
│   ├── manifest.json    # PWA manifest
│   └── service-worker.js
├── templates/           # Flask templates (local dev)
├── index.html          # Main app (Vercel)
├── converter.py        # Core conversion logic
├── app.py             # Flask app (local dev)
└── vercel.json        # Vercel configuration
```

## API Reference

### Get Categories
```http
GET /api/categories
```
Returns all available conversion categories.

### Get Units
```http
GET /api/units?category={category}
```
Returns units for a specific category.

### Convert Units
```http
POST /api/convert
Content-Type: application/x-www-form-urlencoded

value=100&from_unit=m&to_unit=ft
```
Performs unit conversion with educational context.

### Quick Conversions
```http
GET /api/quick-conversions?value={value}&unit={unit}
```
Returns common conversions for the given value and unit.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0). See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Real-time currency data: [forex-python](https://github.com/MicroPyramid/forex-python)
- UI Framework: [Tailwind CSS](https://tailwindcss.com)
- Interactivity: [Alpine.js](https://alpinejs.dev)
- Visualizations: [Chart.js](https://www.chartjs.org)
- Icons: Native emoji sets
- Deployment: [Vercel](https://vercel.com)

## Roadmap

- [ ] Add more unit categories (Energy, Pressure, etc.)
- [ ] Implement unit conversion formulas visualization
- [ ] Add conversion precision settings
- [ ] Create mobile apps (React Native)
- [ ] Add API rate limiting
- [ ] Implement user accounts for cloud sync
- [ ] Add more languages
- [ ] Create browser extension

---

Made with ❤️ by developers who believe unit conversion should be more than just numbers.
## Stabilization v1 (serverless API on Vercel)

This release introduces a versioned API under `/api/v1`, unified JSON response envelopes, basic structured logging, dependency pinning for Python HTTP stack, CI, tests, and a currency-rate fallback for resiliency.

- Runtime/config:
  - Vercel Python functions pinned in [vercel.json](vercel.json)
  - New v1 handlers in `api/v1/*` using a common utility [api/_common.py](api/_common.py)
  - SPA now targets `/api/v1/*` in [index.html](index.html)
- JSON response envelope (v1):
  - Success: `{ "ok": true, "data": &lt;payload&gt; }`
  - Error: `{ "ok": false, "error": { "code": "string", "message": "string", "details": "optional" } }`
- Endpoints:
  - GET `/api/v1/health` → `{ ok:true, data:{status:"ok"} }`
  - GET `/api/v1/categories`
  - GET `/api/v1/units?category=...`
  - POST `/api/v1/convert` body JSON `{ value, from_unit, to_unit }`
  - GET `/api/v1/quick-conversions?value=...&amp;unit=...`
  - POST `/api/v1/batch-convert` body JSON `{ value, from_unit, to_units:[...] }`
- CORS:
  - Controlled via `ALLOW_ORIGIN` env (default `*`). Set to your Vercel preview/prod URLs in those environments.
- Currency fallback:
  - Live rates via `forex-python` with in-memory cache per invocation
  - Fallback file [data/forex_fallback.json](data/forex_fallback.json) used if live fetch fails
  - Optional `FOREX_FALLBACK_JSON` env to point to a custom JSON file
- CI and tests:
  - GitHub Actions at [.github/workflows/ci.yml](.github/workflows/ci.yml): build CSS, run pytest, pip-audit, SBOM
  - Unit tests: [tests/test_converter.py](tests/test_converter.py), [tests/test_currency_fallback.py](tests/test_currency_fallback.py)
- Tooling:
  - Code style and lint via [pyproject.toml](pyproject.toml) and [.pre-commit-config.yaml](.pre-commit-config.yaml)
  - Dev Container: [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json)
  - Tailwind purge targets include [index.html](index.html) in [tailwind.config.js](tailwind.config.js)

### Deprecation policy (legacy `/api`)
- Legacy `/api/*` remains available for at least 90 days from this change.
- New clients should use `/api/v1/*`. After the window, `/api/*` may be removed or aliased to v1.

### Environment variables
- `ALLOW_ORIGIN` — CORS allowlist origin (defaults to `*`)
- `FOREX_FALLBACK_JSON` — path to fallback JSON with USD-based rates (defaults to `data/forex_fallback.json`)

### Local development (no auth; SQLite only if needed later)
- Build CSS:
  - `npm ci &amp;&amp; npm run build:css`
- Run tests:
  - `pip install -r api/requirements.txt pytest`
  - `pytest -q`
- Vercel (recommended): `vercel dev` (requires Vercel CLI)
- Flask app in [app.py](app.py) is for dev-only; production uses Vercel serverless in `api/` and `api/v1/`.

### Observability and security
- Structured JSON logs emitted by serverless handlers (request_id, path, status, duration placeholder)
- Dependency pins in [api/requirements.txt](api/requirements.txt) (requests, urllib3)
- SBOM generated via CI (Anchore action)

### Notes
- If deploying to Vercel, set Project Environment Variables:
  - Preview/Production: `ALLOW_ORIGIN=https://&lt;your-domain&gt;` (replace as needed)
  - Optional: `FOREX_FALLBACK_JSON` for a custom fallback