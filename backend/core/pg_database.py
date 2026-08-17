"""
PostgreSQL / Supabase Database Manager
======================================
Asynchronous database connection pool and session manager using SQLAlchemy.
Supports PostgreSQL (Supabase/Neon/Local) and SQLite fallback.
"""
import os
import logging
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
try:
    from models.db_models import Base
except ImportError:
    from backend.models.db_models import Base

logger = logging.getLogger(__name__)

# Fetch database URL from environment variable
# Supabase URI format: postgresql+asyncpg://postgres.[ref]:[pass]@[host]:5432/postgres
RAW_DB_URL = os.getenv("DATABASE_URL", "").strip()

# Adjust dialect if standard postgresql:// is passed
if RAW_DB_URL.startswith("postgresql://"):
    ASYNC_DB_URL = RAW_DB_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif RAW_DB_URL.startswith("postgres://"):
    ASYNC_DB_URL = RAW_DB_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif RAW_DB_URL:
    ASYNC_DB_URL = RAW_DB_URL
else:
    # Default fallback to async SQLite for zero-config offline mode
    ASYNC_DB_URL = "sqlite+aiosqlite:///access_navigator.db"

# Create async engine with connection pooling
engine = None
AsyncSessionLocal = None

try:
    engine_kwargs = {
        "echo": False,
        "future": True,
    }
    if "postgresql" in ASYNC_DB_URL:
        engine_kwargs["pool_pre_ping"] = True
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20

    engine = create_async_engine(ASYNC_DB_URL, **engine_kwargs)
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    logger.info(f"Database engine initialized for: {ASYNC_DB_URL.split('@')[-1] if '@' in ASYNC_DB_URL else ASYNC_DB_URL}")
except Exception as e:
    logger.warning(f"Could not initialize database engine: {e}")


async def init_db():
    """Create all tables in the database if they don't already exist."""
    if engine is None:
        return
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.warning(f"Database table initialization notice: {e}")


async def get_db() -> AsyncGenerator[Optional[AsyncSession], None]:
    """Dependency for obtaining an async database session in FastAPI endpoints."""
    if AsyncSessionLocal is None:
        yield None
        return
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
