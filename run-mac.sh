
# ============================================
# ReparaturApp Startup Script - macOS Specific
# ============================================

set -e  # Exit on any error

echo ""
echo "============================================"
echo "        ReparaturApp - macOS Startup        "
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$1/$2]${NC} $3"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

print_success() {
    echo -e "${GREEN}SUCCESS:${NC} $1"
}

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    print_error "Homebrew is not installed"
    echo "Install Homebrew first: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    echo "Install with: brew install python@3.11"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    echo "Install with: brew install node"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    echo "Install Docker Desktop for Mac from docker.com"
    exit 1
fi

# Check if Docker is running
if ! docker ps &> /dev/null; then
    print_error "Docker is not running"
    echo "Please start Docker Desktop"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    
    # Kill background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Stop Docker containers
    cd backend 2>/dev/null || true
    docker compose down 2>/dev/null || true
    
    echo "All services stopped."
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

print_status 1 6 "Starting PostgreSQL database with Docker..."
cd backend
docker compose up -d

print_status 2 6 "Installing Python dependencies..."
# Check if poetry is installed
if command -v poetry &> /dev/null; then
    print_success "Using Poetry for dependency management..."
    poetry install
else
    echo "Poetry not found. Installing..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    poetry install
fi

print_status 3 6 "Starting FastAPI backend server..."
# Use macOS specific terminal to open new window
osascript <<EOF
tell application "Terminal"
    do script "cd \"$(pwd)\" && poetry run python -c \"import sys; sys.path.append('src'); import uvicorn; uvicorn.run('api.main:app', host='127.0.0.1', port=8000, reload=True)\""
end tell
EOF

# Wait for backend to start
sleep 8

print_status 4 6 "Installing frontend dependencies..."
cd ../Reparatur-app

if [ ! -d "node_modules" ]; then
    print_status 4 6 "Installing npm packages..."
    npm install
fi

print_status 5 6 "Building frontend..."
npm run build

print_status 6 6 "Starting frontend development server..."
# Use macOS specific terminal to open new window
osascript <<EOF
tell application "Terminal"
    do script "cd \"$(pwd)\" && npm run dev"
end tell
EOF

echo ""
echo "============================================"
echo "      ReparaturApp Started Successfully!   "
echo "============================================"
echo ""
echo "Backend API: http://127.0.0.1:8000"
echo "API Documentation: http://127.0.0.1:8000/docs"
echo "Frontend: http://localhost:5173"
echo ""
echo "Services are running in separate Terminal windows."
echo "Close those windows or press Ctrl+C in them to stop services."
echo ""
echo "To stop Docker containers, run:"
echo "cd backend && docker compose down"
echo ""