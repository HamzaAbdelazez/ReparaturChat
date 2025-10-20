@echo off
REM ============================================
REM ReparaturApp Startup Script - Windows
REM ============================================

echo.
echo ============================================
echo       ReparaturApp - Windows Startup      
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from nodejs.org
    pause
    exit /b 1
)

REM Check if Docker is running
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running
    echo Please start Docker Desktop
    pause
    exit /b 1
)

echo [1/6] Starting PostgreSQL database with Docker...
cd backend
docker compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start database
    pause
    exit /b 1
)

echo [2/6] Installing Python dependencies...
REM Check if poetry is installed
poetry --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Using Poetry for dependency management...
    poetry install
    if %errorlevel% neq 0 (
        echo ERROR: Poetry install failed
        pause
        exit /b 1
    )
    set PYTHON_CMD=poetry run python
) else (
    echo Poetry not found, using pip...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Pip install failed
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
)

echo [3/6] Starting FastAPI backend server...
start "Backend Server" cmd /k "cd /d %CD% && %PYTHON_CMD% -c \"import sys; sys.path.append('src'); import uvicorn; uvicorn.run('api.main:app', host='127.0.0.1', port=8000, reload=True)\""

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo [4/6] Installing frontend dependencies...
cd ..\frontend
if not exist node_modules (
    echo Installing npm packages...
    npm install
    if %errorlevel% neq 0 (
        echo ERROR: npm install failed
        pause
        exit /b 1
    )
)

echo [5/6] Building frontend...
npm run build
if %errorlevel% neq 0 (
    echo ERROR: Frontend build failed
    pause
    exit /b 1
)

echo [6/6] Starting frontend development server...
start "Frontend Server" cmd /k "npm run dev"

echo.
echo ============================================
echo         ReparaturApp Started Successfully!
echo ============================================
echo.
echo Backend API: http://127.0.0.1:8000
echo API Documentation: http://127.0.0.1:8000/docs
echo Frontend: http://localhost:5173
echo.
echo Press any key to stop all services...
pause >nul

echo.
echo Stopping services...
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1
cd ..\backend
docker compose down

echo All services stopped.
pause