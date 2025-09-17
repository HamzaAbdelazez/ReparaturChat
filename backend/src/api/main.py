import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from api.routers import users, uploaded_pdfs, chat , tools , document_chunks , document_tools 
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
# Create FastAPI application
# ------------------------------------------------------
app = FastAPI(title="Reparatur API")

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

# ------------------------------------------------------
# Startup event: initialize database tables asynchronously
# ------------------------------------------------------
@app.on_event("startup")
async def on_startup():
    logger.info("Initializing database tables")
    await init_db_tables()   # Async database initialization
    logger.info("Database tables initialized successfully")
