# ReparaturApp - AI-Powered Repair Platform

An intelligent repair assistance platform that combines Retrieval-Augmented Generation (RAG) with multiple Large Language Models to provide precise, contextual repair guidance. The system analyzes uploaded repair manuals and provides cost estimation, feasibility assessment, and tool recommendations for device repairs.

##  Project Structure

```
Reparatur/
├── backend/                    # FastAPI backend service
│   ├── src/api/
│   │   ├── config/            # Database setup and configuration
│   │   ├── database/          # PostgreSQL models and repositories
│   │   ├── models/            # Pydantic data models
│   │   ├── routers/           # API endpoints (REST routes)
│   │   ├── service/           # Business logic and AI integration
│   │   └── shared/            # Shared utilities and helpers
│   ├── tests/                 # Backend test suite
│   ├── Dockerfile             # Backend container configuration
│   ├── pyproject.toml         # Python dependencies (Poetry)
│   ├── requirements.txt       # Pip fallback dependencies
│   └── docker-compose.yml     # Database-only setup for development
├── frontend/                  # React frontend application
│   ├── src/
│   │   ├── components/        # Reusable React components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── pages/            # Main page components
│   │   ├── services/         # API client services
│   │   ├── utils/            # Utility functions
│   │   └── i18n/             # Internationalization (German/English)
│   ├── Dockerfile            # Frontend container (React + Nginx)
│   ├── package.json          # Node.js dependencies
│   ├── vite.config.js        # Vite build configuration
│   └── tailwind.config.js    # TailwindCSS configuration
├── scripts/                  # Deployment and setup scripts
│   ├── install.sh/.bat       # Automated installation
│   └── run.sh/.bat           # Application startup scripts
├── docs/                     # Documentation
│   ├── DEPLOYMENT_GUIDE.md   # Complete deployment guide
│   └── CODE_STRUCTURE.md     # Code organization guide
├── docker-compose.yml        # Full-stack container orchestration
├── package.json             # Root scripts and concurrency management
├── .env.example             # Environment variables template
└── README.md               
```

##  Quick Start

### Option 1: Automated Installation (Recommended)

```bash
# Linux/macOS
./scripts/install.sh

# Windows
scripts\install.bat

# Then start the application
./scripts/run.sh        # Linux/macOS
scripts\run.bat         # Windows
```

### Option 2: Manual Setup

#### Prerequisites
- **Docker Desktop** (for containerized deployment)
- **Python 3.10+** (for backend development)
- **Node.js 18+** (for frontend development)
- **Poetry** (Python dependency management)

#### Installation Steps

1. **Clone and setup environment**
   ```bash
   git clone <repository-url>
   cd Reparatur
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Install dependencies**
   ```bash
   # Root dependencies
   npm install
   
   # Backend dependencies
   cd backend && poetry install && cd ..
   
   # Frontend dependencies  
   cd frontend && npm install && cd ..
   ```

3. **Start the application**
   ```bash
   # Full stack with Docker
   docker compose up --build
   
   # Access the application
   # Frontend: http://localhost:3000
   # Backend API: http://localhost:8000
   # API Docs: http://localhost:8000/docs
   ```

##  Development Modes

### Full Stack Development
```bash
# Start all services (database + backend + frontend)
./scripts/run.sh                    # Linux/macOS
scripts\run.bat                     # Windows

# With forced rebuild
./scripts/run.sh --rebuild
```

### Backend Development Only
```bash
# Start only database for backend development
cd backend
docker compose up

# Run backend manually
poetry run uvicorn api.main:app --reload --app-dir src
```

### Frontend Development Only
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

##  Database & Environment

### PostgreSQL with pgvector
The platform uses PostgreSQL with the pgvector extension for:
- **Document storage**: PDF content and metadata
- **Vector embeddings**: Semantic search capabilities
- **User management**: Authentication and conversation history

### Required Environment Variables

Create `.env` file (copy from `.env.example`):

```env
# Database Configuration
POSTGRES_USER=test
POSTGRES_PASSWORD=password
POSTGRES_DB=reparatur
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# AI Model API Keys (get from respective providers)
GEMINI_API_KEY=your_actual_gemini_key
REPLICATE_API_TOKEN=your_actual_replicate_token  
OPENAI_API_KEY=your_actual_openai_key
DEEPSEEK_API_KEY=your_actual_deepseek_key
```

### API Key Sources
| Provider | Get API Key | Purpose |
|----------|-------------|---------|
| [Google AI (Gemini)](https://makersuite.google.com/app/apikey) | Advanced reasoning | Free tier available |
| [Replicate](https://replicate.com/account/api-tokens) | Gemma-3 models | Pay-per-use |
| [OpenAI](https://platform.openai.com/api-keys) | GPT-4 integration | Pay-per-use |
| [DeepSeek](https://platform.deepseek.com) | Alternative LLM | Competitive pricing |

##  AI Features

### Multi-Model LLM Support
- **Manual Model Selection**: Users choose between Gemma-3, GPT-4, Gemini, DeepSeek
- **RAG Integration**: Document-grounded responses using uploaded repair manuals
- **Semantic Search**: pgvector-powered context retrieval
- **Safety-First**: Built-in safety prompts and guidelines

### Repair Analysis Capabilities
- **Device Recognition**: Automatic device detection from conversations
- **Cost Estimation**: DIY vs professional repair cost analysis
- **Feasibility Assessment**: User skill level vs repair complexity matching
- **Tool Requirements**: Specific tool and parts recommendations
- **Safety Warnings**: Context-aware safety considerations

##  Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       ▼                       │
        │              ┌─────────────────┐               │
        │              │   AI Services   │               │
        └──────────────┤  (Multiple LLMs) │───────────────┘
                       └─────────────────┘
```

### Technology Stack
- **Frontend**: React 18, TailwindCSS, Vite, i18next
- **Backend**: FastAPI, SQLAlchemy, asyncio, Poetry
- **Database**: PostgreSQL 15 + pgvector extension
- **AI Integration**: Google AI, OpenAI, Replicate, DeepSeek APIs
- **Deployment**: Docker, Docker Compose, Nginx
- **Languages**: English, German (i18next)

## 📚 Available Scripts

### Root Level Scripts
```bash
npm run dev          # Start both frontend and backend concurrently
npm run build        # Build frontend for production
npm run test         # Run all tests (frontend + backend)
npm run lint         # Lint all code
npm run docker:up    # Start with Docker
npm run docker:down  # Stop Docker containers
```

### Backend Scripts
```bash
cd backend
poetry run uvicorn api.main:app --reload --app-dir src  # Dev server
poetry run pytest                                        # Run tests
poetry run black .                                       # Format code
poetry run ruff check .                                  # Lint code
```

### Frontend Scripts
```bash
cd frontend
npm run dev          # Development server (Vite)
npm run build        # Production build
npm run preview      # Preview production build
npm run lint         # ESLint checking
```

##  Development Tools

### API Documentation
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (Alternative API docs)

### Database Access
```bash
# Connect to database container
docker exec -it reparatur_database psql -U test -d reparatur

# View tables
\dt

# View vector similarity queries
SELECT * FROM document_chunks ORDER BY embedding <-> '[vector_here]' LIMIT 5;
```

### Monitoring & Debugging
```bash
# View Docker logs
docker compose logs -f backend
docker compose logs -f frontend

# Monitor resource usage
docker stats
```

##  Production Deployment

### Performance Optimizations
- **Docker multi-stage builds** for minimal image sizes
- **Nginx** for efficient static file serving
- **Poetry** for reproducible Python environments
- **pgvector indexing** for fast semantic search
- **Connection pooling** for database efficiency

### Security Features
- **JWT authentication** for secure user sessions
- **Input validation** on frontend and backend
- **CORS configuration** for cross-origin security
- **Environment variable isolation** for secrets
- **Rate limiting** for API protection

##  Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow code standards**: Use provided linting and formatting tools
4. **Add tests**: Ensure new features have appropriate test coverage
5. **Update documentation**: Keep README and docs current
6. **Submit pull request**: Include detailed description of changes

### Code Quality Standards
- **Python**: Black formatting, Ruff linting, type hints
- **JavaScript**: ESLint, Prettier, consistent component structure
- **Commits**: Conventional commit messages
- **Tests**: Maintain >80% coverage for critical paths

##  Project Status

-  **Core Features**: Multi-model AI integration, RAG pipeline
-  **User Interface**: Responsive React frontend with i18n
-  **Backend API**: FastAPI with comprehensive endpoints
-  **Database**: PostgreSQL with vector search capabilities
-  **Deployment**: Docker containerization with scripts
-  **Documentation**: Complete setup and deployment guides

##  Support

For issues, questions, or contributions:
- **Issues**: Open GitHub issues for bugs or feature requests
- **Documentation**: Check the `/docs` folder for detailed guides
- **Code Review**: All pull requests welcome with proper testing

---

