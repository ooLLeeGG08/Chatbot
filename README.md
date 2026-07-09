# AI ChatBot - Powered by Google Search

A modern, responsive web-based chatbot that uses Google Search to provide intelligent answers to user questions.

## 🎉 Status: FULLY FUNCTIONAL & READY TO DEPLOY

Your chatbot has been completely fixed and modernized! It's now running with:
- Modern Flask backend with proper API endpoints
- Beautiful, responsive UI with gradient design
- CORS support for cross-origin requests
- Proper error handling and validation
- Multiple deployment options ready

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
   python3 server.py
   ```

3. **Access the chatbot**
   Open your browser and go to: `http://localhost:8080`

## 🌐 Deployment Options (Get Your Own URL)

### Option 1: Heroku (Recommended)

1. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Create a new Heroku app:
   ```bash
   heroku create your-chatbot-name
   ```
3. Deploy:
   ```bash
   git add .
   git commit -m "Deploy chatbot"
   git push heroku main
   ```
4. **Your chatbot URL**: `https://your-chatbot-name.herokuapp.com`

### Option 2: Railway

1. Connect your GitHub repository to [Railway](https://railway.app)
2. Railway will automatically detect the `Procfile` and deploy
3. **Your chatbot URL**: `https://your-app.railway.app`

### Option 3: Render

1. Connect your GitHub repository to [Render](https://render.com)
2. Create a new Web Service with these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn server:app`
3. **Your chatbot URL**: `https://your-app.onrender.com`

### Option 4: Docker (Any Platform)

```bash
# Build and run with Docker
docker build -t my-chatbot .
docker run -p 8080:8080 my-chatbot

# Or use docker-compose
docker-compose up
```

## 🎨 Features

- 🤖 **Smart Responses**: Uses Google Search API to find relevant answers
- 🎨 **Modern UI**: Beautiful, responsive design with gradient backgrounds
- 🚀 **Fast & Reliable**: Built with Flask and optimized for performance
- 📱 **Mobile Friendly**: Responsive design works on all devices
- 🔒 **CORS Enabled**: Proper API handling with error management
- ⚡ **Real-time**: Instant responses with "thinking..." indicators
- 🛠️ **Easy Deploy**: Multiple deployment options with one-click setup

## 📁 Project Structure

```
chatbot/
├── server.py              # Flask backend server
├── app.js                 # Frontend JavaScript
├── index.html             # Main HTML page
├── style.css              # Modern CSS styling
├── google_search.py       # Google search integration
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
3. **Google Search**: Backend searches Google for relevant information
4. **Content Extraction**: Extracts the most relevant text from search results
5. **Response**: Returns the processed answer to the user

## 🎛️ Customization

### Changing the UI
Edit `style.css` to modify colors, fonts, and layout. The current design uses:
- Gradient background: `#667eea` to `#764ba2`
- Modern glassmorphism effects
- Responsive design for all screen sizes

### Modifying Search Behavior
Edit `google_search.py` to change how search results are processed.

### Adding Features
The Flask server in `server.py` can be extended with additional endpoints.

## 🔍 Testing

Your chatbot is already running and tested! You can verify it's working by:

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

2. **Google Search Rate Limits**
   - The app uses the `googlesearch-python` library which may have rate limits
   - Consider implementing caching for frequently asked questions

3. **Deployment Issues**
   - Make sure all files are committed to git
   - Check that `requirements.txt` includes all dependencies
   - Verify your deployment platform supports Python 3.11+

## 📞 Support

Your chatbot is now ready for production! If you encounter any issues:
1. Check the server logs for error messages
2. Verify all dependencies are installed correctly
3. Test the API endpoints directly

## 🎯 Next Steps

1. **Deploy to get your URL**: Choose one of the deployment options above
2. **Customize the design**: Modify colors and styling in `style.css`
3. **Add features**: Extend the functionality in `server.py`
4. **Monitor usage**: Add analytics and logging for production use

**Your chatbot is now fixed and ready to go live! 🎉**