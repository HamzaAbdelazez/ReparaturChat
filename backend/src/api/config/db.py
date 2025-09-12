from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from api.config.core import settings
from typing import AsyncGenerator
import api.database.table_models 

# ------------------------------------------------------
# Create async PostgreSQL engine
# ------------------------------------------------------
engine = create_async_engine(
    settings.DATABASE_URL,  # Example: postgresql+asyncpg://user:pass@localhost:5432/reparatur
    echo=True,
    future=True,
)

# ------------------------------------------------------
# Create async session factory
# ------------------------------------------------------
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# ------------------------------------------------------
# Base class for all ORM models
# ------------------------------------------------------
Base = declarative_base()

# ------------------------------------------------------
# Async function to initialize DB tables
# ------------------------------------------------------
async def init_db_tables() -> None:
    """
    Create all tables asynchronously at startup.
    """
    import api.database.table_models  # register models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ------------------------------------------------------
# Dependency for FastAPI to get async DB session
# ------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async SQLAlchemy session.
    Automatically closes after the request.
    """
    async with async_session_maker() as session:
        yield session
