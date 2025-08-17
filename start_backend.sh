#!/bin/bash

echo "Starting Vector Database Backend..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit .env and add your COHERE_API_KEY:"
    echo "Get a free API key from: https://cohere.com/"
    echo ""
    read -p "Press Enter to continue after updating .env..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the backend server
echo "Starting FastAPI server on http://localhost:8000"
echo "API Documentation will be available at http://localhost:8000/docs"
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --reload-dir app