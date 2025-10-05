# Reparatur Project - Complete Architecture & Workflow Documentation

## Project Overview

The Reparatur project is a bilingual repair assistance application that combines AI-powered guidance with document-based knowledge retrieval. It helps users with device repairs by providing contextual advice based on uploaded PDF manuals and general repair knowledge.

## Technology Stack

### Frontend
- **Framework**: React 18 with Vite
- **Styling**: TailwindCSS
- **Icons**: Lucide React, MDI Font
- **Routing**: React Router DOM v6
- **Build Tool**: Vite with ESLint

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with pgvector extension
- **ORM**: SQLAlchemy 2.0 with AsyncPG
- **Vector Search**: pgvector for similarity search
- **AI Integration**: Replicate API (Gemma3 model)
- **Document Processing**: PyMuPDF
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)
- **Authentication**: PassLib with bcrypt

## Project Structure

```
Reparatur/
├── Reparatur-app/                    # Frontend React Application
│   ├── src/
│   │   ├── pages/                    # Main application pages
│   │   │   ├── login.jsx            # User authentication
│   │   │   ├── signup.jsx           # User registration
│   │   │   ├── chatbot.jsx          # Original chat interface
│   │   │   └── chatbot-refactored.jsx # Improved chat interface
│   │   ├── components/              # Reusable React components
│   │   │   ├── ChatInterface.jsx    # Basic chat component
│   │   │   ├── ChatInterfaceWithPDF.jsx # Chat with PDF upload
│   │   │   ├── DeviceManager.jsx    # Device management
│   │   │   ├── DeviceSelector.jsx   # Device selection UI
│   │   │   ├── DocumentUpload.jsx   # PDF upload component
│   │   │   ├── RepairAnalysis.jsx   # Repair analysis display
│   │   │   └── ToolAnalysis.jsx     # Tool analysis component
│   │   ├── assets/                  # Static assets and images
│   │   ├── App.jsx                  # Main application component
│   │   └── main.jsx                 # Application entry point
│   ├── public/                      # Public static files
│   ├── package.json                 # Frontend dependencies
│   ├── vite.config.js              # Vite configuration
│   ├── tailwind.config.js          # TailwindCSS configuration
│   └── eslint.config.js            # ESLint configuration
│
├── backend/                         # FastAPI Backend Application
│   ├── src/api/
│   │   ├── main.py                  # FastAPI application entry point
│   │   ├── config/                  # Configuration and database setup
│   │   │   ├── core.py             # Core application settings
│   │   │   ├── db.py               # Database connection and setup
│   │   │   ├── create_db_tables.py # Database table creation
│   │   │   └── create_tables.sql   # SQL table definitions
│   │   ├── database/               # Database layer
│   │   │   ├── table_models.py     # SQLAlchemy table models
│   │   │   └── repository/         # Data access layer
│   │   │       ├── base.py         # Base repository class
│   │   │       ├── user.py         # User data operations
│   │   │       ├── uploaded_pdf.py # PDF document operations
│   │   │       ├── document_chunk.py # Document chunk operations
│   │   │       ├── document_tool.py # Document-tool relationship
│   │   │       └── tool.py         # Tool data operations
│   │   ├── models/                 # Pydantic data models
│   │   │   ├── user.py            # User models
│   │   │   ├── uploaded_pdf.py    # PDF document models
│   │   │   ├── document_chunk.py  # Document chunk models
│   │   │   ├── document_tool.py   # Document-tool models
│   │   │   ├── tool.py            # Tool models
│   │   │   ├── device.py          # Device models
│   │   │   └── repair_analysis.py # Repair analysis models
│   │   ├── routers/               # API endpoint definitions
│   │   │   ├── users.py           # User management endpoints
│   │   │   ├── chat.py            # Chat and conversation endpoints
│   │   │   ├── conversations.py   # Conversation history endpoints
│   │   │   ├── uploaded_pdfs.py   # PDF upload endpoints
│   │   │   ├── document_chunks.py # Document chunk endpoints
│   │   │   ├── tools.py           # Tool management endpoints
│   │   │   ├── document_tools.py  # Document-tool relationship endpoints
│   │   │   ├── devices.py         # Device management endpoints
│   │   │   ├── repair_analysis.py # Repair analysis endpoints
│   │   │   └── tool_pricing.py    # Tool pricing endpoints
│   │   ├── service/               # Business logic layer
│   │   │   ├── rag.py             # RAG implementation and document processing
│   │   │   ├── tools_extractor.py # Tool extraction from documents
│   │   │   ├── uploaded_pdf.py    # PDF processing service
│   │   │   ├── user.py            # User service logic
│   │   │   ├── repair_analysis.py # Repair analysis service
│   │   │   ├── repair_feasibility.py # Repair feasibility analysis
│   │   │   ├── tool_pricing.py    # Tool pricing service
│   │   │   └── tool_reusability.py # Tool reusability analysis
│   │   └── shared/                # Shared utilities
│   │       └── password_helper.py # Password hashing utilities
│   ├── pyproject.toml             # Python dependencies (Poetry)
│   ├── docker-compose.yml         # Docker configuration for database
│   └── Dockerfile                 # Docker container configuration
│
├── run.sh / run.bat / run-mac.sh    # Platform-specific startup scripts
├── DOCUMENTATION.md                 # Additional documentation
├── PROJECT_EXPLANATION.md           # Project explanation
├── QUICKSTART.md                    # Quick start guide
└── README.md                        # Main project README
```

## Core Components and File Purposes

### Frontend Files

#### Pages (`Reparatur-app/src/pages/`)
- **`login.jsx`**: User authentication interface with form validation
- **`signup.jsx`**: User registration with password confirmation
- **`chatbot.jsx`**: Original chat interface implementation
- **`chatbot-refactored.jsx`**: Enhanced chat interface with improved UX

#### Components (`Reparatur-app/src/components/`)
- **`ChatInterface.jsx`**: Core chat functionality and message handling
- **`ChatInterfaceWithPDF.jsx`**: Chat interface integrated with PDF upload
- **`DeviceManager.jsx`**: Device selection and management interface
- **`DeviceSelector.jsx`**: UI component for device selection
- **`DocumentUpload.jsx`**: PDF file upload with validation
- **`RepairAnalysis.jsx`**: Display repair analysis results
- **`ToolAnalysis.jsx`**: Show tool recommendations and analysis

### Backend Files

#### Core Application (`backend/src/api/`)
- **`main.py`**: FastAPI application setup, CORS configuration, router registration

#### Configuration (`backend/src/api/config/`)
- **`core.py`**: Application settings and environment configuration
- **`db.py`**: Database connection setup and session management
- **`create_db_tables.py`**: Database initialization and table creation
- **`create_tables.sql`**: SQL schema definitions

#### Database Layer (`backend/src/api/database/`)
- **`table_models.py`**: SQLAlchemy ORM models for all database tables
- **Repository Pattern**: Individual repository classes for each entity
  - **`base.py`**: Base repository with common CRUD operations
  - **`user.py`**: User-specific database operations
  - **`uploaded_pdf.py`**: PDF document database operations
  - **`document_chunk.py`**: Document chunk storage and retrieval
  - **`document_tool.py`**: Many-to-many relationship management
  - **`tool.py`**: Tool database operations

#### API Models (`backend/src/api/models/`)
- **Pydantic Models**: Request/response validation and serialization
  - Data validation and type safety
  - API documentation generation
  - Request/response schema definitions

#### API Routers (`backend/src/api/routers/`)
- **`users.py`**: User registration, authentication, profile management
- **`chat.py`**: Chat endpoints with user expertise level adaptation
- **`conversations.py`**: Conversation history and management
- **`uploaded_pdfs.py`**: PDF upload, processing, and management
- **`document_chunks.py`**: Document chunk retrieval and search
- **`tools.py`**: Tool management and recommendations
- **`document_tools.py`**: Document-tool relationship management
- **`devices.py`**: Device catalog and management
- **`repair_analysis.py`**: Repair analysis and feasibility
- **`tool_pricing.py`**: Tool pricing and cost analysis

#### Business Logic (`backend/src/api/service/`)
- **`rag.py`**: Core RAG implementation
  - Document embedding generation
  - Vector similarity search
  - Context-aware response generation
  - Integration with Replicate/Gemma3
- **`tools_extractor.py`**: Tool extraction from PDF documents
- **`uploaded_pdf.py`**: PDF processing and text extraction
- **`user.py`**: User management business logic
- **`repair_analysis.py`**: Repair feasibility analysis
- **`repair_feasibility.py`**: Detailed repair assessment
- **`tool_pricing.py`**: Tool cost calculation
- **`tool_reusability.py`**: Tool reusability analysis

## Application Workflow

### 1. User Registration and Authentication
```
1. User accesses signup.jsx
2. Frontend sends registration data to /users/register
3. Backend validates data and hashes password
4. User record created in PostgreSQL
5. User can login via login.jsx
6. JWT token or session management (if implemented)
```

### 2. Document Upload and Processing
```
1. User uploads PDF via DocumentUpload.jsx
2. Frontend sends file to /uploaded_pdfs/upload
3. Backend processes PDF with PyMuPDF
4. Text extracted and chunked into segments
5. Each chunk converted to vector embeddings using SentenceTransformers
6. Chunks and embeddings stored in PostgreSQL with pgvector
7. Tools extracted from document using tools_extractor.py
8. Document-tool relationships established
```

### 3. Chat Interaction and RAG Process
```
1. User enters query in ChatInterface components
2. Query sent to /chat/ask endpoint with user expertise level
3. Backend RAG process (rag.py):
   a. Convert user query to vector embedding
   b. Perform similarity search against stored document chunks
   c. Retrieve most relevant chunks as context
   d. Construct prompt with:
      - User expertise level prefix
      - Retrieved context
      - User query
   e. Send to Replicate API (Gemma3 model)
   f. Process and return AI response
4. Response displayed in chat interface
5. Conversation stored for history
```

### 4. Device and Tool Management
```
1. User selects device via DeviceSelector.jsx
2. Device information stored and associated with user session
3. Tool recommendations generated based on:
   - Selected device
   - Uploaded documents
   - Repair requirements
4. Tool analysis displayed via ToolAnalysis.jsx
5. Pricing and availability information provided
```

### 5. Repair Analysis Workflow
```
1. User requests repair analysis
2. System analyzes:
   - Device specifications
   - Available tools
   - User expertise level
   - Document context
3. Generates repair feasibility assessment
4. Provides step-by-step guidance
5. Results displayed via RepairAnalysis.jsx
```

## Data Flow Architecture

### Frontend to Backend Communication
```
React Components → API Calls → FastAPI Routers → Services → Database/External APIs
```

### RAG Data Flow
```
PDF Upload → Text Extraction → Chunking → Embedding Generation → Vector Storage
User Query → Query Embedding → Similarity Search → Context Retrieval → AI Response
```

### Database Schema Flow
```
Users ←→ UploadedPDFs ←→ DocumentChunks
                    ↓
              DocumentTools ←→ Tools
                    ↓
               Devices ←→ RepairAnalysis
```

## Key Features

### 1. Multilingual Support
- Interface supports multiple languages
- AI responses adapt to user language preferences

### 2. User Expertise Adaptation
- 5-level expertise system (beginner to expert)
- Response complexity adjusted based on user level
- Technical terminology adapted accordingly

### 3. Vector-based Document Search
- Semantic search using embeddings
- Context-aware information retrieval
- Relevance-based chunk selection

### 4. Tool Integration
- Automatic tool extraction from manuals
- Tool-document relationship mapping
- Pricing and availability analysis

### 5. Repair Analysis
- Feasibility assessment
- Step-by-step guidance
- Tool requirements analysis

## Development and Deployment

### Local Development Setup
```bash
# Frontend
cd Reparatur-app
npm install
npm run dev  # http://localhost:5173

# Backend
cd backend
poetry install
poetry run uvicorn api.main:app --reload --app-dir src  # http://127.0.0.1:8000

# Database
docker compose up  # PostgreSQL with pgvector
```

### API Documentation
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Testing
- Backend: `poetry run pytest`
- Application: `python test_application.py`

## External Dependencies

### AI Services
- **Replicate API**: Gemma3 model for text generation
- **SentenceTransformers**: Local embedding generation

### Database Extensions
- **pgvector**: PostgreSQL extension for vector operations

### Key Libraries
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Python ORM
- **React**: Frontend framework
- **TailwindCSS**: Utility-first CSS framework
- **PyMuPDF**: PDF processing
- **PassLib**: Password hashing

## Security Considerations

### Authentication
- Password hashing with bcrypt
- Secure session management
- CORS configuration for cross-origin requests

### Data Protection
- Input validation with Pydantic models
- SQL injection prevention via ORM
- File upload validation and sanitization

This architecture provides a scalable, maintainable foundation for the repair assistance application with clear separation of concerns and modern development practices.