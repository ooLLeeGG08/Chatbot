import http.server
import socketserver
import os
from google_search import chatbot_query

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        # If requesting the root, serve index.html
        if self.path == '/':
            self.path = '/index.html'
        
        # Serve static files
        return super().do_GET()

    def do_POST(self):
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            content_length = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_length)
            
            # Decode the query from bytes to string
            query = post_body.decode('utf-8')
            self.end_headers()
            
            print('User query:', query)
            
            if not query.strip():
                response = "Please ask me something!"
            else:
                response = chatbot_query(query)
            
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            print(f"Error processing request: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"Sorry, I encountered an error processing your request.")

with socketserver.TCPServer(('', PORT), Handler) as httpd:
    print(f'Server running at http://localhost:{PORT}/')
    print('Press Ctrl+C to stop the server')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    httpd.server_close()
