#!/bin/bash
# Access Navigator AI - Backend Startup Script

cd backend

echo "==================================="
echo "  Access Navigator AI - Backend"
echo "==================================="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check for API keys
if [ -z "$GROQ_API_KEY" ] && [ -z "$GEMINI_API_KEY" ]; then
    echo ""
    echo "WARNING: No LLM API key set!"
    echo "Set GROQ_API_KEY or GEMINI_API_KEY environment variable."
    echo ""
    echo "Example: export GROQ_API_KEY='your_key_here'"
    echo ""
fi

echo "Starting server on http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
echo ""

# Start server
python main.py
