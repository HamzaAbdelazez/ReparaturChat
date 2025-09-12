from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from api.config.core import settings

# Create engine
engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

# Async session factory
async_session_maker = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)

# Dependency for FastAPI routes
async def db_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    Async generator dependency that yields a database session.
    """
    async with async_session_maker() as session:
        yield session
