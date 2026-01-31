#!/bin/bash
# Quick start script for HackTheAgent Email Brain

echo "🧠 HackTheAgent Email Brain - Starting..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "✏️  Please edit .env to add your watsonx credentials (optional)"
fi

# Start the server
echo ""
echo "🚀 Starting FastAPI server..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000