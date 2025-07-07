from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs
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
            
            # Parse form data
            parsed_data = parse_qs(post_data)
            
            value = float(parsed_data.get('value', [None])[0])
            from_unit = parsed_data.get('from_unit', [None])[0]
            to_unit = parsed_data.get('to_unit', [None])[0]
            
            if not all([value is not None, from_unit, to_unit]):
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = {'error': 'Missing required parameters'}
                self.wfile.write(json.dumps(error_response).encode())
                return
            
            # Initialize converter
            converter = UnitConverter()
            
            # Perform conversion
            result = converter.convert(value, from_unit, to_unit)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode())
            
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
            
            error_response = {'error': 'Conversion failed: ' + str(e)}
            self.wfile.write(json.dumps(error_response).encode())