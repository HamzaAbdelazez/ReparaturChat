@echo off
REM ============================================
REM ReparaturApp Startup Script - Windows
REM Enhanced with Docker optimization
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo       ReparaturApp - Windows Startup      
echo ============================================
echo.

REM Configuration
set "COMPOSE_FILE=docker-compose.yml"
set "FORCE_REBUILD=false"
set "PARALLEL_BUILD=false"

REM Parse command line arguments
:parse_args
if "%1"=="--rebuild" (
    set "FORCE_REBUILD=true"
    shift
    goto parse_args
)
if "%1"=="--parallel" (
    set "PARALLEL_BUILD=true"
    shift
    goto parse_args
)
if "%1"=="--help" (
    echo Usage: %0 [OPTIONS]
    echo Options:
    echo   --rebuild   Force rebuild of Docker images
    echo   --parallel  Build images in parallel
    echo   --help      Show this help message
    echo.
    echo For backend development only:
    echo   cd backend ^&^& docker compose up
    exit /b 0
)
if not "%1"=="" (
    echo ERROR: Unknown option: %1
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

echo INFO: Configuration: Full stack deployment (%COMPOSE_FILE%)

REM Navigate to project root
cd /d "%~dp0\.."

REM Build options
set "BUILD_ARGS=--build"
if "%FORCE_REBUILD%"=="true" (
    set "BUILD_ARGS=--build --no-cache"
    echo INFO: Force rebuild enabled - this will take longer
) else if "%PARALLEL_BUILD%"=="true" (
    set "BUILD_ARGS=--build --parallel"
    echo INFO: Parallel build enabled
)

echo [1/3] Building and starting Docker services...
echo INFO: Using compose file: %COMPOSE_FILE%

REM Start services
echo INFO: Starting full stack application...
docker compose -f "%COMPOSE_FILE%" up -d %BUILD_ARGS%

if %errorlevel% equ 0 (
    echo [2/3] Waiting for services to be ready...
    timeout /t 10 /nobreak >nul
    
    echo [3/3] Checking service health...
    docker compose -f "%COMPOSE_FILE%" ps | findstr "Up" >nul
    if %errorlevel% equ 0 (
        echo SUCCESS: Services are running!
    ) else (
        echo WARNING: Some services might still be starting...
    )
    
    echo.
    echo ============================================
    echo         ReparaturApp Started Successfully!
    echo ============================================
    echo.
    echo 🌐 Frontend: http://localhost:3000
    echo 🚀 Backend API: http://localhost:8000
    echo 📚 API Documentation: http://localhost:8000/docs
    echo 🗄️  Database: PostgreSQL on localhost:5432
    echo.
    echo 💡 Tips:
    echo    - Use 'docker compose logs -f' to view logs
    echo    - Use 'docker compose down' to stop services
    echo    - For backend development: 'cd backend ^&^& docker compose up'
    echo.
    echo SUCCESS: All services are running in the background!
    echo Press any key to stop all services...
    pause >nul
    
    echo.
    echo Stopping services...
    docker compose -f "%COMPOSE_FILE%" down
    echo All services stopped.
    
) else (
    echo ERROR: Failed to start services
    pause
    exit /b 1
)

pause