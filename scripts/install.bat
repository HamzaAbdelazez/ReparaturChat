@echo off
REM ============================================
REM ReparaturApp Installation Script - Windows
REM Enhanced dependency management and setup
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo     ReparaturApp - Installation Script    
echo ============================================
echo.

REM Configuration
set "DEVELOPMENT_MODE=false"
set "SKIP_DOCKER=false"

REM Parse command line arguments
:parse_args
if "%1"=="--dev" (
    set "DEVELOPMENT_MODE=true"
    shift
    goto parse_args
)
if "%1"=="--skip-docker" (
    set "SKIP_DOCKER=true"
    shift
    goto parse_args
)
if "%1"=="--help" (
    echo Usage: %0 [OPTIONS]
    echo Options:
    echo   --dev          Install development dependencies
    echo   --skip-docker  Skip Docker setup (use existing database)
    echo   --help         Show this help message
    exit /b 0
)
if not "%1"=="" (
    echo ERROR: Unknown option: %1
    exit /b 1
)

echo [1/7] Checking system prerequisites...

REM Check Windows version
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
if "%VERSION%" lss "10.0" (
    echo WARNING: Windows 10 or later recommended for best compatibility
)

echo [2/7] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo SUCCESS: Python %PYTHON_VERSION% found

REM Check Poetry installation
echo [3/7] Checking Poetry installation...
poetry --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Poetry not found. Installing Poetry...
    curl -sSL https://install.python-poetry.org | python -
    if %errorlevel% neq 0 (
        echo ERROR: Poetry installation failed
        echo Please install Poetry manually: https://python-poetry.org/docs/#installation
        pause
        exit /b 1
    )
    echo INFO: Poetry installed. You may need to restart your terminal
    REM Add Poetry to PATH for current session
    set "PATH=%APPDATA%\Python\Scripts;%PATH%"
)

poetry --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%i in ('poetry --version') do echo SUCCESS: Poetry %%i found
) else (
    echo ERROR: Poetry installation verification failed
    pause
    exit /b 1
)

echo [4/7] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from nodejs.org
    pause
    exit /b 1
)

REM Check Node.js version
for /f "tokens=1" %%i in ('node --version') do set NODE_VERSION=%%i
echo SUCCESS: Node.js %NODE_VERSION% found

echo [5/7] Checking Docker installation...
if "%SKIP_DOCKER%"=="false" (
    docker --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Docker is not installed or not in PATH
        echo Please install Docker Desktop from docker.com
        echo After installation, make sure Docker Desktop is running
        pause
        exit /b 1
    )
    
    REM Check if Docker is running
    docker ps >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Docker is installed but not running
        echo Please start Docker Desktop and try again
        pause
        exit /b 1
    )
    
    for /f "tokens=3" %%i in ('docker --version') do echo SUCCESS: Docker %%i found and running
) else (
    echo INFO: Skipping Docker setup as requested
)

REM Navigate to project root
cd /d "%~dp0\.."

echo [6/7] Setting up environment configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo SUCCESS: Created .env file from .env.example
        echo WARNING: Please update .env with your actual API keys
    ) else (
        echo WARNING: .env.example not found. Creating basic .env file...
        (
            echo # Database Configuration
            echo POSTGRES_USER=test
            echo POSTGRES_PASSWORD=password
            echo POSTGRES_DB=reparatur
            echo POSTGRES_HOST=localhost
            echo POSTGRES_PORT=5432
            echo.
            echo # API Tokens (replace with your actual tokens^)
            echo GEMINI_API_KEY=your_gemini_api_key_here
            echo REPLICATE_API_TOKEN=your_replicate_token_here
            echo GEMMA_API_KEY=your_gemma_api_key_here
            echo OPENAI_API_KEY=your_openai_api_key_here
            echo DEEPSEEK_API_KEY=your_deepseek_api_key_here
        ) > .env
        echo SUCCESS: Created basic .env file
        echo WARNING: Please update .env with your actual API keys
    )
) else (
    echo INFO: .env file already exists
)

echo [7/7] Installing project dependencies...

REM Install root dependencies
if exist "package.json" (
    echo INFO: Installing root npm dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install root dependencies
        pause
        exit /b 1
    )
)

REM Install backend dependencies
if exist "backend" (
    echo INFO: Installing backend dependencies with Poetry...
    cd backend
    if exist "pyproject.toml" (
        if "%DEVELOPMENT_MODE%"=="true" (
            poetry install --with dev
        ) else (
            poetry install --only main
        )
        if %errorlevel% neq 0 (
            echo ERROR: Failed to install backend dependencies
            pause
            exit /b 1
        )
    ) else (
        echo WARNING: pyproject.toml not found in backend directory
    )
    cd ..
)

REM Install frontend dependencies
if exist "frontend" (
    echo INFO: Installing frontend dependencies...
    cd frontend
    if exist "package.json" (
        npm install
        if %errorlevel% neq 0 (
            echo ERROR: Failed to install frontend dependencies
            pause
            exit /b 1
        )
    ) else (
        echo WARNING: package.json not found in frontend directory
    )
    cd ..
)

echo.
echo ============================================
echo      Installation Completed Successfully! 
echo ============================================
echo.
echo 📁 Project Structure:
echo    ├── backend/     - FastAPI backend with Poetry
echo    ├── frontend/    - React frontend with Vite
echo    ├── scripts/     - Setup and run scripts
echo    └── docs/        - Documentation
echo.
echo 🚀 Next Steps:
echo    1. Update .env with your API keys
echo    2. Run 'scripts\run.bat' to start the application
echo    3. Or run 'scripts\run.bat --dev' for development mode
echo.
echo 📚 Available Services:
echo    - Frontend: http://localhost:3000 (production)
echo    - Frontend Dev: http://localhost:5173 (development)
echo    - Backend API: http://localhost:8000
echo    - API Documentation: http://localhost:8000/docs
echo.

if "%DEVELOPMENT_MODE%"=="true" (
    echo SUCCESS: Development dependencies installed!
) else (
    echo INFO: Run with --dev flag to install development dependencies
)

echo.
echo SUCCESS: Installation complete! 🎉
pause