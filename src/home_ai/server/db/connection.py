"""Database connection management."""

from sqlalchemy import create_engine as sa_create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from home_ai.common.config import get_settings


def get_database_url() -> str:
    """Get database URL from settings.
    
    Returns:
        PostgreSQL database URL.
    """
    settings = get_settings()
    return settings.database_url


def create_engine(database_url: str | None = None):
    """Create SQLAlchemy engine.
    
    Args:
        database_url: Database URL. If None, uses settings.
        
    Returns:
        SQLAlchemy engine.
    """
    if database_url is None:
        database_url = get_database_url()
    
    return sa_create_engine(database_url)


def create_async_engine_instance(database_url: str | None = None):
    """Create async SQLAlchemy engine.
    
    Args:
        database_url: Database URL. If None, uses settings.
        
    Returns:
        Async SQLAlchemy engine.
    """
    if database_url is None:
        database_url = get_database_url()
    
    # Convert postgresql:// to postgresql+asyncpg://
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    return create_async_engine(database_url)


def get_session_factory(engine=None):
    """Get session factory.
    
    Args:
        engine: SQLAlchemy engine. If None, creates one from settings.
        
    Returns:
        Session factory.
    """
    if engine is None:
        engine = create_engine()
    
    return sessionmaker(bind=engine)


def get_async_session_factory(engine=None):
    """Get async session factory.
    
    Args:
        engine: Async SQLAlchemy engine. If None, creates one from settings.
        
    Returns:
        Async session factory.
    """
    if engine is None:
        engine = create_async_engine_instance()
    
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

