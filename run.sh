#!/bin/bash

# Timesheet Middleware API Startup Script

echo "=== Timesheet Middleware API Setup ==="
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found. Please create it first:"
    echo "python -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
echo "Checking dependencies..."
python -c "import flask, pytesseract, pandas, openai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

# Check for environment variables
echo "Checking configuration..."
if [ -f ".env" ]; then
    export $(cat .env | xargs)
    echo "Loaded .env file"
else
    echo "WARNING: .env file not found. Using default configuration."
    echo "For OpenAI functionality, set OPENAI_API_KEY environment variable"
fi

# Check if Tesseract is installed
echo "Checking Tesseract OCR..."
which tesseract >/dev/null
if [ $? -ne 0 ]; then
    echo "WARNING: Tesseract OCR not found. Install it for full functionality:"
    echo "  macOS: brew install tesseract"
    echo "  Ubuntu: sudo apt install tesseract-ocr"
fi

echo
echo "=== Starting Flask Application ==="
echo "API will be available at: http://localhost:5000"
echo "Health check: http://localhost:5000/health"
echo "Press Ctrl+C to stop"
echo

# Start the Flask app
python app.py