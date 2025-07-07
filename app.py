from flask import Flask, render_template, request, jsonify
from converter import UnitConverter
import os
from datetime import datetime
import json

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize converter
converter = UnitConverter()

@app.route('/')
def index():
    """Render the main application"""
    return render_template('index.html')

@app.route('/categories')
def get_categories():
    """Get all available conversion categories"""
    return jsonify(converter.get_categories())

@app.route('/units')
def get_units():
    """Get units for a specific category"""
    category = request.args.get('category')
    if not category:
        return jsonify({'error': 'Category parameter is required'}), 400
    
    units = converter.get_units(category)
    if not units:
        return jsonify({'error': 'Invalid category'}), 404
    
    return jsonify(units)

@app.route('/convert', methods=['POST'])
def convert():
    """Perform unit conversion"""
    try:
        value = float(request.form.get('value'))
        from_unit = request.form.get('from_unit')
        to_unit = request.form.get('to_unit')
        
        if not all([value, from_unit, to_unit]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        result = converter.convert(value, from_unit, to_unit)
        return jsonify(result)
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Conversion failed: ' + str(e)}), 500

@app.route('/quick-conversions')
def get_quick_conversions():
    """Get quick conversions for a given value and unit"""
    try:
        value = float(request.args.get('value'))
        unit = request.args.get('unit')
        
        if not all([value, unit]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        conversions = converter.get_quick_conversions(value, unit)
        return jsonify(conversions)
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to get quick conversions: ' + str(e)}), 500

# PWA Routes
@app.route('/static/manifest.json')
def manifest():
    """Serve PWA manifest"""
    manifest_data = {
        "name": "Unit Converter Pro",
        "short_name": "UnitConvert",
        "description": "Smart unit conversions with real-world context",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#3b82f6",
        "icons": [
            {
                "src": "/static/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/static/icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    return jsonify(manifest_data)

@app.route('/service-worker.js')
def service_worker():
    """Serve service worker for offline functionality"""
    return app.send_static_file('service-worker.js'), 200, {'Content-Type': 'application/javascript'}

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

# Development server
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)