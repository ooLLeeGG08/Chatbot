# AI ChatBot

A modern, responsive web-based chatbot that answers small talk and simple arithmetic directly, and falls back to the Gemini API for everything else.

## Features

- Modern Flask backend with a JSON API endpoint
- Responsive UI with a light/dark mode toggle
- CORS support for cross-origin requests
- Proper error handling and validation

## 🚀 Quick Start

### Local Development

1. **Run with the startup script (Recommended)**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

2. **Manual installation**
   ```bash
   pip install --break-system-packages -r requirements.txt
   export GEMINI_API_KEY=your_api_key_here
   python3 server.py
   ```
   Get a free key at [Google AI Studio](https://aistudio.google.com/apikey). You can also copy `.env.example` to `.env` and set it there instead of exporting it.

3. **Access the chatbot**
   Open your browser and go to: `http://localhost:8080`

## 🌐 Deployment Options (Get Your Own URL)

All options below require setting `GEMINI_API_KEY` as an environment variable on the platform — never commit it to the repo.

### Option 1: Heroku (Recommended)

1. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Create a new Heroku app:
   ```bash
   heroku create your-chatbot-name
   ```
3. Set the API key:
   ```bash
   heroku config:set GEMINI_API_KEY=your_api_key_here
   ```
4. Deploy:
   ```bash
   git add .
   git commit -m "Deploy chatbot"
   git push heroku main
   ```
5. **Your chatbot URL**: `https://your-chatbot-name.herokuapp.com`

### Option 2: Railway

1. Connect your GitHub repository to [Railway](https://railway.app)
2. Railway will automatically detect the `Procfile` and deploy
3. Under the project's **Variables**, add `GEMINI_API_KEY`
4. **Your chatbot URL**: `https://your-app.railway.app`

### Option 3: Render

1. Connect your GitHub repository to [Render](https://render.com)
2. Create a new Web Service with these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn server:app`
3. Under **Environment**, add `GEMINI_API_KEY`
4. **Your chatbot URL**: `https://your-app.onrender.com`

### Option 4: Docker (Any Platform)

```bash
# Build and run with Docker
docker build -t my-chatbot .
docker run -p 8080:8080 -e GEMINI_API_KEY=your_api_key_here my-chatbot

# Or use docker-compose (set GEMINI_API_KEY in your shell or a .env file first)
docker-compose up
```

## 📁 Project Structure

```
chatbot/
├── server.py              # Flask backend server
├── app.js                 # Frontend JavaScript
├── index.html             # Main HTML page
├── style.css              # Modern CSS styling
├── answer_engine.py       # Small talk, calculator, and Gemini API integration
├── chatbot.png           # Chatbot avatar image
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
├── Dockerfile            # Docker container setup
├── docker-compose.yml    # Docker compose configuration
├── runtime.txt           # Python version specification
├── start.sh              # Local startup script
└── README.md             # This file
```

## 🔗 API Endpoints

- `GET /` - Serves the main chatbot interface
- `POST /api/chat` - Chatbot API endpoint
  - **Request Body**: `{"message": "your question"}`
  - **Response**: `{"response": "bot answer", "status": "success"}`

## 🔧 How It Works

1. **User Input**: User types a question in the web interface
2. **API Call**: Frontend sends the question to `/api/chat` endpoint
3. **Answer Resolution** (`answer_engine.py`), in order:
   - Small talk (greetings, thanks, etc.) matched against a fixed phrase list
   - Simple arithmetic, evaluated safely via a restricted AST parser
   - Otherwise, a question answered by the Gemini API (`gemini-flash-latest`, Google's current fast/low-cost model)
4. **Response**: Returns the resolved answer to the user, or a fallback message if nothing matched

## 🎛️ Customization

### Changing the UI
Edit `style.css` to modify colors, fonts, and layout. The current design uses:
- Gradient background: `#667eea` to `#764ba2`
- Modern glassmorphism effects
- Responsive design for all screen sizes

### Modifying Answer Behavior
Edit `answer_engine.py` to change small talk phrases, calculator behavior, or the Gemini system prompt.

### Adding Features
The Flask server in `server.py` can be extended with additional endpoints.

## 🔍 Testing

1. **Web Interface**: Visit `http://localhost:8080`
2. **API Test**:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
   -d '{"message":"What is the capital of France?"}' \
   http://localhost:8080/api/chat
   ```

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Change the port in `server.py` or kill the existing process
   - `sudo lsof -t -i tcp:8080 | xargs kill -9`

2. **Answers fall back to "cannot think of a reply"**
   - This means `GEMINI_API_KEY` is missing or invalid, or the Gemini API request failed. Check the server logs for an `answer_engine error` line with the specific cause.

3. **Deployment Issues**
   - Make sure all files are committed to git
   - Check that `requirements.txt` includes all dependencies
   - Verify your deployment platform supports Python 3.11+