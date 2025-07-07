import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from converter import UnitConverter

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """
        Handle POST request to perform batch unit conversions.
        """
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''
            
            # Try to parse as JSON first (for modern API usage)
            try:
                data = json.loads(body)
                value = float(data.get('value'))
                from_unit = data.get('from_unit')
                to_units = data.get('to_units', [])
            except json.JSONDecodeError:
                # Fall back to form data parsing
                parsed_data = parse_qs(body)
                value = float(parsed_data.get('value', [None])[0])
                from_unit = parsed_data.get('from_unit', [None])[0]
                to_units = parsed_data.get('to_units[]', [])  # Array notation for form data
            
            if not all([value is not None, from_unit, to_units]):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing required parameters'}).encode('utf-8'))
                return
            
            # Initialize converter
            converter = UnitConverter()
            
            # Perform batch conversion
            results = converter.batch_convert(value, from_unit, to_units)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json.dumps({'conversions': results}).encode('utf-8'))
            
        except ValueError as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Batch conversion failed: ' + str(e)}).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS request for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()