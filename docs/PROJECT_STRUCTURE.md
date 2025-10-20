# 🔧 Repair Platform - Project Structure

## 📁 Main Project Structure
```
Reparatur/
├── 📁 backend/                 # Python FastAPI backend
├── 📁 frontend/                # React frontend  
├── 📄 run.bat                  # Windows startup script
├── 📄 run.sh                   # Linux/Mac startup script
├── 📄 PROJECT_STRUCTURE.md     # This file
└── 📄 README.md                # Project documentation
```

---

## 🐍 Backend Structure (`backend/`)

```
backend/
├── 📁 src/api/                 # Main application code
│   ├── 📁 config/              # Database & app configuration
│   │   ├── 📄 core.py          # App settings (env variables)
│   │   ├── 📄 db.py            # Database connection
│   │   └── 📄 create_tables.sql # Database schema
│   │
│   ├── 📁 database/            # Database layer
│   │   ├── 📄 table_models.py  # Database tables (User, Tool, etc.)
│   │   └── 📁 repository/      # Data access objects
│   │       ├── 📄 user.py      # User database operations
│   │       ├── 📄 tool.py      # Tool database operations
│   │       └── 📄 ...          # Other repositories
│   │
│   ├── 📁 models/              # API response models
│   │   ├── 📄 user.py          # User API models
│   │   ├── 📄 tool.py          # Tool API models
│   │   ├── 📄 repair_analysis.py # Repair analysis models
│   │   └── 📄 ...              # Other API models
│   │
│   ├── 📁 routers/             # API endpoints
│   │   ├── 📄 users.py         # User management endpoints
│   │   ├── 📄 uploaded_pdfs.py # PDF upload endpoints
│   │   ├── 📄 chat.py          # Chat endpoints
│   │   ├── 📄 tools.py         # Tool management endpoints
│   │   ├── 📄 intelligent_analysis.py # Smart repair analysis
│   │   ├── 📄 service_providers.py # Professional services
│   │   └── 📄 ...              # Other endpoints
│   │
│   ├── 📁 service/             # Business logic
│   │   ├── 📄 intelligent_repair_analysis.py # Smart analysis logic
│   │   ├── 📄 tool_pricing.py  # Real-time tool pricing
│   │   ├── 📄 chat_based_analysis.py # Problem analysis from chat
│   │   ├── 📄 rag.py           # PDF search & AI responses
│   │   ├── 📄 user.py          # User business logic
│   │   └── 📄 ...              # Other services
│   │
│   ├── 📁 shared/              # Utility functions
│   │   └── 📄 password_helper.py # Password hashing
│   │
│   └── 📄 main.py              # FastAPI app entry point
│
├── 📄 docker-compose.yml       # PostgreSQL database container
├── 📄 pyproject.toml           # Python dependencies
├── 📄 populate_tool_prices.py  # Script to update tool prices
└── 📄 .env                     # Environment variables
```

---

## ⚛️ Frontend Structure (`frontend/`)

```
frontend/
├── 📁 src/
│   ├── 📁 components/          # React components
│   │   ├── 📄 MainContent.jsx  # Main page layout
│   │   ├── 📄 DocumentUpload.jsx # PDF upload component
│   │   ├── 📄 RepairAnalysis.jsx # Repair recommendations
│   │   ├── 📄 ChatInterface.jsx # Chat with AI
│   │   ├── 📄 DeviceSelector.jsx # Device selection
│   │   ├── 📄 ToolAnalysis.jsx # Tool pricing display
│   │   └── 📄 ...              # Other components
│   │
│   ├── 📁 hooks/               # Custom React hooks
│   │   ├── 📄 useAuth.js       # User authentication
│   │   ├── 📄 useChat.js       # Chat functionality
│   │   ├── 📄 usePdfUpload.js  # PDF upload handling
│   │   └── 📄 ...              # Other hooks
│   │
│   ├── 📁 i18n/                # Multi-language support
│   │   ├── 📄 index.js         # Language configuration
│   │   └── 📁 locales/         # Translation files
│   │       ├── 📄 en.json      # English translations
│   │       └── 📄 de.json      # German translations
│   │
│   ├── 📁 pages/               # Main page components
│   │   ├── 📄 login.jsx        # Login page
│   │   ├── 📄 signup.jsx       # Registration page
│   │   └── 📄 chatbot.jsx      # Main application page
│   │
│   ├── 📁 services/            # API calls
│   ├── 📁 utils/               # Utility functions
│   ├── 📄 App.jsx              # Main app component
│   └── 📄 main.jsx             # React app entry point
│
├── 📄 package.json             # JavaScript dependencies
├── 📄 vite.config.js           # Vite bundler configuration
├── 📄 tailwind.config.js       # TailwindCSS styling
└── 📄 index.html               # HTML template
```

---

## 🗄️ Database Tables

**Main Tables:**
- `users` - User accounts with skill levels (1-5 scale)
- `uploaded_pdfs` - Repair manual documents
- `document_chunks` - PDF content with AI embeddings
- `tools` - Required tools with pricing data
- `tool_prices` - Real-time prices from Amazon, eBay, OBI
- `service_providers` - Professional repair services
- `conversations` - Chat sessions
- `messages` - Chat messages for context analysis
- `devices` - User devices for repair
- `document_tools` - Links tools to repair manuals

---

## 🚀 Key Features

**Backend Features:**
- User skill assessment (1-5 scale for skill, experience, strength, space)
- Real-time tool pricing from German websites
- Intelligent repair analysis based on user profile and chat context
- PDF text extraction and AI-powered search
- Professional service provider database
- Multi-language support (German/English)

**Frontend Features:**
- PDF upload with automatic tool extraction
- Real-time chat with AI about repair problems
- Personalized repair recommendations
- Cost and time estimates based on user skills
- Tool pricing comparison across vendors
- Device management and warranty checking

---

## 🔧 Technology Stack

**Backend:**
- **FastAPI** - Python web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Database with vector support
- **pgvector** - Vector embeddings for AI search
- **aiohttp** - Web scraping for tool prices
- **Replicate API** - AI language models
- **Docker** - Database containerization

**Frontend:**
- **React** - JavaScript UI framework
- **Vite** - Fast build tool
- **TailwindCSS** - Utility-first CSS
- **i18next** - Internationalization
- **Lucide React** - Icon library

**AI/ML:**
- **Sentence Transformers** - Text embeddings
- **RAG (Retrieval-Augmented Generation)** - AI-powered PDF search
- **Natural Language Processing** - Problem recognition from chat

---

## 📋 How It Works

1. **User Registration** - Users create accounts and assess their repair skills (1-5 scale)

2. **PDF Upload** - Users upload repair manuals
   - System extracts text and required tools
   - Automatically fetches real-time tool prices from websites
   - Stores content with AI embeddings for search

3. **Chat Interface** - Users describe their repair problems
   - AI analyzes the problem type and complexity
   - System considers user skill level and device type
   - Generates personalized recommendations

4. **Intelligent Analysis** - System provides:
   - Repair feasibility based on user skills
   - Cost estimates with real tool prices
   - Time estimates adjusted for user experience
   - Comparison with professional service costs
   - Personalized warnings and next steps

5. **Professional Services** - If self-repair isn't recommended:
   - Shows local professional repair services
   - Compares costs and time estimates
   - Provides contact information and specialties

This structure enables users to get personalized, context-aware repair advice based on their actual skill level and specific problems.