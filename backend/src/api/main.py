import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from api.routers import users, uploaded_pdfs, chat ,tools , document_chunks , document_tools , documents, devices, repair_analysis, tool_pricing, conversations, document_tools_simple, service_providers, llm_status, user_preferences
from api.config.db import init_db_tables






# ------------------------------------------------------
# Configure logging for the application
# ------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[ %(levelname)s ] %(asctime)s %(name)s %(message)s"
)
logger = logging.getLogger("api.main")

# ------------------------------------------------------
# Lifespan context manager for startup/shutdown events
# ------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database tables")
    init_db_tables()
    yield
    # Shutdown (if needed)
    logger.info("Application shutdown")

# ------------------------------------------------------
# Create FastAPI application
# ------------------------------------------------------
app = FastAPI(title="Reparatur API", lifespan=lifespan)

# ------------------------------------------------------
# Enable CORS (Cross-Origin Resource Sharing)
# ------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------
# Register routers (API endpoints)
# ------------------------------------------------------
app.include_router(users.router)
app.include_router(uploaded_pdfs.router)
app.include_router(chat.router)
app.include_router(document_chunks.router)
app.include_router(tools.router)
app.include_router(document_tools.router)
app.include_router(document_tools_simple.router)  # Add simple endpoint for frontend compatibility
app.include_router(documents.router)
app.include_router(devices.router)
app.include_router(repair_analysis.router)
app.include_router(tool_pricing.router)
app.include_router(conversations.router)
app.include_router(service_providers.router)
app.include_router(llm_status.router)
app.include_router(user_preferences.router)


