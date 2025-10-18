#!/bin/bash
# Mini SQL Playground Backend - Development Startup Script

echo "🚀 Starting Mini SQL Playground Backend..."
echo ""

# Check if virtual environment exists
if [ ! -d "dbenv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv dbenv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source dbenv/bin/activate

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python3 -c "import fastapi, uvicorn" 2>/dev/null || {
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
}

# Start the server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📚 API Documentation available at http://localhost:8000/docs"
echo "🔧 Health check available at http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
