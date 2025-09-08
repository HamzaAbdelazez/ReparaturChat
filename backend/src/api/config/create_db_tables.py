import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from api.database import table_models
from dotenv import load_dotenv
from api.config.core import settings

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_tables():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        logger.info("Creating extensions...")
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))

        logger.info("Creating tables...")
        await conn.run_sync(table_models.Base.metadata.create_all)
        logger.info("Tables created successfully.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())
