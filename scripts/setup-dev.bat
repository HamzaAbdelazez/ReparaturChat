@echo off
REM Development Setup Script for Reparatur Platform (Windows)

echo 🚀 Setting up Reparatur Platform for development...

REM Check if required tools are installed
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Node.js is not installed. Please install it first.
    exit /b 1
)

where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ npm is not installed. Please install it first.
    exit /b 1
)

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Python is not installed. Please install it first.
    exit /b 1
)

where poetry >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Poetry is not installed. Please install it first.
    exit /b 1
)

where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker is not installed. Please install it first.
    exit /b 1
)

echo 📋 Prerequisites check passed!

REM Install root dependencies
echo 📦 Installing root dependencies...
npm install

REM Setup backend
echo 🐍 Setting up backend...
cd backend
if not exist ".env" (
    echo ⚙️ Creating backend .env file...
    copy "..\\.env.example" ".env"
    echo ⚠️  Please update backend/.env with your actual API keys
)
poetry install
cd ..

REM Setup frontend
echo ⚛️ Setting up frontend...
cd frontend
npm install
cd ..

REM Start database
echo 🗄️ Starting PostgreSQL database...
docker-compose up -d database

REM Wait for database to be ready
echo ⏳ Waiting for database to be ready...
timeout /t 10 /nobreak >nul

echo ✅ Setup complete!
echo.
echo 🎯 Next steps:
echo 1. Update backend/.env with your API keys
echo 2. Run 'npm run dev' to start the development servers
echo 3. Frontend: http://localhost:5173
echo 4. Backend API: http://localhost:8000
echo 5. API Docs: http://localhost:8000/docs

pause