from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from urllib.parse import parse_qs

# Add parent directory to path to import converter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from converter import UnitConverter

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # Try to parse as JSON first (for modern API usage)
            try:
                data = json.loads(post_data)
                value = float(data.get('value'))
                from_unit = data.get('from_unit')
                to_units = data.get('to_units', [])
            except:
                # Fall back to form data parsing
                parsed_data = parse_qs(post_data)
                value = float(parsed_data.get('value', [None])[0])
                from_unit = parsed_data.get('from_unit', [None])[0]
                to_units = parsed_data.get('to_units[]', [])  # Array notation for form data
            
            if not all([value is not None, from_unit, to_units]):
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = {'error': 'Missing required parameters'}
                self.wfile.write(json.dumps(error_response).encode())
                return
            
            # Initialize converter
            converter = UnitConverter()
            
            # Perform batch conversion
            results = converter.batch_convert(value, from_unit, to_units)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({'conversions': results}).encode())
            
        except ValueError as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {'error': 'Batch conversion failed: ' + str(e)}
            self.wfile.write(json.dumps(error_response).encode())