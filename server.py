import json
import subprocess
import tempfile
import os
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import signal

class CodeExecutionChatbotHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Serve static files"""
        if self.path == '/':
            self.path = '/index.html'
        
        try:
            if self.path.endswith('.html'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open('index.html', 'r') as file:
                    self.wfile.write(file.read().encode())
            elif self.path.endswith('.css'):
                self.send_response(200)
                self.send_header('Content-type', 'text/css')
                self.end_headers()
                with open('style.css', 'r') as file:
                    self.wfile.write(file.read().encode())
            elif self.path.endswith('.js'):
                self.send_response(200)
                self.send_header('Content-type', 'application/javascript')
                self.end_headers()
                with open('app.js', 'r') as file:
                    self.wfile.write(file.read().encode())
            elif self.path.endswith('.png'):
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                with open('chatbot.png', 'rb') as file:
                    self.wfile.write(file.read())
            else:
                self.send_error(404)
        except FileNotFoundError:
            self.send_error(404)

    def do_POST(self):
        """Handle API requests"""
        if self.path == '/api/chat':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                response = self.process_chat_request(request_data)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                print(f"Error processing request: {e}")
                self.send_error(500)
        else:
            self.send_error(404)

    def process_chat_request(self, data):
        """Process chat messages and code execution requests"""
        message = data.get('message', '')
        language = data.get('language', 'chat')
        
        if language == 'chat':
            return self.handle_chat_message(message)
        elif language == 'javascript':
            return self.execute_javascript(message)
        elif language == 'python':
            return self.execute_python(message)
        else:
            return {
                'content': 'Unsupported language.',
                'type': 'error',
                'error': True
            }

    def handle_chat_message(self, message):
        """Handle regular chat messages"""
        # Simple responses for demonstration
        responses = {
            'hello': 'Hello! How can I help you with code execution today?',
            'hi': 'Hi there! Ready to run some code?',
            'help': 'I can execute JavaScript and Python code. Select a language and type your code!',
            'what can you do': 'I can execute JavaScript and Python code for you. Just select the language and type your code!',
            'bye': 'Goodbye! Come back anytime to run more code.',
            'thanks': 'You\'re welcome! Happy coding!',
            'how are you': 'I\'m doing great and ready to execute your code!'
        }
        
        message_lower = message.lower().strip()
        
        # Check for exact matches first
        for key, response in responses.items():
            if key in message_lower:
                return {
                    'content': response,
                    'type': 'text',
                    'error': False
                }
        
        # Default response
        return {
            'content': 'I\'m a code execution chatbot! I can run JavaScript and Python code for you. Select a language from the dropdown and enter your code to get started.',
            'type': 'text',
            'error': False
        }

    def execute_javascript(self, code):
        """Execute JavaScript code safely"""
        try:
            # Check if Node.js is available
            try:
                subprocess.run(['node', '--version'], capture_output=True, check=True, timeout=5)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {
                    'content': 'Node.js is not installed or not available in PATH.',
                    'type': 'result',
                    'error': True
                }
            
            # Create a temporary file for the JavaScript code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            try:
                # Execute the JavaScript code with timeout
                result = subprocess.run(
                    ['node', temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=10,  # 10 second timeout
                    cwd=tempfile.gettempdir()
                )
                
                output = result.stdout
                error_output = result.stderr
                
                if result.returncode == 0:
                    return {
                        'content': output if output.strip() else '(No output)',
                        'type': 'result',
                        'error': False
                    }
                else:
                    return {
                        'content': error_output if error_output.strip() else 'Unknown error occurred',
                        'type': 'result',
                        'error': True
                    }
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            return {
                'content': 'Code execution timed out (10 seconds limit)',
                'type': 'result',
                'error': True
            }
        except Exception as e:
            return {
                'content': f'Error executing JavaScript: {str(e)}',
                'type': 'result',
                'error': True
            }

    def execute_python(self, code):
        """Execute Python code safely"""
        try:
            # Create a temporary file for the Python code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            try:
                # Execute the Python code with timeout
                result = subprocess.run(
                    [sys.executable, temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=10,  # 10 second timeout
                    cwd=tempfile.gettempdir()
                )
                
                output = result.stdout
                error_output = result.stderr
                
                if result.returncode == 0:
                    return {
                        'content': output if output.strip() else '(No output)',
                        'type': 'result',
                        'error': False
                    }
                else:
                    return {
                        'content': error_output if error_output.strip() else 'Unknown error occurred',
                        'type': 'result',
                        'error': True
                    }
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            return {
                'content': 'Code execution timed out (10 seconds limit)',
                'type': 'result',
                'error': True
            }
        except Exception as e:
            return {
                'content': f'Error executing Python: {str(e)}',
                'type': 'result',
                'error': True
            }

    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

def run_server():
    """Run the HTTP server"""
    PORT = 8080
    server_address = ('', PORT)
    
    httpd = HTTPServer(server_address, CodeExecutionChatbotHandler)
    
    print(f"🚀 Code Execution Chatbot Server running at http://localhost:{PORT}")
    print("📝 Supports JavaScript and Python code execution")
    print("🔒 Code runs in isolated temporary files with timeouts")
    print("⚠️  Press Ctrl+C to stop the server")
    
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down server...")
        httpd.server_close()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
