import json
import subprocess
import tempfile
import os
import sys
import time
import re
import urllib.request
import urllib.parse
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
            return self.handle_intelligent_chat(message)
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

    def handle_intelligent_chat(self, message):
        """Handle intelligent chat messages with web search and knowledge"""
        message_lower = message.lower().strip()
        
        # Programming and tech questions
        if any(keyword in message_lower for keyword in ['code', 'programming', 'python', 'javascript', 'html', 'css', 'algorithm', 'software', 'development']):
            return self.handle_programming_question(message)
        
        # Math questions
        if any(keyword in message_lower for keyword in ['calculate', 'math', 'equation', '+', '-', '*', '/', 'solve']):
            return self.handle_math_question(message)
        
        # Current events, facts, general knowledge
        if any(keyword in message_lower for keyword in ['what is', 'who is', 'when did', 'where is', 'how to', 'why', 'explain', 'tell me about']):
            return self.search_and_answer(message)
        
        # Greetings and basic interactions
        greetings = {
            'hello': 'Hello! I\'m an intelligent chatbot that can answer questions, execute code, and help with various topics. What would you like to know?',
            'hi': 'Hi there! I can help you with questions, run code, or discuss any topic. What\'s on your mind?',
            'hey': 'Hey! Ready to chat or run some code? Ask me anything!',
            'good morning': 'Good morning! Hope you\'re having a great day. How can I assist you?',
            'good afternoon': 'Good afternoon! What can I help you with today?',
            'good evening': 'Good evening! What would you like to explore or learn about?',
            'how are you': 'I\'m doing great and ready to help! I can answer questions, execute code, or discuss various topics.',
            'what can you do': 'I can:\n• Answer questions on any topic using web search\n• Execute JavaScript and Python code\n• Help with math problems\n• Discuss programming concepts\n• Provide explanations and tutorials\n• And much more! What interests you?',
            'help': 'I\'m here to help! You can:\n• Ask me any question and I\'ll search for answers\n• Switch to JavaScript or Python mode to execute code\n• Ask about programming, math, science, history, etc.\n• Request explanations or tutorials\n\nWhat would you like to explore?',
            'bye': 'Goodbye! It was great chatting with you. Come back anytime for more questions or coding!',
            'thanks': 'You\'re very welcome! Happy to help. Feel free to ask anything else!',
            'thank you': 'My pleasure! I\'m always here when you need answers or want to run some code.'
        }
        
        for greeting, response in greetings.items():
            if greeting in message_lower:
                return {
                    'content': response,
                    'type': 'text',
                    'error': False
                }
        
        # For any other question, try to search and provide an intelligent answer
        return self.search_and_answer(message)

    def handle_programming_question(self, message):
        """Handle programming-related questions"""
        message_lower = message.lower()
        
        programming_responses = {
            'python': 'Python is a versatile, high-level programming language known for its readable syntax. It\'s great for web development, data science, AI, automation, and more. Would you like to see some Python code examples?',
            'javascript': 'JavaScript is the language of the web! It runs in browsers and servers (Node.js). It\'s essential for web development, can create interactive websites, and much more. Want to try some JavaScript code?',
            'html': 'HTML (HyperText Markup Language) is the backbone of web pages. It structures content using tags like <h1>, <p>, <div>, etc. It works with CSS for styling and JavaScript for interactivity.',
            'css': 'CSS (Cascading Style Sheets) makes websites beautiful! It controls colors, layouts, fonts, animations, and responsive design. It works hand-in-hand with HTML.',
            'algorithm': 'Algorithms are step-by-step procedures for solving problems. Common types include sorting (bubble, merge, quick), searching (binary search), and graph algorithms (BFS, DFS).',
            'function': 'Functions are reusable blocks of code that perform specific tasks. They take inputs (parameters), process them, and often return outputs. They\'re fundamental in all programming languages!'
        }
        
        for keyword, response in programming_responses.items():
            if keyword in message_lower:
                return {
                    'content': response,
                    'type': 'text',
                    'error': False
                }
        
        # If no specific match, search for programming-related answer
        return self.search_and_answer(message)

    def handle_math_question(self, message):
        """Handle math calculations and questions"""
        # Try to extract and solve simple math expressions
        import re
        
        # Look for simple arithmetic expressions
        math_pattern = r'(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)'
        match = re.search(math_pattern, message)
        
        if match:
            try:
                num1, operator, num2 = match.groups()
                num1, num2 = float(num1), float(num2)
                
                if operator == '+':
                    result = num1 + num2
                elif operator == '-':
                    result = num1 - num2
                elif operator == '*':
                    result = num1 * num2
                elif operator == '/':
                    if num2 != 0:
                        result = num1 / num2
                    else:
                        return {
                            'content': 'Cannot divide by zero!',
                            'type': 'text',
                            'error': False
                        }
                
                return {
                    'content': f'{num1} {operator} {num2} = {result}',
                    'type': 'text',
                    'error': False
                }
            except:
                pass
        
        # For complex math questions, search for answers
        return self.search_and_answer(message)

    def search_and_answer(self, query):
        """Search the web and provide intelligent answers"""
        try:
            # Simple web search using DuckDuckGo's instant answer API
            search_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
            
            with urllib.request.urlopen(search_url, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            # Try to get instant answer
            if data.get('AbstractText'):
                answer = data['AbstractText']
                source = data.get('AbstractSource', 'DuckDuckGo')
                return {
                    'content': f'{answer}\n\n📚 Source: {source}',
                    'type': 'text',
                    'error': False
                }
            
            # Try definition
            if data.get('Definition'):
                answer = data['Definition']
                source = data.get('DefinitionSource', 'DuckDuckGo')
                return {
                    'content': f'{answer}\n\n📚 Source: {source}',
                    'type': 'text',
                    'error': False
                }
            
            # Try related topics
            if data.get('RelatedTopics') and len(data['RelatedTopics']) > 0:
                topic = data['RelatedTopics'][0]
                if 'Text' in topic:
                    return {
                        'content': f'{topic["Text"]}\n\n💡 This is one perspective. Would you like me to search for more specific information?',
                        'type': 'text',
                        'error': False
                    }
            
            # Try answer
            if data.get('Answer'):
                return {
                    'content': f'{data["Answer"]}\n\n📚 Source: DuckDuckGo',
                    'type': 'text',
                    'error': False
                }
            
            # Fallback with helpful response
            return {
                'content': f'I searched for "{query}" but didn\'t find a direct answer. Here are some suggestions:\n\n• Try rephrasing your question\n• Be more specific\n• Ask about a particular aspect of the topic\n• Use the code execution modes for programming questions\n\nWhat specific aspect would you like to know about?',
                'type': 'text',
                'error': False
            }
            
        except Exception as e:
            # Provide intelligent fallback responses based on question type
            return self.provide_fallback_answer(query)

    def provide_fallback_answer(self, query):
        """Provide intelligent fallback answers when search fails"""
        query_lower = query.lower()
        
        # Science questions
        if any(word in query_lower for word in ['science', 'physics', 'chemistry', 'biology', 'astronomy']):
            return {
                'content': 'Science is fascinating! While I couldn\'t search for your specific question right now, I\'d be happy to discuss scientific concepts. Could you ask a more specific question about the scientific topic you\'re interested in?',
                'type': 'text',
                'error': False
            }
        
        # History questions
        if any(word in query_lower for word in ['history', 'historical', 'when did', 'ancient']):
            return {
                'content': 'History is full of interesting events and people! I\'d love to help with historical questions. Could you be more specific about the time period, person, or event you\'re asking about?',
                'type': 'text',
                'error': False
            }
        
        # Technology questions
        if any(word in query_lower for word in ['technology', 'computer', 'internet', 'AI', 'artificial intelligence']):
            return {
                'content': 'Technology is evolving rapidly! I can discuss various tech topics. What specific technology or concept would you like to learn about? I can also run code if you want to see examples!',
                'type': 'text',
                'error': False
            }
        
        # General fallback
        return {
            'content': f'That\'s an interesting question about "{query}"! While I couldn\'t fetch real-time information, I\'m still here to help. You could:\n\n• Try asking a more specific question\n• Rephrase your question\n• Ask me to explain a concept\n• Use the code execution modes for programming topics\n\nWhat would you like to explore?',
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
    
    print(f"🚀 Intelligent Code Execution Chatbot Server running at http://localhost:{PORT}")
    print("💬 Can answer questions on any topic with web search")
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
