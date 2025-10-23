#!/bin/bash

# Memorial Automator - Start Script

echo "🚀 Memorial Automator - Starting..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please copy .env.example to .env and configure your OpenAI API key"
    echo ""
    echo "Run: cp .env.example .env"
    echo "Then edit .env and add your OPENAI_API_KEY"
    exit 1
fi

# Create required directories
echo "📁 Ensuring directories exist..."
python -c "from app.core.config import ensure_directories; ensure_directories()"

# Start the server
echo ""
echo "✅ Starting FastAPI server..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "📖 ReDoc: http://localhost:8000/redoc"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

