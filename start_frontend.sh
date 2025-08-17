#!/bin/bash

echo "Starting Vector Database Frontend..."

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install --legacy-peer-deps
fi

# Start the development server
echo "Starting React development server on http://localhost:3000"
echo "Make sure the backend is running on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

npm start