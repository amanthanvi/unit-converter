from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add parent directory to path to import converter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from converter import UnitConverter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Initialize converter
            converter = UnitConverter()
            
            # Get categories
            categories = converter.get_categories()
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(categories).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())