#!/bin/bash

echo "========================================================================"
echo "         CSV Analysis Web Application - Startup Script"
echo "========================================================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "   Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed"
    echo "   Please install Python from https://python.org/"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"
echo "✅ Python found: $(python --version)"
echo ""

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
    echo ""
fi

# Install backend dependencies if needed
if [ ! -d "backend/venv" ]; then
    echo "🐍 Setting up Python virtual environment..."
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo ""
fi

# Compile TypeScript
echo "🔨 Compiling TypeScript..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ TypeScript compilation failed"
    exit 1
fi

echo ""
echo "========================================================================"
echo "🚀 Starting CSV Analysis Web Application..."
echo "========================================================================"
echo ""
echo "🌐 Frontend will be available at: http://localhost:5000"
echo "📊 Backend API running on: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the application"
echo "========================================================================"
echo ""

# Start the backend (which also serves the frontend)
cd backend
python app.py