
# ============================================
# ReparaturApp Startup Script - Linux/Mac
# ============================================

set -e  # Exit on any error

echo ""
echo "============================================"
echo "       ReparaturApp - Unix Startup         "
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

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        print_error "Python is not installed"
        echo "Please install Python 3.10+ from python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    echo "Please install Node.js from nodejs.org"
    exit 1
fi

# Check if Docker is running
if ! docker ps &> /dev/null; then
    print_error "Docker is not running"
    echo "Please start Docker service"
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
if [ $? -ne 0 ]; then
    print_error "Failed to start database"
    exit 1
fi

print_status 2 6 "Installing Python dependencies..."
# Check if poetry is installed
if command -v poetry &> /dev/null; then
    print_success "Using Poetry for dependency management..."
    poetry install
    if [ $? -ne 0 ]; then
        print_error "Poetry install failed"
        exit 1
    fi
    PYTHON_RUN_CMD="poetry run $PYTHON_CMD"
else
    print_warning "Poetry not found, using pip..."
    if [ -f "requirements.txt" ]; then
        $PYTHON_CMD -m pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            print_error "Pip install failed"
            exit 1
        fi
    else
        print_warning "requirements.txt not found, assuming dependencies are installed"
    fi
    PYTHON_RUN_CMD="$PYTHON_CMD"
fi

print_status 3 6 "Starting FastAPI backend server..."
# Start backend in background
PYTHONPATH="src" $PYTHON_RUN_CMD -c "import uvicorn; uvicorn.run('api.main:app', host='127.0.0.1', port=8000, reload=True)" &
BACKEND_PID=$!

# Wait for backend to start
print_status 3 6 "Waiting for backend to start..."
sleep 5

# Check if backend is running
if ! curl -s http://127.0.0.1:8000/docs > /dev/null; then
    print_warning "Backend might still be starting..."
fi

print_status 4 6 "Installing frontend dependencies..."
cd ../Reparatur-app

if [ ! -d "node_modules" ]; then
    print_status 4 6 "Installing npm packages..."
    npm install
    if [ $? -ne 0 ]; then
        print_error "npm install failed"
        cleanup
        exit 1
    fi
fi

print_status 5 6 "Building frontend..."
npm run build
if [ $? -ne 0 ]; then
    print_error "Frontend build failed"
    cleanup
    exit 1
fi

print_status 6 6 "Starting frontend development server..."
# Start frontend in background
npm run dev &
FRONTEND_PID=$!

echo ""
echo "============================================"
echo "      ReparaturApp Started Successfully!   "
echo "============================================"
echo ""
echo "Backend API: http://127.0.0.1:8000"
echo "API Documentation: http://127.0.0.1:8000/docs"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Wait for user interrupt
wait