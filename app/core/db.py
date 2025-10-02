from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator

# Import the configured settings object
from app.core.config import settings
from app.models import * # Import all models to ensure Base.metadata.create_all works

# --- Database Setup ---

# Use the DATABASE_URL configured in the settings object
engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)

# Session factory for use in dependencies
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for declarative class definitions (Models)
Base = declarative_base()

# --- Dependency Injection Functions ---

# Dependency to get the database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provides a transactional database session for endpoints."""
    async with AsyncSessionLocal() as session:
        yield session

# Function to initialize database tables
async def init_db():
    """Initializes the database by creating all defined tables."""
    # This block executes commands that require direct connection access (DDL)
    async with engine.begin() as conn:
        print("Initializing database...")
        # Note: Base.metadata automatically includes all imported models
        # await conn.run_sync(Base.metadata.drop_all) # Optional: Uncomment to drop tables first
        await conn.run_sync(Base.metadata.create_all)
        print("Database initialization complete.")
