import http.server
import socketserver
import os

PORT = int(os.environ.get("PORT", 8080))

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"G777 CLOUD BRAIN IS ALIVE! (Minimal Mode)")
        return

print(f"🚀 Starting Minimal Server on port {PORT}...")
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("✅ Serving forever...")
    httpd.serve_forever()
