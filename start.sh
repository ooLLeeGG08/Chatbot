#!/bin/bash

# AI ChatBot Startup Script

echo "🤖 Starting AI ChatBot..."
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Function to install dependencies
install_dependencies() {
    echo "📦 Installing dependencies..."
    
    # Try virtual environment first
    if command -v python3 -m venv &> /dev/null; then
        if [ ! -d "venv" ]; then
            echo "🏗️  Creating virtual environment..."
            python3 -m venv venv 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "✅ Virtual environment created!"
                source venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                return $?
            fi
        else
            echo "🔧 Activating existing virtual environment..."
            source venv/bin/activate
            pip install -r requirements.txt
            return $?
        fi
    fi
    
    # Fallback to system installation
    echo "🔧 Installing to system (virtual environment not available)..."
    if pip install -r requirements.txt 2>/dev/null; then
        return 0
    elif pip install --break-system-packages -r requirements.txt 2>/dev/null; then
        return 0
    elif pip3 install --break-system-packages -r requirements.txt 2>/dev/null; then
        return 0
    else
        echo "❌ Could not install dependencies. Please install manually:"
        echo "   pip install --break-system-packages -r requirements.txt"
        return 1
    fi
}

# Install dependencies
install_dependencies

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies."
    exit 1
fi

# Start the server
echo "🚀 Starting the chatbot server..."
echo "🌐 Your chatbot will be available at: http://localhost:8080"
echo "📱 Press Ctrl+C to stop the server"
echo "================================"

# Try to run with the activated environment if available, otherwise use system python
if [ -f "venv/bin/python" ]; then
    venv/bin/python server.py
else
    python3 server.py
fi