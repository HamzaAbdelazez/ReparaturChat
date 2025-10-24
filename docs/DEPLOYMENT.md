# ReparaturApp Deployment Guide

A comprehensive guide for setting up, configuring, and deploying the AI-powered Repair Platform.

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Development Setup](#development-setup)
7. [Docker Deployment](#docker-deployment)
8. [Performance Optimization](#performance-optimization)
9. [Troubleshooting](#troubleshooting)
10. [Production Deployment](#production-deployment)

## Quick Start

### For Impatient Users 

```bash
# 1. Clone and navigate to project
git clone <repository-url>
cd Reparatur

# 2. Run installation script
./scripts/install.sh --dev

# 3. Configure API keys (edit .env file)
nano .env

# 4. Start the application
./scripts/run.sh --dev
```

**Windows users:** Use `.bat` files instead of `.sh` files.

## System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows 10+
- **RAM**: 4GB (8GB recommended for development)
- **Storage**: 5GB free space
- **Network**: Internet connection for AI API calls

### Required Software
- **Docker Desktop**: For containerized deployment
- **Python**: 3.10 or higher
- **Node.js**: 18 or higher
- **Git**: For version control

### Optional but Recommended
- **Poetry**: Python dependency management
- **VS Code**: With Python and TypeScript extensions

## Installation

### Automated Installation

The installation scripts handle dependency management and system setup:

#### Linux/macOS
```bash
# Standard installation
./scripts/install.sh

# Development installation (includes dev dependencies)
./scripts/install.sh --dev

# Skip Docker setup (if using external database)
./scripts/install.sh --skip-docker
```

#### Windows
```cmd
REM Standard installation
scripts\install.bat

REM Development installation
scripts\install.bat --dev

REM Skip Docker setup
scripts\install.bat --skip-docker
```

### Manual Installation

If automated scripts fail, follow these manual steps:

#### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip nodejs npm docker.io docker-compose
```

**macOS (with Homebrew):**
```bash
brew install python@3.11 node docker
brew install --cask docker
```

**Windows:**
- Install Python from [python.org](https://python.org)
- Install Node.js from [nodejs.org](https://nodejs.org)
- Install Docker Desktop from [docker.com](https://docker.com)

#### 2. Install Poetry (Python Dependency Manager)
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

#### 3. Install Project Dependencies
```bash
# Root dependencies
npm install

# Backend dependencies
cd backend && poetry install && cd ..

# Frontend dependencies
cd frontend && npm install && cd ..
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Copy example configuration
cp .env.example .env
```

### Required API Keys

Edit `.env` and add your API credentials:

```env
# Database Configuration
POSTGRES_USER=test
POSTGRES_PASSWORD=password
POSTGRES_DB=reparatur
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# AI Model API Keys
GEMINI_API_KEY=your_actual_gemini_key_here
REPLICATE_API_TOKEN=your_actual_replicate_token_here
OPENAI_API_KEY=your_actual_openai_key_here
DEEPSEEK_API_KEY=your_actual_deepseek_key_here

# Optional: Custom model endpoints
CUSTOM_LLM_ENDPOINT=http://your-custom-endpoint
```

### Obtaining API Keys

| Provider | How to Get API Key | Cost |
|----------|-------------------|------|
| **Google AI (Gemini)** | [Google AI Studio](https://makersuite.google.com/app/apikey) | Free tier available |
| **Replicate (Gemma-3)** | [Replicate Account](https://replicate.com/account/api-tokens) | Pay-per-use |
| **OpenAI (GPT-4)** | [OpenAI Platform](https://platform.openai.com/api-keys) | Pay-per-use |
| **DeepSeek** | [DeepSeek Platform](https://platform.deepseek.com) | Competitive pricing |

### Security Notes 

- **Never commit API keys** to version control
- Use **environment variables** for all sensitive data
- Consider using **key rotation** for production deployments
- Monitor **API usage and costs** regularly

## Running the Application

### Production Mode (Recommended)

```bash
# Linux/macOS
./scripts/run.sh

# Windows
scripts\run.bat
```

**Features:**
- Optimized Docker builds with caching
- Production-ready Nginx frontend serving
- Background service execution
- Automatic health checks

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Development Mode

```bash
# Linux/macOS
./scripts/run.sh --dev

# Windows
scripts\run.bat --dev
```

**Features:**
- Hot reload for frontend and backend
- Development debugging enabled
- Detailed logging output
- Source code mounting in containers

**Access Points:**
- Frontend Dev Server: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Advanced Run Options

```bash
# Force rebuild Docker images (slower but ensures latest changes)
./scripts/run.sh --rebuild

# Build images in parallel (faster on multi-core systems)
./scripts/run.sh --parallel

# Development mode with forced rebuild
./scripts/run.sh --dev --rebuild
```

## Development Setup

### IDE Configuration

#### Visual Studio Code
Recommended extensions:
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

#### PyCharm/IntelliJ
- Configure Poetry interpreter
- Enable TypeScript support
- Install Tailwind CSS plugin

### Code Quality Tools

#### Backend (Python)
```bash
cd backend

# Code formatting
poetry run black .
poetry run isort .

# Linting
poetry run flake8 .
poetry run mypy .

# Testing
poetry run pytest
```

#### Frontend (React)
```bash
cd frontend

# Code formatting
npm run format

# Linting
npm run lint

# Type checking
npm run type-check

# Testing
npm run test
```

### Database Management

#### Accessing PostgreSQL
```bash
# Connect to database container
docker exec -it reparatur-database-1 psql -U test -d reparatur

# View tables
\dt

# Exit
\q
```

#### Database Migrations
```bash
cd backend
poetry run alembic upgrade head
```

## Docker Deployment

### Container Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Nginx)       │    │   (FastAPI)     │    │  (PostgreSQL)   │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Docker Compose Files

| File | Purpose | Usage |
|------|---------|-------|
| `docker-compose.yml` | Production deployment | `docker compose up` |
| `docker-compose.dev.yml` | Development with hot reload | `docker compose -f docker-compose.dev.yml up` |
| `docker-compose.simple.yml` | Backend-only testing | `docker compose -f docker-compose.simple.yml up` |

### Building Images

```bash
# Build all services
docker compose build

# Build specific service
docker compose build backend

# Build without cache (force fresh build)
docker compose build --no-cache

# Build in parallel (faster)
docker compose build --parallel
```

### Managing Services

```bash
# Start services in background
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Restart specific service
docker compose restart backend

# Scale services (for load testing)
docker compose up --scale backend=3
```

## Performance Optimization

### Docker Build Speed

The main performance bottleneck is the Poetry dependency installation. Here are optimization strategies:

#### 1. Use Build Cache
```bash
# Leverage Docker layer caching
docker compose build --parallel
```

#### 2. Multi-stage Dockerfile Optimization
The backend Dockerfile uses multi-stage builds to minimize final image size:

```dockerfile
# Build stage - installs dependencies
FROM python:3.11-slim as builder
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction

# Runtime stage - copies only necessary files
FROM python:3.11-slim as runtime
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
```

#### 3. Dependency Caching
```bash
# Pre-build dependencies layer
docker compose build --target builder

# Then build full application
docker compose build
```

### Runtime Performance

#### Backend Optimization
- **Async/await**: All database and API calls use async patterns
- **Connection pooling**: PostgreSQL connections are pooled
- **Response caching**: Frequently accessed data is cached

#### Frontend Optimization
- **Code splitting**: React components are lazy-loaded
- **Bundle optimization**: Vite optimizes JavaScript bundles
- **Asset compression**: Nginx compresses static assets

#### Database Optimization
- **Indexing**: pgvector indexes for semantic search
- **Query optimization**: Optimized SQL queries for document retrieval
- **Connection limits**: Configured for concurrent users

## Troubleshooting

### Common Issues

#### 1. "Docker is not running"
**Solution:**
```bash
# Linux
sudo systemctl start docker

# macOS/Windows
# Start Docker Desktop application
```

#### 2. "Port already in use"
**Symptoms:** Cannot bind to port 3000, 8000, or 5432

**Solution:**
```bash
# Find process using port
lsof -i :8000  # Linux/macOS
netstat -ano | findstr 8000  # Windows

# Kill process or change port in docker-compose.yml
```

#### 3. "Poetry install takes forever"
**Solutions:**
```bash
# Use pip instead (faster but less reliable)
pip install -r requirements.txt

# Or use Poetry with pip resolver
poetry config experimental.new-installer false
poetry install
```

#### 4. "API key errors"
**Symptoms:** LLM requests fail with authentication errors

**Solution:**
1. Verify API keys in `.env` file
2. Check API key validity on provider websites
3. Ensure sufficient API credits/quota

#### 5. "Frontend build fails"
**Solutions:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Use different Node version
nvm use 18  # if using nvm
```

### Debug Mode

#### Enable Debug Logging
```bash
# Backend debug mode
cd backend
PYTHONPATH=src poetry run uvicorn api.main:app --reload --log-level debug

# Frontend debug mode
cd frontend
npm run dev -- --debug
```

#### Container Debugging
```bash
# Access running container
docker exec -it reparatur-backend-1 bash

# View container logs
docker logs reparatur-backend-1 -f

# Inspect container configuration
docker inspect reparatur-backend-1
```

### Performance Monitoring

#### System Resources
```bash
# Monitor Docker resource usage
docker stats

# Monitor container health
docker compose ps
```

#### Application Metrics
- **Frontend**: Browser DevTools → Network/Performance tabs
- **Backend**: FastAPI automatic metrics at `/metrics`
- **Database**: PostgreSQL query logs and pg_stat_statements

## Production Deployment

### Security Checklist

- [ ] Change default database passwords
- [ ] Use HTTPS with SSL certificates
- [ ] Configure firewall rules
- [ ] Set up API rate limiting
- [ ] Enable CORS properly
- [ ] Use secrets management (not .env files)
- [ ] Regular security updates

### Scaling Considerations

#### Horizontal Scaling
```bash
# Scale backend instances
docker compose up --scale backend=3

# Use load balancer (Nginx, HAProxy, or cloud load balancer)
```

#### Database Scaling
- **Read replicas** for query scaling
- **Connection pooling** with pgbouncer
- **Caching layer** with Redis

#### CDN and Static Assets
- Use CDN for frontend static files
- Optimize images and assets
- Enable browser caching

### Monitoring and Logging

#### Production Monitoring Stack
```yaml
version: '3.8'
services:
  # Application services...
  
  prometheus:
    image: prom/prometheus
    # Monitor application metrics
    
  grafana:
    image: grafana/grafana
    # Visualization dashboards
    
  loki:
    image: grafana/loki
    # Log aggregation
```

#### Health Checks
```bash
# Application health endpoints
curl http://localhost:8000/health
curl http://localhost:3000/health

# Database connectivity
docker exec reparatur-database-1 pg_isready
```

### Backup and Recovery

#### Database Backups
```bash
# Create backup
docker exec reparatur-database-1 pg_dump -U test reparatur > backup.sql

# Restore backup
docker exec -i reparatur-database-1 psql -U test reparatur < backup.sql
```

#### Application State
- Document uploads (file storage)
- User conversations (database)
- Vector embeddings (database)
- Configuration files

## Support and Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Community
- Open issues on GitHub repository
- Check existing documentation in `/docs` folder
- Review code comments and docstrings

### Development Team Contact
- **Backend Issues**: Check `backend/README.md`
- **Frontend Issues**: Check `frontend/README.md`
- **Infrastructure Issues**: Check this deployment guide

---

**Last Updated**: 2025-01-24  
**Version**: 1.0.0  
**Compatibility**: Docker Compose v2, Python 3.10+, Node.js 18+