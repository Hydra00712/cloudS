#!/usr/bin/env python3
"""
Minimal HTTP server to serve index.html
No Streamlit complexity, just static file serving
"""
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

class HtmlHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

if __name__ == '__main__':
    # Get port from environment or default to 8000
    port = int(os.getenv('PORT', 8000))
    
    # Change to repo root directory
    os.chdir('/home/site/wwwroot') if os.path.exists('/home/site/wwwroot') else None
    
    server = HTTPServer(('0.0.0.0', port), HtmlHandler)
    print(f"✅ Server running on port {port}")
    print(f"📁 Serving from: {os.getcwd()}")
    server.serve_forever()
