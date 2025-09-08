from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from api.config.db import get_db


async def db_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    Async generator dependency that yields a database session.

    This allows FastAPI to handle the database session lifecycle for each request.
    """
    async for db in get_db():
        yield db
