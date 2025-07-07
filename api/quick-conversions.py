from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from converter import UnitConverter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse query parameters
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            
            value = query_params.get('value', [None])[0]
            unit = query_params.get('unit', [None])[0]
            
            if value:
                value = float(value)
            
            if not all([value is not None, unit]):
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = {'error': 'Missing required parameters'}
                self.wfile.write(json.dumps(error_response).encode())
                return
            
            # Initialize converter
            converter = UnitConverter()
            
            # Get quick conversions
            conversions = converter.get_quick_conversions(value, unit)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(conversions).encode())
            
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
            
            error_response = {'error': 'Failed to get quick conversions: ' + str(e)}
            self.wfile.write(json.dumps(error_response).encode())