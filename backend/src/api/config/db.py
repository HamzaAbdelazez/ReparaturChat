from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from api.config.core import settings

# ------------------------------------------------------
# Create sync PostgreSQL engine
# ------------------------------------------------------
engine = create_engine(
    settings.DATABASE_URL.replace("+asyncpg", ""),  # ensure sync driver
    echo=False,  # Disabled for better performance
    future=True,
    pool_size=10,          # Connection pool for better performance
    max_overflow=20,       # Additional connections if needed
    pool_pre_ping=True,    # Validate connections
    pool_recycle=3600      # Refresh connections hourly
)

# ------------------------------------------------------
# Session factory
# ------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ------------------------------------------------------
# Base
# ------------------------------------------------------
Base = declarative_base()

# ------------------------------------------------------
# Init DB tables (sync)
# ------------------------------------------------------
def init_db_tables() -> None:
    """
    Create all tables synchronously at startup.
    """
    import api.database.table_models  # register models
    Base.metadata.create_all(bind=engine)

# ------------------------------------------------------
# Dependency for FastAPI (sync session)
# ------------------------------------------------------
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
