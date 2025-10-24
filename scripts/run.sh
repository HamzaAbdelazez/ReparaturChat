
#!/bin/bash

# ============================================
# ReparaturApp Startup Script - Linux/Mac
# Enhanced with Docker optimization
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
CYAN='\033[0;36m'
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

print_info() {
    echo -e "${CYAN}INFO:${NC} $1"
}

# Configuration
COMPOSE_FILE="docker-compose.yml"

# Parse command line arguments
FORCE_REBUILD=false
PARALLEL_BUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --rebuild)
            FORCE_REBUILD=true
            shift
            ;;
        --parallel)
            PARALLEL_BUILD=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --rebuild   Force rebuild of Docker images"
            echo "  --parallel  Build images in parallel"
            echo "  --help      Show this help message"
            echo ""
            echo "For backend development only:"
            echo "  cd backend && docker compose up"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if Docker is running
if ! docker ps &> /dev/null; then
    print_error "Docker is not running"
    echo "Please start Docker Desktop or Docker service"
    exit 1
fi

print_info "Configuration: Full stack deployment ($(basename $COMPOSE_FILE))"

# Function to cleanup on exit
cleanup() {
    echo ""
    print_warning "Stopping services..."
    
    # Stop Docker containers
    cd "$(dirname "$0")/.." 2>/dev/null || true
    docker compose -f "$COMPOSE_FILE" down 2>/dev/null || true
    
    print_success "All services stopped."
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Navigate to project root
cd "$(dirname "$0")/.."

# Build options
BUILD_ARGS=""
if [ "$FORCE_REBUILD" = true ]; then
    BUILD_ARGS="--build --no-cache"
    print_info "Force rebuild enabled - this will take longer"
elif [ "$PARALLEL_BUILD" = true ]; then
    BUILD_ARGS="--build --parallel"
    print_info "Parallel build enabled"
else
    BUILD_ARGS="--build"
fi

print_status 1 3 "Building and starting Docker services..."
print_info "Using compose file: $COMPOSE_FILE"

# Start services
print_info "Starting full stack application..."
docker compose -f "$COMPOSE_FILE" up -d $BUILD_ARGS

if [ $? -eq 0 ]; then
    print_status 2 3 "Waiting for services to be ready..."
    sleep 10
    
    print_status 3 3 "Checking service health..."
    # Check if services are running
    if docker compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        print_success "Services are running!"
    else
        print_warning "Some services might still be starting..."
    fi
    
    echo ""
    echo "============================================"
    echo "      ReparaturApp Started Successfully!   "
    echo "============================================"
    echo ""
    echo "🌐 Frontend: http://localhost:3000"
    echo "🚀 Backend API: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo "🗄️  Database: PostgreSQL on localhost:5432"
    echo ""
    echo "💡 Tips:"
    echo "   - Use 'docker compose logs -f' to view logs"
    echo "   - Use 'docker compose down' to stop services"
    echo "   - For backend development: 'cd backend && docker compose up'"
    echo ""
    print_success "All services are running in the background!"
    echo "Press Ctrl+C to stop all services..."
    
    # Wait for user interrupt
    while true; do
        sleep 1
    done
else
    print_error "Failed to start services"
    exit 1
fi