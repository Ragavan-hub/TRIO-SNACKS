#!/bin/bash

echo "========================================"
echo "  Trio Snacks - Starting Application"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ from https://www.python.org/downloads/"
    exit 1
fi

echo "Python found!"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "No virtual environment found. Using system Python."
    echo ""
    echo "TIP: Create a virtual environment for better isolation:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
fi

# Check if requirements are installed
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Failed to install dependencies"
        echo "Try: pip3 install --user -r requirements.txt"
        exit 1
    fi
    echo "Dependencies installed!"
    echo ""
fi

echo "Starting Flask application..."
echo ""
echo "========================================"
echo "  Application will be available at:"
echo "  http://localhost:5000"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py

