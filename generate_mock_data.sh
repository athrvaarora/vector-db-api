#!/bin/bash

echo "Generating Mock Data for Vector Database..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your Cohere API key:"
    echo "cp .env.example .env"
    echo "Then edit .env and add your COHERE_API_KEY"
    echo ""
    echo "You can get a free API key from: https://cohere.com/"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if the backend is running
echo "Checking if backend is running on port 8000..."
if ! curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "Error: Backend is not running!"
    echo "Please start the backend first using: ./start_backend.sh"
    exit 1
fi

echo "Backend is running. Generating mock data..."
echo ""

# Set Python path and generate mock data
PYTHONPATH=. python scripts/generate_mock_data.py --populate

echo ""
echo "Mock data generation complete!"
echo "You can now:"
echo "1. Visit http://localhost:8000/docs to explore the API"
echo "2. Visit http://localhost:3000 to use the web interface"
echo "3. Try searching through the generated libraries"