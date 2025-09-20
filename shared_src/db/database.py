"""
shared_src/db/database.py

Database connection and session management for the AI Excel Interviewer.
- Defines async SQLAlchemy engine and sessionmaker for PostgreSQL.
- Provides helper functions for initializing the database and yielding sessions.
"""
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict 
from .models import Base

class DbSettings(BaseSettings):
    """Loads database configuration from environment variables."""
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = DbSettings()

DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    """Create all database tables defined in models."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Database tables created.")

async def get_db():
    """Async generator yielding a database session for dependency injection."""
    async with AsyncSessionLocal() as session:
        yield session