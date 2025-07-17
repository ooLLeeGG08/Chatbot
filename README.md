# 🤖 Code Execution Chatbot

A modern web-based chatbot that can execute JavaScript and Python code in real-time with a beautiful, responsive interface.

## ✨ Features

- **💬 Interactive Chat**: Natural conversation with the chatbot
- **🟨 JavaScript Execution**: Run JavaScript code using Node.js
- **🐍 Python Execution**: Execute Python code safely
- **🎨 Modern UI**: Beautiful, responsive design with syntax highlighting
- **🔒 Safe Execution**: Code runs in isolated temporary files with timeouts
- **⚡ Real-time Results**: Instant feedback with proper error handling

## 🚀 Quick Start

### Prerequisites

- **Python 3.6+** (for the backend server)
- **Node.js** (for JavaScript code execution)

### Installation & Running

1. **Clone or download** this repository

2. **Start the server**:
   ```bash
   python server.py
   ```

3. **Open your browser** and go to:
   ```
   http://localhost:8080
   ```

4. **Start coding!** 🎉

## 🎯 How to Use

### Chat Mode
- Select "💬 Chat" from the dropdown
- Type regular messages to chat with the bot

### JavaScript Execution
- Select "🟨 JavaScript" from the dropdown  
- Type JavaScript code like:
  ```javascript
  console.log("Hello, World!");
  let x = 5 + 3;
  console.log("5 + 3 =", x);
  ```

### Python Execution
- Select "🐍 Python" from the dropdown
- Type Python code like:
  ```python
  print("Hello, World!")
  x = 5 + 3
  print(f"5 + 3 = {x}")
  ```

## 🔧 Technical Details

### Backend (Python)
- Built with Python's built-in `http.server`
- No external dependencies required
- Executes code in temporary files with 10-second timeout
- Automatic cleanup of temporary files
- Handles both stdout and stderr

### Frontend (HTML/CSS/JavaScript)
- Modern ES6+ JavaScript
- Responsive CSS with gradient backgrounds
- Syntax highlighting with highlight.js
- Real-time typing indicators
- Auto-resizing input textarea

### Security Features
- ⏱️ **Execution Timeout**: 10-second limit per code execution
- 🗂️ **Isolated Execution**: Code runs in temporary files
- 🧹 **Automatic Cleanup**: Temporary files are deleted after execution
- 🚫 **No File System Access**: Code cannot access the main project files

## 📁 Project Structure

```
├── index.html          # Main HTML interface
├── style.css           # Modern CSS styling
├── app.js              # Frontend JavaScript logic
├── server.py           # Backend Python server
├── requirements.txt    # Python dependencies (currently none)
├── chatbot.png        # Chatbot icon
└── README.md          # This file
```

## 🛠️ Customization

### Adding New Languages
To add support for more programming languages:

1. Add the language option to the dropdown in `index.html`
2. Update the placeholder logic in `app.js`
3. Add a new execution method in `server.py`

### Styling
- Modify `style.css` to change colors, fonts, or layout
- The design uses CSS gradients and modern styling techniques

### Chat Responses
- Update the `handle_chat_message()` method in `server.py` to add more intelligent responses
- Consider integrating with AI APIs for more sophisticated conversations

## ⚠️ Security Notes

This chatbot is designed for educational and development purposes. The code execution features should be used responsibly:

- Code runs with the same permissions as the Python process
- No network restrictions are enforced by default  
- Consider additional sandboxing for production use
- Be cautious when running untrusted code

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this chatbot!

## 📄 License

This project is open source and available under the MIT License.

---

**Happy Coding! 🚀**