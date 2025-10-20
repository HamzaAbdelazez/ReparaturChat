#!/bin/bash

# Development Setup Script for Reparatur Platform
set -e

echo "🚀 Setting up Reparatur Platform for development..."

# Check if required tools are installed
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    fi
}

echo "📋 Checking prerequisites..."
check_tool "node"
check_tool "npm"
check_tool "python"
check_tool "poetry"
check_tool "docker"

# Install root dependencies
echo "📦 Installing root dependencies..."
npm install

# Setup backend
echo "🐍 Setting up backend..."
cd backend
if [ ! -f ".env" ]; then
    echo "⚙️ Creating backend .env file..."
    cp ../.env.example .env
    echo "⚠️  Please update backend/.env with your actual API keys"
fi
poetry install
cd ..

# Setup frontend
echo "⚛️ Setting up frontend..."
cd frontend
npm install
cd ..

# Start database
echo "🗄️ Starting PostgreSQL database..."
docker-compose up -d database

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Update backend/.env with your API keys"
echo "2. Run 'npm run dev' to start the development servers"
echo "3. Frontend: http://localhost:5173"
echo "4. Backend API: http://localhost:8000"
echo "5. API Docs: http://localhost:8000/docs"