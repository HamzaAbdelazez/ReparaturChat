# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a bilingual repair assistance application that combines a React frontend with a FastAPI backend. The system uses RAG (Retrieval-Augmented Generation) with vector embeddings to provide intelligent repair guidance based on uploaded PDF manuals and general repair knowledge.

## Architecture

### Frontend (Reparatur-app/)
- **Technology**: React 18 + Vite + TailwindCSS
- **Key Features**: PDF upload, chatbot interface, user authentication, multi-language support
- **Main Components**: 
  - `src/pages/chatbot.jsx` - Main chat interface with PDF upload
  - `src/pages/login.jsx` - User authentication
  - `src/pages/signup.jsx` - User registration

### Backend (backend/)
- **Technology**: FastAPI + SQLAlchemy + pgvector + PostgreSQL
- **Key Features**: 
  - Document processing with PyMuPDF
  - Vector embeddings using SentenceTransformers
  - RAG implementation for context-aware responses
  - Integration with Gemma3 via Replicate API
  - User expertise level adaptation (1-5 scale)
- **Main Modules**:
  - `src/api/service/rag.py` - RAG implementation and document processing
  - `src/api/routers/chat.py` - Chat endpoints with user level prefixes
  - `src/api/service/tools_extractor.py` - Tool extraction from documents
  - `src/api/database/` - Database models and repositories

## Development Commands

### Frontend Development
```bash
cd Reparatur-app
npm install
npm run dev           # Start development server on http://localhost:5173
npm run build         # Build for production
npm run lint          # Run ESLint
npm run preview       # Preview production build
```

### Backend Development
```bash
cd backend
# Install dependencies (if not using poetry)
pip install sqlalchemy fastapi uvicorn psycopg2-binary pgvector python-multipart sentence-transformers pymupdf python-dotenv passlib bcrypt pydantic-settings dataclasses-json replicate aiohttp asyncpg

# Or with poetry
poetry install        

# Start API server
poetry run uvicorn api.main:app --reload --app-dir src  # Start API server on http://127.0.0.1:8000
# OR without poetry
python -c "import sys; sys.path.append('src'); import uvicorn; uvicorn.run('api.main:app', host='127.0.0.1', port=8000, reload=True, app_dir='src')"
```

### Docker Development
```bash
# From backend directory
docker compose build --no-cache
docker compose up     # Start PostgreSQL with pgvector
docker compose down   # Stop containers
```

### Testing
- Backend: Uses pytest framework (run with `poetry run pytest`)
- Frontend: No test framework currently configured
- Application test: Run `python test_application.py` from project root

## Database Setup

The application uses PostgreSQL with pgvector extension for vector similarity search. Database tables are automatically initialized on startup via `init_db_tables()` in `main.py`.

## Key Integrations

- **Replicate API**: Used for Gemma3 model inference (requires REPLICATE_API_TOKEN)
- **SentenceTransformers**: "all-MiniLM-L6-v2" model for document embeddings
- **pgvector**: PostgreSQL extension for vector similarity search
- **PyMuPDF**: PDF text extraction and processing

## Environment Configuration

The backend requires environment variables for database connection and API access. Check `.env` file requirements in the backend directory.

## API Documentation

FastAPI automatically generates documentation available at:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc