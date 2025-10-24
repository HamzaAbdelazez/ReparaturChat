# Code Structure Guide

A comprehensive guide to understanding the codebase organization, file purposes, and development patterns in the ReparaturApp project.

##  Project Overview

The ReparaturApp is structured as a full-stack application with clear separation of concerns:

```
Reparatur/
├──  frontend/          # React frontend application
├──   backend/           # FastAPI backend service
├──  scripts/           # Deployment and setup automation
├──  docs/              # Documentation and guides
├──  docker-compose.yml # Container orchestration
└──  configuration files
```

##  Frontend Structure (`/frontend`)

### Core Application Files

| File | Purpose | Key Features |
|------|---------|--------------|
| `src/main.jsx` | Application entry point | React 18 setup, providers initialization |
| `src/App.jsx` | Root component | Routing, authentication checks, global layout |
| `src/App.css` | Global styles | Base styles, utility classes |
| `index.html` | HTML template | Meta tags, favicon, root element |

### Page Components (`/frontend/src/pages`)

| File | Purpose | Features |
|------|---------|----------|
| `chatbot.jsx` | Main application interface | Chat interface, document upload, repair analysis |
| `login.jsx` | User authentication | JWT token-based login form |
| `signup.jsx` | User registration | Account creation with validation |

**Key patterns:**
- Each page is a complete feature module
- Uses custom hooks for state management
- Integrates multiple components for complex workflows

### Component Library (`/frontend/src/components`)

#### Core UI Components
| Component | Purpose | Props/Features |
|-----------|---------|----------------|
| `ChatInterface.jsx` | Main chat component | Message display, input handling, model selection |
| `LLMModelSelector.jsx` | AI model selection | Dropdown for Gemma-3, GPT-4, Gemini, DeepSeek |
| `DocumentUpload.jsx` | PDF file upload | Drag-and-drop, progress tracking, validation |
| `RepairAnalysis.jsx` | Analysis results display | Cost breakdown, feasibility assessment |
| `Sidebar.jsx` | Navigation and conversations | Chat history, new conversation creation |
| `MainContent.jsx` | Central content area | Layout orchestration, state management |

#### Utility Components
| Component | Purpose | Features |
|-----------|---------|----------|
| `MarkdownRenderer.jsx` | Formatted text display | Renders AI responses with proper formatting |
| `ConfirmationModal.jsx` | User confirmations | Reusable dialog for destructive actions |
| `LanguageSwitcher.jsx` | Internationalization | German/English language toggle |
| `ProtectedRoute.jsx` | Authentication guard | Route protection for authenticated users |

#### Specialized Components
| Component | Purpose | Features |
|-----------|---------|----------|
| `DeviceManager.jsx` | Device CRUD operations | Add, edit, delete user devices |
| `DeviceSelector.jsx` | Device selection UI | Dropdown with user's registered devices |
| `ToolAnalysis.jsx` | Tool recommendations | Tool requirements and cost analysis |
| `ToolsPartsToggle.jsx` | Analysis mode switch | Toggle between tools and parts analysis |

### Custom Hooks (`/frontend/src/hooks`)

| Hook | Purpose | State Management |
|------|---------|------------------|
| `useAuth.js` | Authentication logic | User state, login/logout, token management |
| `useChat.js` | Chat functionality | Message history, sending messages, model selection |
| `useConversations.js` | Conversation management | Chat history, switching conversations, persistence |
| `useDevices.js` | Device management | User devices, selection state, CRUD operations |
| `usePdfUpload.js` | Document handling | File upload, processing status, document management |

**Hook patterns:**
- Return state and actions as objects
- Handle API calls with error handling
- Provide loading states for UI feedback
- Use React Query patterns for caching

### Services & Utilities (`/frontend/src`)

#### API Services (`/frontend/src/services`)
- Centralized API client configurations
- Axios instances with authentication headers
- Request/response interceptors for error handling

#### Utility Functions (`/frontend/src/utils`)
| File | Purpose |
|------|---------|
| `repairAnalysis.js` | Analysis data processing and formatting |
| `stateCleanup.js` | State management utilities for cleanup operations |

#### Internationalization (`/frontend/src/i18n`)
| File | Purpose |
|------|---------|
| `index.js` | i18next configuration and setup |
| `locales/en.json` | English translations |
| `locales/de.json` | German translations |

### Configuration Files

| File | Purpose | Configuration |
|------|---------|---------------|
| `package.json` | Dependencies and scripts | React 18, Vite, TailwindCSS, testing tools |
| `vite.config.js` | Build configuration | Development server, build optimization, proxy settings |
| `tailwind.config.js` | CSS framework setup | Custom colors, responsive breakpoints, component classes |
| `eslint.config.js` | Code quality rules | Linting rules for consistent code style |
| `postcss.config.js` | CSS processing | TailwindCSS integration and optimization |

### Docker Configuration
| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage build: Node.js build → Nginx serve |
| `nginx.conf` | Nginx configuration for serving React SPA |
| `.dockerignore` | Build context optimization |

##  Backend Structure (`/backend`)

### Application Core (`/backend/src/api`)

#### Configuration (`/backend/src/api/config`)
| File | Purpose | Features |
|------|---------|----------|
| `core.py` | Application settings | Environment variables, CORS setup, logging |
| `db.py` | Database configuration | SQLAlchemy setup, connection pooling, session management |
| `create_db_tables.py` | Database initialization | Table creation, initial data seeding |
| `create_tables.sql` | SQL schema definitions | Table structures, indexes, constraints |

#### Database Layer (`/backend/src/api/database`)

**Models (`table_models.py`)**
- SQLAlchemy ORM models for all database tables
- Relationships between entities
- Index definitions for performance

**Repositories (`/backend/src/api/database/repository`)**
| File | Purpose | Operations |
|------|---------|-------------|
| `base.py` | Abstract base repository | CRUD operations, common queries |
| `user.py` | User data access | Authentication, profile management |
| `document_chunk.py` | Document content storage | Vector embeddings, similarity search |
| `uploaded_pdf.py` | Document metadata | File information, processing status |
| `tool.py` | Tool and parts data | Equipment database, pricing information |
| `document_tool.py` | Document-tool relationships | Tool extraction from manuals |
| `service_provider.py` | External service configuration | AI model provider settings |

**Database Utilities**
| File | Purpose |
|------|---------|
| `init.sql` | Database initialization script |
| `__init__.py` | Package initialization and exports |

#### Data Models (`/backend/src/api/models`)

Pydantic models for API serialization/validation:

| File | Purpose | Features |
|------|---------|----------|
| `user.py` | User data schemas | Registration, login, profile models |
| `document_chunk.py` | Document content models | Text chunks, embeddings, metadata |
| `uploaded_pdf.py` | File upload models | Document information, processing status |
| `device.py` | Device information models | Manufacturer, model, category data |
| `tool.py` | Tool and parts models | Equipment specifications, pricing |
| `repair_analysis.py` | Analysis result models | Cost estimation, feasibility assessment |
| `document_tool.py` | Tool extraction models | Document-tool relationship data |
| `service_provider.py` | AI service models | Provider configuration and status |

#### API Routes (`/backend/src/api/routers`)

**Core Routes**
| File | Purpose | Endpoints |
|------|---------|-----------|
| `users.py` | User management | `/users/register`, `/users/login`, `/users/profile` |
| `chat.py` | Chat functionality | `/chat/ask`, `/chat/history` |
| `conversations.py` | Conversation management | `/conversations/`, `/conversations/{id}` |
| `documents.py` | Document handling | `/documents/upload`, `/documents/{id}` |
| `uploaded_pdfs.py` | PDF management | Upload, processing, retrieval |

**Specialized Routes**
| File | Purpose | Endpoints |
|------|---------|-----------|
| `repair_analysis.py` | Analysis endpoints | `/repair-analysis/feasibility`, `/repair-analysis/cost-estimation` |
| `document_chunks.py` | Document content | Chunk retrieval, similarity search |
| `tools.py` | Tool database | Tool information, recommendations |
| `devices.py` | Device management | User device CRUD operations |
| `tool_pricing.py` | Cost analysis | Tool and parts pricing |

**Support Routes**
| File | Purpose | Features |
|------|---------|----------|
| `llm_status.py` | AI service monitoring | Model availability, health checks |
| `dependencies.py` | Route dependencies | Authentication, database sessions |
| `setup.py` | Application setup | Initialization endpoints |

#### Business Logic (`/backend/src/api/service`)

**AI Integration Services**
| File | Purpose | Features |
|------|---------|----------|
| `llm_service.py` | LLM orchestration | Multi-model support (Gemma-3, GPT-4, Gemini, DeepSeek) |
| `rag.py` | RAG implementation | Document retrieval, context assembly, embedding generation |
| `chat_based_analysis.py` | Conversation analysis | Device detection, problem classification |

**Analysis Services**
| File | Purpose | Features |
|------|---------|----------|
| `repair_analysis.py` | Comprehensive analysis | Feasibility, cost, time estimation |
| `repair_feasibility.py` | Repair assessment | Skill matching, safety evaluation |
| `tool_pricing.py` | Cost calculation | Tool and parts pricing, comparison analysis |
| `device_extractor.py` | Device recognition | Extract device info from text/documents |
| `tools_extractor.py` | Tool identification | Extract tool requirements from manuals |

**Content Processing**
| File | Purpose | Features |
|------|---------|----------|
| `uploaded_pdf.py` | Document processing | PDF parsing, text extraction, chunking |
| `tools_parts_service.py` | Tool/parts management | Database operations, recommendations |
| `tool_reusability.py` | Tool optimization | Reusability analysis, cost optimization |

**User Services**
| File | Purpose | Features |
|------|---------|----------|
| `user.py` | User operations | Profile management, preferences |

#### Shared Utilities (`/backend/src/api/shared`)
| File | Purpose | Features |
|------|---------|----------|
| `password_helper.py` | Security utilities | Password hashing, verification with bcrypt |

#### Scripts (`/backend/src/api/scripts`)
| File | Purpose |
|------|---------|
| `seed_service_providers.py` | Database seeding script for AI service providers |

### Testing (`/backend/tests`)
- Unit tests for services and repositories
- Integration tests for API endpoints
- Test fixtures and utilities

### Configuration Files

| File | Purpose | Configuration |
|------|---------|---------------|
| `pyproject.toml` | Poetry configuration | Dependencies, build settings, tool configurations |
| `requirements.txt` | Pip fallback | Simplified dependency list for Docker |
| `Dockerfile` | Multi-stage container | Poetry build → Production runtime |
| `Dockerfile.simple` | Simplified container | Pip-based installation |
| `docker-compose.yml` | Database container | PostgreSQL with pgvector for development |

##  Scripts & Automation (`/scripts`)

### Installation Scripts
| File | Purpose | Features |
|------|---------|----------|
| `install.sh` | Linux/macOS setup | Dependency detection, automated installation |
| `install.bat` | Windows setup | Cross-platform equivalent with error handling |

### Runtime Scripts
| File | Purpose | Features |
|------|---------|----------|
| `run.sh` | Linux/macOS startup | Docker orchestration, health checks |
| `run.bat` | Windows startup | Full-stack application launcher |

**Script Features:**
- Command-line argument parsing (`--rebuild`, `--parallel`)
- Dependency validation (Docker, Python, Node.js)
- Health checks and status reporting
- Graceful error handling and cleanup

##  Documentation (`/docs`)

| File | Purpose | Content |
|------|---------|---------|
| `DEPLOYMENT_GUIDE.md` | Complete setup guide | Installation, configuration, troubleshooting |
| `CODE_STRUCTURE.md` | This file | Codebase organization and architecture |
| `2.3_Web_Application_Technologies.md` | Technical documentation | Academic paper sections |

##  Container Configuration

### Docker Compose Files
| File | Purpose | Services |
|------|---------|----------|
| `docker-compose.yml` | Full-stack deployment | Database + Backend + Frontend |
| `backend/docker-compose.yml` | Backend development | Database only |

### Environment Configuration
| File | Purpose | Variables |
|------|---------|-----------|
| `.env.example` | Environment template | Database credentials, API keys |
| `.env` | Local configuration | Actual secrets (git-ignored) |

##  Root Configuration

| File | Purpose | Configuration |
|------|---------|---------------|
| `package.json` | Root scripts | Concurrency management, cross-platform scripts |
| `package-lock.json` | Dependency lock | Exact version specifications |

##  Development Workflow

### Typical Development Flow

1. **Backend Development**
   ```bash
   cd backend
   docker compose up          # Start database
   poetry run uvicorn api.main:app --reload --app-dir src
   ```

2. **Frontend Development**
   ```bash
   cd frontend
   npm run dev               # Start Vite dev server
   ```

3. **Full Stack Testing**
   ```bash
   ./scripts/run.sh          # Start everything with Docker
   ```

### Code Organization Principles

1. **Separation of Concerns**
   - Frontend: UI logic and user interactions
   - Backend: Business logic and data processing
   - Database: Data persistence and relationships

2. **Layered Architecture**
   - **Presentation Layer**: React components and pages
   - **API Layer**: FastAPI routers and endpoints
   - **Service Layer**: Business logic and AI integration
   - **Data Layer**: Repositories and database models

3. **Dependency Flow**
   - Frontend → Backend API → Service Layer → Database
   - No circular dependencies
   - Clear interfaces between layers

4. **Configuration Management**
   - Environment-specific settings
   - Secret management through environment variables
   - Containerized deployment configurations

## 🔍 Key Patterns and Conventions

### Frontend Patterns
- **Component Composition**: Smaller, reusable components
- **Custom Hooks**: Business logic extraction from components
- **State Management**: Local state + API state with custom hooks
- **Error Boundaries**: Graceful error handling

### Backend Patterns
- **Repository Pattern**: Data access abstraction
- **Service Layer**: Business logic separation
- **Dependency Injection**: Automatic dependency resolution
- **Async/Await**: Non-blocking operations throughout

### API Design
- **RESTful Resources**: Standard HTTP methods and status codes
- **Request/Response Models**: Pydantic validation
- **Error Handling**: Consistent error response format
- **Documentation**: Automatic OpenAPI generation

##  Important Notes

### Security Considerations
- Never commit API keys or passwords
- Use environment variables for all secrets
- Validate all user inputs
- Implement proper authentication and authorization

### Performance Optimization
- Database indexing for frequently queried fields
- Async operations for I/O-bound tasks
- Connection pooling for database efficiency
- Docker layer caching for faster builds

### Maintenance Guidelines
- Follow established naming conventions
- Write tests for new features
- Update documentation with changes
- Use linting and formatting tools consistently

---

This structure provides a scalable foundation for the AI-powered repair platform, with clear separation of concerns and well-defined interfaces between components.