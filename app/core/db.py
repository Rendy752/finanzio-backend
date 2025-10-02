from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

# Import the configured settings object
from app.core.config import settings
from app.core.base import Base 

# --- Database Setup ---

# Use the DATABASE_URL configured in the settings object
engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)

# Session factory for use in dependencies
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# --- Dependency Injection Functions ---

# Dependency to get the database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provides a transactional database session for endpoints."""
    async with AsyncSessionLocal() as session:
        yield session

# Function to initialize database tables
async def init_db():
    """Initializes the database by creating all defined tables."""
        
    async with engine.begin() as conn:
        print("Initializing database...")
        # Note: Base.metadata automatically includes all imported models
        # await conn.run_sync(Base.metadata.drop_all) # Optional: Uncomment to drop tables first
        await conn.run_sync(Base.metadata.create_all)
        print("Database initialization complete.")
