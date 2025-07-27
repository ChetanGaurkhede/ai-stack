#!/bin/bash

# AI Stack Backend Startup Script

set -e

echo "🚀 Starting AI Stack Backend..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your configuration before continuing."
    echo "   Required: API keys for OpenAI, Gemini, or other services"
    read -p "Press Enter to continue after editing .env file..."
fi

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "🐳 Running in Docker container..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
else
    echo "💻 Running in local development mode..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    
    # Initialize database
    echo "🗄️  Initializing database..."
    python scripts/init_db.py
    
    # Start the application
    echo "🌟 Starting FastAPI application..."
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
fi 