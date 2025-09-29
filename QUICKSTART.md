# ReparaturApp - Quick Start Guide

## Get Started in 5 Minutes

### Prerequisites Check
Before starting, make sure you have:
- **Python 3.10+** installed
-  **Node.js 16+** installed  
-  **Docker Desktop** running
-  **Git** installed

### Platform-Specific Setup

####  Windows
```cmd
# Open Command Prompt or PowerShell as Administrator
# Navigate to project directory
cd "D:\BA Thesis\project\Reparatur"

# Run the startup script
run.bat
```

####  Linux
```bash
# Open terminal
# Navigate to project directory
cd /path/to/ReparaturApp

# Make script executable and run
chmod +x run.sh
./run.sh
```

####  macOS  
```bash
# Open Terminal
# Navigate to project directory  
cd /path/to/ReparaturApp

# Make script executable and run
chmod +x run-mac.sh
./run-mac.sh
```

### Manual Setup (If Scripts Don't Work)

#### Step 1: Start Database
```bash
cd backend
docker compose up -d
```

#### Step 2: Setup Backend
```bash
# Option A: With Poetry (Recommended)
poetry install
poetry run uvicorn api.main:app --reload --app-dir src

# Option B: With pip
pip install sqlalchemy fastapi uvicorn psycopg2-binary pgvector python-multipart sentence-transformers pymupdf python-dotenv passlib bcrypt pydantic-settings dataclasses-json replicate aiohttp asyncpg
python -c "import sys; sys.path.append('src'); import uvicorn; uvicorn.run('api.main:app', host='127.0.0.1', port=8000, reload=True)"
```

#### Step 3: Setup Frontend
```bash
cd ../Reparatur-app
npm install
npm run dev
```

###  Verification

Once started, verify everything works:

1. **Backend API**: http://127.0.0.1:8000/docs
2. **Frontend**: http://localhost:5173
3. **Database**: Check Docker Desktop for running postgres container

### Configuration

#### Environment Variables
Create `backend/.env`:
```env
POSTGRES_USER=test
POSTGRES_PASSWORD=password
POSTGRES_DB=reparatur
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://test:password@localhost:5432/reparatur
REPLICATE_API_TOKEN=your_token_here
```

#### Get Replicate API Token
1. Go to [replicate.com](https://replicate.com)
2. Sign up/login
3. Go to Account → API Tokens  
4. Create new token
5. Add to `.env` file

###  First Steps

1. **Register Account**: Create user account in the app
2. **Upload PDF**: Upload a repair manual
3. **Ask Questions**: Chat about the uploaded manual
4. **Explore Tools**: See extracted tools and analysis

### 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Kill existing Python processes |
| Port 5432 in use | Stop other PostgreSQL services |
| Import errors | Run `pip install` in backend directory |
| Docker not starting | Ensure Docker Desktop is running |
| Permission errors | Run terminal as Administrator (Windows) |


---

**🎉 You're ready to go!** The app should now be running with full functionality.