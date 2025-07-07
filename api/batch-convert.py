import json
import cgi
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from converter import UnitConverter

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """
        Handle POST request to perform batch unit conversions.
        """
        try:
            # Get content type
            content_type = self.headers.get('Content-Type', '')
            
            # Initialize variables
            value = None
            from_unit = None
            to_units = []
            
            if 'multipart/form-data' in content_type:
                # Parse multipart form data
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                value = form.getvalue('value')
                from_unit = form.getvalue('from_unit')
                # Handle array of to_units
                if 'to_units[]' in form:
                    # Handle array notation from form data
                    to_units = form.getlist('to_units[]')
                elif 'to_units' in form:
                    # Handle single value or comma-separated values
                    to_units_value = form.getvalue('to_units')
                    if isinstance(to_units_value, list):
                        to_units = to_units_value
                    elif isinstance(to_units_value, str):
                        # Check if it's comma-separated
                        if ',' in to_units_value:
                            to_units = [unit.strip() for unit in to_units_value.split(',')]
                        else:
                            to_units = [to_units_value]
            else:
                # Read request body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''
                
                # Try to parse as JSON first
                if 'application/json' in content_type:
                    try:
                        data = json.loads(body)
                        value = data.get('value')
                        from_unit = data.get('from_unit')
                        to_units = data.get('to_units', [])
                    except (json.JSONDecodeError, ValueError):
                        pass
                else:
                    # Fall back to URL-encoded form data parsing
                    parsed_data = parse_qs(body)
                    value = parsed_data.get('value', [None])[0] if 'value' in parsed_data else None
                    from_unit = parsed_data.get('from_unit', [None])[0] if 'from_unit' in parsed_data else None
                    to_units = parsed_data.get('to_units[]', [])  # Array notation for form data
            
            if not all([value is not None, from_unit, to_units]):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'Missing required parameters. Got value={value}, from_unit={from_unit}, to_units={to_units}'}).encode('utf-8'))
                return
            
            # Convert value to float
            try:
                value = float(value)
            except (TypeError, ValueError):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'Invalid value: {value}'}).encode('utf-8'))
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