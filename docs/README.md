# ReparaturApp - Intelligent Repair Assistant

A bilingual repair assistance application that combines React frontend with FastAPI backend, using RAG (Retrieval-Augmented Generation) to provide intelligent repair guidance based on uploaded PDF manuals.

## 🚀 Quick Start

### Windows
```cmd
# Double-click or run in Command Prompt
run.bat
```

### Linux/Unix
```bash
chmod +x run.sh
./run.sh
```

### macOS
```bash
chmod +x run-mac.sh
./run-mac.sh
```

## 📋 Prerequisites

- **Python 3.10+** (with pip)
- **Node.js 16+** (with npm)
- **Docker Desktop** (for PostgreSQL)
- **Git** (for version control)

### Optional but Recommended
- **Poetry** (Python dependency management)
- **PostgreSQL client** (for database inspection)

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│  (React + Vite) │◄──►│ (FastAPI)       │◄──►│ (PostgreSQL +   │
│                 │    │                 │    │  pgvector)      │
│ • PDF Upload    │    │ • RAG Pipeline  │    │ • User Data     │
│ • Chat UI       │    │ • AI Integration│    │ • PDF Content   │
│ • Conversations │    │ • Tool Analysis │    │ • Vector Store  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  External APIs  │
                       │ • Gemma-3 (AI)  │
                       │ • Replicate API │
                       └─────────────────┘
```

## 🔧 Technology Stack

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **TailwindCSS** - Styling
- **Lucide React** - Icons

### Backend
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **AsyncIO** - Async operations

### Database
- **PostgreSQL** - Main database
- **pgvector** - Vector similarity search
- **Alembic** - Database migrations

### AI & Processing
- **SentenceTransformers** - Text embeddings
- **PyMuPDF** - PDF text extraction
- **Replicate API** - gemma-3 model access
- **Vector Search** - Semantic document search

## 📁 Project Structure

```
ReparaturApp/
├── 📁 frontend/          # Frontend React application
│   ├── 📁 src/
│   │   ├── 📁 components/      # React components
│   │   ├── 📁 pages/          # Page components
│   │   └── 📄 main.jsx        # App entry point
│   ├── 📄 package.json        # Node.js dependencies
│   └── 📄 vite.config.js      # Vite configuration
├── 📁 backend/                # Backend FastAPI application
│   ├── 📁 src/api/
│   │   ├── 📁 config/         # Configuration
│   │   ├── 📁 database/       # Database models & setup
│   │   ├── 📁 models/         # Pydantic models
│   │   ├── 📁 routers/        # API endpoints
│   │   ├── 📁 service/        # Business logic
│   │   └── 📄 main.py         # FastAPI app entry
│   ├── 📄 pyproject.toml      # Python dependencies
│   ├── 📄 docker-compose.yml  # Database setup
│   └── 📄 .env                # Environment variables
├── 📄 README.md               # This file
├── 📄 DOCUMENTATION.md        # Detailed technical docs
├── 📄 run.bat                 # Windows startup script
├── 📄 run.sh                  # Linux/Unix startup script
└── 📄 run-mac.sh              # macOS startup script
```

## 🔄 Workflow Overview

### 1. User Registration & Login
```mermaid
graph TD
    A[User visits app] --> B{Registered?}
    B -->|No| C[Sign up form]
    B -->|Yes| D[Login form]
    C --> E[Create account]
    D --> E
    E --> F[Dashboard]
```

### 2. PDF Upload & Processing
```mermaid
graph TD
    A[Select PDF file] --> B[Upload to backend]
    B --> C[Extract text with PyMuPDF]
    C --> D[Split into chunks]
    D --> E[Generate embeddings]
    E --> F[Store in PostgreSQL]
    F --> G[Extract tools with regex]
    G --> H[Save tools to database]
    H --> I[Ready for chat]
```

### 3. Chat & RAG Pipeline
```mermaid
graph TD
    A[User asks question] --> B[Generate query embedding]
    B --> C[Vector similarity search]
    C --> D[Retrieve relevant chunks]
    D --> E[Build context prompt]
    E --> F[Send to gemma-3 AI]
    F --> G[Generate response]
    G --> H[Save conversation]
    H --> I[Display to user]
```

## 🗃️ Database Schema

### Core Tables
- **users** - User accounts and profiles
- **uploaded_pdfs** - PDF files and metadata  
- **document_chunks** - Text chunks with embeddings
- **conversations** - Chat sessions
- **messages** - Individual chat messages
- **tools** - Repair tools database
- **chat_messages** - Legacy message storage

### Relationships
```sql
users (1) ───→ (M) uploaded_pdfs
users (1) ───→ (M) conversations
conversations (1) ───→ (M) messages
uploaded_pdfs (1) ───→ (M) document_chunks
tools (M) ←───→ (M) uploaded_pdfs (via document_tools)
```

## 🔐 Environment Variables

Create `backend/.env` file:
```env
# Database
POSTGRES_USER=test
POSTGRES_PASSWORD=password
POSTGRES_DB=reparatur
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://test:password@localhost:5432/reparatur

# AI Services
REPLICATE_API_TOKEN=your_replicate_token_here
```

## 🧪 Development Setup

### Manual Setup

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd ReparaturApp
   ```

2. **Start database**
   ```bash
   cd backend
   docker compose up -d
   ```

3. **Backend setup**
   ```bash
   # With Poetry (recommended)
   poetry install
   poetry run uvicorn api.main:app --reload --app-dir src
   
   # Or with pip
   pip install -r requirements.txt
   python -c "import sys; sys.path.append('src'); import uvicorn; uvicorn.run('api.main:app', host='127.0.0.1', port=8000, reload=True)"
   ```

4. **Frontend setup**
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

## 📊 API Documentation

Once running, visit:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Key Endpoints
- `POST /uploadedPdfs/` - Upload PDF files
- `GET /chat/pdf` - Chat about uploaded PDFs
- `GET /chat/general` - General repair questions
- `GET /conversations/` - List user conversations
- `GET /documents/{id}/tools` - Get extracted tools

## 🐳 Docker Deployment

Full Docker setup:
```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: password
      POSTGRES_DB: reparatur
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql+asyncpg://test:password@db:5432/reparatur

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

## 🚨 Troubleshooting

### Common Issues

1. **Import errors**: Make sure `__init__.py` files exist in all Python packages
2. **Database connection**: Ensure PostgreSQL is running via Docker
3. **API token**: Set `REPLICATE_API_TOKEN` in `.env` file
4. **Port conflicts**: Check ports 5432 (DB), 8000 (API), 5173 (Frontend)
5. **Dependencies**: Run install commands for both frontend and backend

### Log Locations
- **Backend logs**: Console output from uvicorn
- **Frontend logs**: Browser developer tools
- **Database logs**: `docker compose logs db`

## 📈 Performance Tips

1. **Database indexing**: Ensure proper indexes on vector columns
2. **Connection pooling**: Configure SQLAlchemy pool settings
3. **Chunking strategy**: Optimize text chunk size for your use case
4. **Caching**: Implement Redis for API response caching
5. **CDN**: Use CDN for static assets in production

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👨‍💻 Authors

- **Your Name** - Initial work

## 🙏 Acknowledgments

- OpenAI for ChatGPT-style interface inspiration
- Google DeepMind for Gemma-3 models
- PostgreSQL team for pgvector extension
- FastAPI and React communities