# Reparatur Platform

An AI-powered repair analysis platform that provides cost estimation, feasibility assessment, and tool recommendations for device repairs.

## 🏗️ Project Structure

```
reparatur-platform/
├── backend/                    # FastAPI backend service
│   ├── src/
│   │   └── api/
│   │       ├── config/        # Configuration and database setup
│   │       ├── database/      # Database models and repositories
│   │       ├── models/        # Pydantic models
│   │       ├── routers/       # API endpoints
│   │       ├── service/       # Business logic
│   │       └── shared/        # Shared utilities
│   ├── tests/                 # Backend tests
│   ├── Dockerfile
│   ├── pyproject.toml         # Python dependencies
│   └── README.md
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── pages/            # Page components
│   │   ├── services/         # API services
│   │   └── utils/            # Utility functions
│   ├── public/               # Static assets
│   ├── package.json          # Node.js dependencies
│   └── README.md
├── docs/                      # Project documentation
├── docker-compose.yml         # Full-stack Docker setup
├── package.json              # Root package.json for scripts
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** (≥18.0.0)
- **Python** (≥3.11)
- **Poetry** (for Python dependency management)
- **Docker** (optional, for containerized deployment)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd reparatur-platform
   ```

2. **Install dependencies**
   ```bash
   npm run setup
   ```

3. **Start the development servers**
   ```bash
   npm run dev
   ```

   This will start:
   - Backend API at `http://localhost:8000`
   - Frontend at `http://localhost:5173`

### Docker Setup (Alternative)

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down
```

## 🛠️ Development

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start both frontend and backend in development mode |
| `npm run dev:frontend` | Start only the frontend |
| `npm run dev:backend` | Start only the backend |
| `npm run build` | Build the frontend for production |
| `npm run test` | Run tests for both frontend and backend |
| `npm run lint` | Lint both frontend and backend code |
| `npm run docker:up` | Start services with Docker |
| `npm run setup` | Install all dependencies |

### Backend Development

```bash
cd backend
poetry install                    # Install dependencies
poetry run uvicorn api.main:app --app-dir src --reload  # Start dev server
poetry run pytest                 # Run tests
poetry run ruff check .           # Lint code
```

### Frontend Development

```bash
cd frontend
npm install                       # Install dependencies
npm run dev                       # Start dev server
npm run build                     # Build for production
npm run lint                      # Lint code
```

## 🗄️ Database

The platform uses PostgreSQL with pgvector extension for vector storage and similarity search.

### Database Setup

1. **Using Docker (Recommended)**
   ```bash
   docker-compose up database
   ```

2. **Manual Setup**
   - Install PostgreSQL with pgvector extension
   - Create database: `reparatur`
   - Update connection details in `backend/.env`

### Environment Variables

Create `backend/.env`:
```env
# Database Configuration
POSTGRES_USER=test
POSTGRES_PASSWORD=password
POSTGRES_DB=reparatur
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# API Tokens
HUGGINGFACE_HUB_TOKEN=your_token_here
GEMINI_API_KEY=your_key_here
REPLICATE_API_TOKEN=your_token_here
```

## 🔧 Features

- **AI-Powered Analysis**: Leverages multiple LLM models for repair analysis
- **Cost Estimation**: Provides detailed cost breakdowns for repairs
- **Tool Recommendations**: Suggests appropriate tools and parts
- **Multi-language Support**: Available in English and German
- **Document Upload**: PDF upload and processing for repair manuals
- **Conversation History**: Track and manage repair analysis sessions

## 🏛️ Architecture

- **Frontend**: React 18 with Vite, TailwindCSS, and React Router
- **Backend**: FastAPI with async support, SQLAlchemy ORM
- **Database**: PostgreSQL with pgvector for semantic search
- **AI Integration**: Hugging Face, Google Gemini, Replicate APIs
- **Containerization**: Docker and Docker Compose

## 📚 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [Frontend README](./frontend/README.md)
- [Backend README](./backend/README.md)
- [Documentation](./docs/)