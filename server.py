from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from answer_engine import chatbot_query

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message']
        bot_response = chatbot_query(user_message)
        
        return jsonify({
            'response': bot_response,
            'status': 'success'
        })
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'error': 'Sorry, I encountered an error processing your request.',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
