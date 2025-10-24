#!/bin/bash

# ============================================
# ReparaturApp Installation Script - Linux/Mac
# Enhanced dependency management and setup
# ============================================

set -e  # Exit on any error

echo ""
echo "============================================"
echo "    ReparaturApp - Installation Script     "
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
DEVELOPMENT_MODE=false
SKIP_DOCKER=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            DEVELOPMENT_MODE=true
            shift
            ;;
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --dev          Install development dependencies"
            echo "  --skip-docker  Skip Docker setup (use existing database)"
            echo "  --help         Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to check if a tool is installed
check_tool() {
    if ! command -v $1 &> /dev/null; then
        return 1
    fi
    return 0
}

# Function to install tool via package manager
install_tool() {
    local tool=$1
    local install_cmd=$2
    
    print_info "Installing $tool..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y $install_cmd
    elif command -v yum &> /dev/null; then
        sudo yum install -y $install_cmd
    elif command -v brew &> /dev/null; then
        brew install $install_cmd
    else
        print_error "No package manager found. Please install $tool manually."
        return 1
    fi
}

print_status 1 7 "Checking system prerequisites..."

# Check and install Git
if ! check_tool git; then
    print_warning "Git not found. Installing..."
    install_tool "Git" "git" || exit 1
fi

# Check and install curl
if ! check_tool curl; then
    print_warning "curl not found. Installing..."
    install_tool "curl" "curl" || exit 1
fi

# Check Python installation
print_status 2 7 "Checking Python installation..."
if ! check_tool python3; then
    if ! check_tool python; then
        print_error "Python is not installed"
        print_info "Installing Python 3..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip
        elif command -v brew &> /dev/null; then
            brew install python@3.11
        else
            print_error "Please install Python 3.10+ manually from python.org"
            exit 1
        fi
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
REQUIRED_VERSION="3.10"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

print_success "Python $PYTHON_VERSION found"

# Check and install Poetry
print_status 3 7 "Checking Poetry installation..."
if ! check_tool poetry; then
    print_warning "Poetry not found. Installing..."
    curl -sSL https://install.python-poetry.org | $PYTHON_CMD -
    export PATH="$HOME/.local/bin:$PATH"
    if ! check_tool poetry; then
        print_error "Poetry installation failed. Please install manually."
        exit 1
    fi
fi

print_success "Poetry found: $(poetry --version)"

# Check Node.js installation
print_status 4 7 "Checking Node.js installation..."
if ! check_tool node; then
    print_warning "Node.js not found. Installing..."
    if command -v apt-get &> /dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif command -v yum &> /dev/null; then
        curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
        sudo yum install -y nodejs npm
    elif command -v brew &> /dev/null; then
        brew install node
    else
        print_error "Please install Node.js manually from nodejs.org"
        exit 1
    fi
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    print_error "Node.js 18 or higher is required. Found: $(node --version)"
    exit 1
fi

print_success "Node.js $(node --version) found"

# Check Docker installation
print_status 5 7 "Checking Docker installation..."
if [ "$SKIP_DOCKER" = false ]; then
    if ! check_tool docker; then
        print_warning "Docker not found. Installing..."
        if command -v apt-get &> /dev/null; then
            # Install Docker on Ubuntu/Debian
            sudo apt-get update
            sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        elif command -v yum &> /dev/null; then
            # Install Docker on CentOS/RHEL
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            sudo systemctl start docker
            sudo systemctl enable docker
        elif command -v brew &> /dev/null; then
            print_warning "Please install Docker Desktop for Mac manually from docker.com"
            exit 1
        else
            print_error "Please install Docker manually from docker.com"
            exit 1
        fi
        
        # Add user to docker group (requires logout/login to take effect)
        if [ "$EUID" -ne 0 ]; then
            sudo usermod -aG docker $USER
            print_warning "You may need to logout and login again for Docker permissions to take effect"
        fi
    fi
    
    # Check if Docker is running
    if ! docker ps &> /dev/null; then
        print_warning "Docker is installed but not running. Starting Docker..."
        if command -v systemctl &> /dev/null; then
            sudo systemctl start docker
        else
            print_error "Please start Docker service manually"
            exit 1
        fi
    fi
    
    print_success "Docker is installed and running"
else
    print_info "Skipping Docker setup as requested"
fi

# Navigate to project root
cd "$(dirname "$0")/.."

# Setup environment file
print_status 6 7 "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env file from .env.example"
        print_warning "Please update .env with your actual API keys"
    else
        print_warning ".env.example not found. Creating basic .env file..."
        cat > .env << EOF
# Database Configuration
POSTGRES_USER=test
POSTGRES_PASSWORD=password
POSTGRES_DB=reparatur
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# API Tokens (replace with your actual tokens)
GEMINI_API_KEY=your_gemini_api_key_here
REPLICATE_API_TOKEN=your_replicate_token_here
EOF
        print_success "Created basic .env file"
        print_warning "Please update .env with your actual API keys"
    fi
else
    print_info ".env file already exists"
fi

# Install dependencies
print_status 7 7 "Installing project dependencies..."

# Install root dependencies
if [ -f "package.json" ]; then
    print_info "Installing root npm dependencies..."
    npm install
fi

# Install backend dependencies
if [ -d "backend" ]; then
    print_info "Installing backend dependencies with Poetry..."
    cd backend
    if [ -f "pyproject.toml" ]; then
        if [ "$DEVELOPMENT_MODE" = true ]; then
            poetry install --with dev
        else
            poetry install --only main
        fi
    else
        print_warning "pyproject.toml not found in backend directory"
    fi
    cd ..
fi

# Install frontend dependencies
if [ -d "frontend" ]; then
    print_info "Installing frontend dependencies..."
    cd frontend
    if [ -f "package.json" ]; then
        npm install
    else
        print_warning "package.json not found in frontend directory"
    fi
    cd ..
fi

echo ""
echo "============================================"
echo "      Installation Completed Successfully! "
echo "============================================"
echo ""
echo "📁 Project Structure:"
echo "   ├── backend/     - FastAPI backend with Poetry"
echo "   ├── frontend/    - React frontend with Vite"
echo "   ├── scripts/     - Setup and run scripts"
echo "   └── docs/        - Documentation"
echo ""
echo "🚀 Next Steps:"
echo "   1. Update .env with your API keys"
echo "   2. Run './scripts/run.sh' to start the application"
echo "   3. Or run './scripts/run.sh --dev' for development mode"
echo ""
echo "📚 Available Services:"
echo "   - Frontend: http://localhost:3000 (production)"
echo "   - Frontend Dev: http://localhost:5173 (development)"
echo "   - Backend API: http://localhost:8000"
echo "   - API Documentation: http://localhost:8000/docs"
echo ""
if [ "$DEVELOPMENT_MODE" = true ]; then
    print_success "Development dependencies installed!"
else
    print_info "Run with --dev flag to install development dependencies"
fi

print_success "Installation complete! 🎉"