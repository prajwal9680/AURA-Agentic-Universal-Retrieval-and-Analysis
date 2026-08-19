"""
AURA — Database Connection & Engine Management
Dual-engine architecture:
- Production: PostgreSQL + pgvector with HNSW vector indexing & connection pooling
- Local/Offline Fallback: SQLite + aiosqlite with local Vector adapter
"""
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.config import DB_PATH, settings

logger = logging.getLogger(__name__)

# Determine active database URL
_raw_url = settings.database_url.strip() if settings.database_url else ""
if _raw_url.startswith("postgres://"):
    # Normalize legacy postgres:// to asyncpg
    DATABASE_URL = _raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif _raw_url.startswith("postgresql://"):
    DATABASE_URL = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif _raw_url:
    DATABASE_URL = _raw_url
else:
    DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

IS_POSTGRES = DATABASE_URL.startswith("postgresql")

# Create async engine with production connection pooling for Postgres
if IS_POSTGRES:
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.debug,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_pre_ping=True,
    )
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.debug,
        connect_args={"check_same_thread": False},
    )

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    """FastAPI dependency for scoped database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all tables on startup and initialize pgvector if PostgreSQL is active."""
    from app import models  # noqa: F401 — registers models
    async with engine.begin() as conn:
        if IS_POSTGRES:
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                logger.info("PostgreSQL pgvector extension verified.")
            except Exception as e:
                logger.warning(f"Could not initialize pgvector extension: {e}")
        await conn.run_sync(Base.metadata.create_all)
        logger.info(f"Database initialized successfully ({'PostgreSQL+pgvector' if IS_POSTGRES else 'SQLite'}).")

