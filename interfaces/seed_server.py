import http.server
import socketserver
import os
import json

# Load server IP from config.json
with open('../config.json', 'r') as config_file:
    config = json.load(config_file)
server_ip = config['server_ip']

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer((server_ip, PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()